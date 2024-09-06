import socket
import ssl
import struct
import time

import h2.connection
from h2.config import H2Configuration
from h2.events import DataReceived, StreamEnded, StreamReset

from .connData import (
    LegyH2PingFrame,
    LegyH2PingFrameType,
    LegyH2PushFrame,
    LegyH2PushFrameType,
    LegyH2SignOnResponseFrame,
)
from .connManager import ConnManager


class Conn(object):
    def __init__(self, manager: ConnManager):
        self.manager = manager
        self.conn = None
        self.writer = None
        self.h2_headers = []
        self.is_not_finished = False
        self.cache_data = b""
        self.notFinPayloads = {}

        self._last_send_time = 0
        self._closed = False

    @property
    def client(self):
        return self.manager.line_client

    def new(self, host, port, path, headers: dict = {}):
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(["h2"])
        s = socket.create_connection((host, port))
        self.writer = ctx.wrap_socket(s, server_hostname=host)
        config = H2Configuration(client_side=True)
        self.conn = h2.connection.H2Connection(config=config)
        self.h2_headers = [
            (":method", "POST"),
            (":authority", host),
            (":scheme", "https"),
            (":path", path),
        ]
        for h in headers.keys():
            self.h2_headers.append((h, headers[h]))
        self.conn.initiate_connection()
        self.conn.send_headers(1, self.h2_headers)
        self.send()

    def send(self):
        if self.conn and self.writer:
            send_data = self.conn.data_to_send()
            if send_data:
                self.client.log(f"[H2][PUSH] send data: {send_data.hex()}", True)
                self._last_send_time = time.time()
            self.writer.sendall(send_data)
        else:
            raise RuntimeError

    def writeByte(self, data: bytes):
        if self.conn:
            self.conn.send_data(stream_id=1, data=data, end_stream=False)
            self.send()
        else:
            raise RuntimeError

    def wirteRequest(self, requestType: int, data: bytes):
        d = self.manager.buildRequest(requestType, data)
        self.writeByte(d)

    def read(self):
        if self.conn and self.writer:
            try:
                response_stream_ended = self._closed
                self.send()
                while not response_stream_ended and self.client.is_login:
                    data = self.writer.recv(65536 * 1024)
                    if not data:
                        break
                    events = self.conn.receive_data(data)
                    for event in events:
                        if isinstance(event, DataReceived):
                            # update flow control so the server doesn't starve us
                            self.conn.acknowledge_received_data(
                                event.flow_controlled_length, event.stream_id
                            )

                            _data = event.data
                            if _data is not None and len(_data) < 4:
                                self.client.log(f"[CONN] Invalid Packet: {_data.hex()}")
                                continue
                            self.onDataReceived(_data)
                        elif isinstance(event, StreamEnded):
                            # response body completed, let's exit the loop
                            response_stream_ended = True
                            break
                        elif isinstance(event, StreamReset):
                            raise RuntimeError("Stream reset: %d" % event.error_code)
                    # send any pending data to the server
                    self.send()
                self.conn.close_connection()
                self.send()
            except Exception as e:
                self.client.log(f"[CONN] task disconnect: {e}")
                if isinstance(e, OSError):
                    pass
                else:
                    raise e
            self._closed = True
            # close the socket
            self.writer.close()
        else:
            raise RuntimeError

    def IsAble2Request(self):
        if self.client.is_login and not self._closed:
            if time.time() - self._last_send_time > 0.5:
                return True
        return False

    def readPacketHeader(self, data):
        (_dl,) = struct.unpack("!H", data[:2])
        _dt = data[2]
        _dd = data[3:]
        return _dt, _dd, _dl

    def onDataReceived(self, data):
        # long data received
        if self.is_not_finished:
            data = self.cache_data + data

        # more response body data received
        self.client.log(f"[H2][PUSH] receives packet. raw:{data.hex()}", True)
        _dt, _dd, _dl = self.readPacketHeader(data)
        if _dl > len(_dd):
            self.is_not_finished = True
            self.cache_data = data
            return
        else:
            self.is_not_finished = False
            if len(_dd) > _dl:
                self.onPacketReceived(_dt, _dd[:_dl])
                data = _dd[_dl:]
                self.client.log(f"[PUSH] extra data {data.hex()[:50]}...", True)
                return self.onDataReceived(data)
        self.onPacketReceived(_dt, _dd)

    def onPacketReceived(self, _dt, _dd):
        debug_only = True
        if _dt == 1:
            _pingType = _dd[0]
            (_pingId,) = struct.unpack("!H", _dd[1:3])
            packet = LegyH2PingFrame(_pingType, _pingId)
            self.client.log(
                f"[PUSH] receives ping frame. pingId:{packet.ping_id}", debug_only
            )

            if packet.ping_type == LegyH2PingFrameType.ACK_REQUIRED:
                self.writeByte(packet.ack_packet())
                self.client.log(f"[PUSH] send ping ack. pingId:{_pingId}", debug_only)
                self.manager.OnPingCallback(_pingId)
            else:
                raise NotImplementedError(f"ping type not Implemented: {_pingType}")
        elif _dt == 3:
            (req,) = struct.unpack("!H", _dd[0:2])
            _requestId = req & 32767
            # Android using 32768, CHRLINE use (32768 / 2)
            _isFin = (req & 32768) != 0
            _responsePayload = _dd[2:]
            packet = LegyH2SignOnResponseFrame(_requestId, _isFin, _responsePayload)
            if packet.is_fin:
                if packet.request_id in self.notFinPayloads:
                    _responsePayload = (
                        self.notFinPayloads[_requestId] + _responsePayload
                    )
                    del self.notFinPayloads[_requestId]
                self.manager.OnSignOnResponse(_requestId, _isFin, _responsePayload)
            else:
                self.client.log(
                    f"[PUSH] receives long data. requestId: {_requestId}, req={req}",
                    debug_only,
                )
                if packet.request_id not in self.notFinPayloads:
                    self.notFinPayloads[packet.request_id] = b""
                self.notFinPayloads[packet.request_id] += packet.response_payload
        elif _dt == 4:
            _pushType = _dd[0]
            _serviceType = _dd[1]
            (_pushId,) = struct.unpack("!i", _dd[2:6])
            _pushPayload = _dd[6:]
            packet = LegyH2PushFrame(_pushType, _serviceType, _pushId, _pushPayload)
            self.client.log(
                f"[PUSH] receives push frame. service:{packet.service_type}", debug_only
            )
            if packet.push_type in [
                LegyH2PushFrameType.NONE,
                LegyH2PushFrameType.ACK_REQUIRED,
            ]:
                if packet.push_type == LegyH2PushFrameType.ACK_REQUIRED:
                    # SEND ACK FOR PUSHES
                    self.writeByte(packet.ack_packet())
                    self.client.log(
                        f"[PUSH] send push ack. service:{_serviceType}", debug_only
                    )

                # Callback
                self.manager.OnPushResponse(packet)
            else:
                raise NotImplementedError(f"push type not Implemented: {_pushType}")
        else:
            raise NotImplementedError(
                f"PUSH not Implemented: type:{_dt}, payloads:{_dd[:30]}, len:{len(_dd)}"
            )

    def close(self):
        """Close conn."""
        self._closed = True
        # write close packet
        if self.conn and self.writer:
            self.conn.close_connection()
            self.send()
            # close the socket
            self.writer.shutdown(socket.SHUT_RDWR)
            self.writer.close()
