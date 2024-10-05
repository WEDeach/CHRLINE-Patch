import struct
import threading
import time
from typing import Any, Callable

from ..client import CHRLINE
from ..services import *
from .connData import LegyH2PushFrame, LegyPushOABot, LegyPushOABotTyping


def gen_m(ss=[1, 3, 5, 6, 8, 9, 10]):
    i = 0
    for s in ss:
        i |= 1 << (s - 1)
    return i


class ConnManager(object):
    def __init__(self, line_client: CHRLINE):
        self.line_client = line_client
        self.conns = []
        self.hook_callback = None
        self.curr_ping_id = 0
        self.subscriptionIds = {}
        self.SignOnRequests = {}
        self.OnPingCallback = self._OnPingCallback
        self.OnSignReqResp = {}
        self.OnSignOnResponse = self._OnSignOnResponse
        self.OnPushResponse = self._OnPushResponse
        self.logger = self.line_client.get_logger("PUSH")

        self._eventSynced = False
        self._revisionSynced = False
        self._pingInterval = 30
        self._access_token = None

    @property
    def accessToken(self):
        return self._access_token

    @accessToken.setter
    def accessToken(self, newToken):
        self._access_token = newToken

    def log(self, text: str, debug: bool = False):
        if debug:
            return self.logger.debug(text)
        return self.logger.info(text)

    def initializeConn(self, state: int = 1, initServices: list = [3, 5]):
        """Create new conn and return it."""
        from .conn import Conn

        _conn = Conn(self)
        if state == 1:
            self.conns.append(_conn)
            self.accessToken = self.line_client.authToken
        tosend_headers = {
            "x-line-application": self.line_client.server.Headers["x-line-application"],
            "x-line-access": self.accessToken,
        }
        m = gen_m(initServices)
        self.log(f"Using `m={m}` on `/PUSH`")
        _conn.new("gw.line.naver.jp", 443, f"/PUSH/1/subs?m={m}", tosend_headers)
        return _conn

    def InitAndRead(self, initServices: list = [3, 5]):
        """Init conn state and read data."""
        if not self.conns:
            raise ValueError("No valid connections found.")
        cl = self.line_client
        _conn = self.conns[0]
        FLAG = 0
        _conn.wirteRequest(0, bytes([0, FLAG, self._pingInterval]))
        self.log(f"send status frame. flag:{FLAG}, pi:{self._pingInterval}")
        for service in initServices:
            self.log(f"Init service: {service}")
            ex_val = {}
            if service == 3:
                subscriptionId = int(time.time() * 1000)
                syncToken = ""
                if self.line_client.eventSyncToken is not None:
                    syncToken = str(self.line_client.eventSyncToken)
                ex_val = {
                    "subscriptionId": subscriptionId,
                    "syncToken": syncToken,
                }
                self.log(
                    f"request fetchMyEvent({subscriptionId}), syncToken:{syncToken}"
                )
                self.subscriptionIds = {}  # clear
            elif service in [5, 8]:
                ex_val = {
                    "revision": self.line_client.revision,
                    "count": 100,
                    "globalRev": cl.globalRev,
                    "individualRev": cl.individualRev,
                    "fullSyncRequestReason": None,
                    "lastPartialFullSyncs": None,
                }
                self.log(f"request talk fetcher: {ex_val}")
            self.buildAndSendSignOnRequest(_conn, service, **ex_val)
        self.log("CONN start read push.")
        _conn.read()
        self.logger.warning(f"CONN died on PingId={self.curr_ping_id}")
        self.conns.remove(_conn)

    def SendAndReadSignOnRequest(
        self, serviceType, waitAndReadResp: bool = False, **kwargs
    ):
        """Test send request and read response."""
        if not self.conns:
            raise ValueError("No valid connections found.")
        _conn = None
        conns = []
        for c in self.conns[1:]:
            if c.IsAble2Request():
                conns.append(c)
        if len(conns) < 1:
            pusher = ConnManager(self.line_client)
            pusher.initializeConn()
            # use thread for send pings
            _td = threading.Thread(target=pusher.InitAndRead, args=([],))
            _td.daemon = True
            _td.start()
            _conn = pusher.conns[0]
            self.conns.append(_conn)
        else:
            for c in conns:
                if not c._closed:
                    _conn = c
                    break
        if _conn is None:
            raise NotImplementedError
        _, reqId = self.buildAndSendSignOnRequest(_conn, serviceType, **kwargs)
        if waitAndReadResp:
            raise NotImplementedError()

            def Callback(self, reqId, data):
                self.OnSignReqResp[reqId] = data

            self.SignOnRequests[reqId][2] = Callback
            return self.OnSignReqResp[reqId]

    def buildRequest(self, service, data):
        """Build request struct."""
        return struct.pack("!H", len(data)) + bytes([service]) + data

    def buildAndSendSignOnRequest(self, conn: Any, serviceType: int, **kwargs):
        """
        Build and send sign-on-request.

        ServiceType:
            - 3: fetchMyEvents
            - 5: fecthOps / sync
            - 9: fetchLiveTalkEvents
            - 10: - (for OABotPush)
        """
        cl = self.line_client
        _id = len(self.SignOnRequests) + 1
        _payload = struct.pack("!H", _id)
        _req = None
        serviceName = None
        methodName = None
        if serviceType in [0, 1, 2, 4, 7]:
            #
            _req = b""
        elif serviceType == 3:
            # Square
            serviceName = "Square"
            methodName = "fetchMyEvents"
            _req = self.buildFetchMyEventsRequest(**kwargs)
        elif serviceType in [5, 8]:
            # Talk
            serviceName = "Talk"
            methodName = "fetchOps"
            if cl.DEVICE_TYPE in cl.SYNC_SUPPORT:
                methodName = "sync"
                _req = self.buildServiceRequest(serviceName, methodName, **kwargs)
            else:
                _req = self.buildFetchOpsRequest(**kwargs)
        elif serviceType == 6:
            #
            _req = b""
        elif serviceType == 8:
            # Talk
            _req = b""
        elif serviceType == 9:
            # LiveTalk
            _req = b""
        elif serviceType == 10:
            # OABot
            _req = b""
        elif serviceType == "sendMessage":
            raise NotImplementedError
            methodName = "sendMessage"
            serviceType = 5
            _req = self.buildSendMessageRequest(**kwargs)
        else:
            raise ValueError(f"unknow serviceType: {serviceType}")
        _payload += bytes([serviceType, 0])
        _payload += struct.pack("!H", len(_req))
        _payload += _req
        self.SignOnRequests[_id] = [serviceType, methodName, None]
        self.line_client.log(
            f"[H2][PUSH] send sign-on-request. requestId:{_id}, service:{serviceType}",
            True,
        )
        conn.wirteRequest(2, _payload)
        return _payload, _id

    def buildFetchMyEventsRequest(self, subscriptionId, syncToken):
        """Build request for fetchMyEvents."""
        cl = self.line_client
        params = [
            [
                12,
                1,
                [
                    [10, 1, subscriptionId],
                    [11, 2, syncToken],
                    [8, 3, 100],
                ],
            ]
        ]
        return bytes(cl.generateDummyProtocol("fetchMyEvents", params, 4))

    def buildFetchOpsRequest(self, revision: int = -1, **kargs):
        """Build request for fetchOps."""
        cl = self.line_client
        if revision == -1:
            revision = cl.revision
        params = [
            [10, 2, revision],
            [8, 3, 200],  # use 200.
            [10, 4, cl.globalRev],
            [10, 5, cl.individualRev],
        ]
        return bytes(cl.generateDummyProtocol("fetchOps", params, 4))

    def buildServiceRequest(self, serviceName: str, methodName: str, **kargs):
        """Build request for service."""
        cl = self.line_client
        service = f"{serviceName}Service"
        serviceStruct = f"{service}.{service}Struct"
        methodRequest = methodName.title() + "Request"
        unitCalled = f"{serviceStruct}.{methodRequest}"
        ins = eval(f"{unitCalled}")
        payload = ins(**kargs)
        data = cl.generateDummyProtocol(methodName, payload, 4)
        return bytes(data)

    def _OnSignOnResponse(self, reqId, isFin, data):
        if reqId in self.SignOnRequests:
            serviceType = self.SignOnRequests[reqId][0]
            methodName = self.SignOnRequests[reqId][1]
            callback = self.SignOnRequests[reqId][2]
            serviceName = "TalkService"
            cl = self.line_client
            self.log(
                f"receives sign-on-response frame. requestId:{reqId}, service:{serviceType}, isFin:{isFin}, payload:{data[:20].hex()}",
                True,
            )
            if serviceType == 3:
                data = cl.TCompactProtocol(cl, data)
                resp = data.res
                if isinstance(resp, dict) and "error" in resp:
                    self.log(f"can't use PUSH for OpenChat:{resp['error']}")
                    return False
                subscription = cl.checkAndGetValue(resp, "subscription", 1)
                events = cl.checkAndGetValue(resp, "events", 2)
                syncToken = cl.checkAndGetValue(resp, "syncToken", 3)
                subscriptionId = cl.checkAndGetValue(subscription, "subscriptionId", 1)
                if not isinstance(events, list):
                    raise ValueError(f"events should be list: {events}")
                if syncToken is not None and not isinstance(syncToken, str):
                    raise ValueError(f"syncToken should be str: {syncToken}")
                self.log(
                    f"response fetchMyEvent({subscriptionId}) events:{len(events)}, syncToken:{syncToken}"
                )
                if subscriptionId is not None and not isinstance(subscriptionId, int):
                    raise ValueError(f"subscriptionId should be int: {subscriptionId}")
                cl.subscriptionId = subscriptionId
                if subscriptionId is not None:
                    self.subscriptionIds[subscriptionId] = time.time()
                if not self._eventSynced:
                    cl.setEventSyncToken(syncToken)
                    self.log(
                        f"myEvents start({subscriptionId}) : syncToken:{cl.eventSyncToken}"
                    )
            elif serviceType in [5, 8]:
                _conn = self.conns[0]
                try:
                    data = cl.TMoreCompactProtocol(cl, data)
                    resp = data.res
                    if methodName == "sync":
                        serviceName = "SyncService"
                    resp = cl.serializeDummyProtocolToThrift(
                        data.dummyProtocol, readWith=f"{serviceName}.{methodName}"
                    )
                    if methodName == "sync":
                        ops = resp
                        sht, shd = cl.talk_handler.SyncHandler(resp)
                        ex_val = {
                            "revision": cl.globalRev,
                            "count": 100,
                            "globalRev": cl.globalRev,
                            "individualRev": cl.individualRev,
                            "fullSyncRequestReason": None,
                            "lastPartialFullSyncs": None,
                        }
                        if sht == 1:
                            ops = shd
                            if not isinstance(ops, list):
                                raise ValueError(f"ops should be list: {ops}")
                            self.log(
                                f"response sync. operations:{len(ops)}",
                                True,
                            )
                            for op in ops:
                                if isinstance(self.hook_callback, Callable):
                                    self.hook_callback(cl, serviceType, op)
                                revision = cl.checkAndGetValue(op, "revision", 1)
                                cl.setRevision(revision)
                        elif sht == 2:
                            cl.setRevision(shd)
                        else:
                            raise RuntimeError
                        ex_val["revision"] = cl.revision
                        self.buildAndSendSignOnRequest(_conn, serviceType, **ex_val)
                        return
                    elif methodName == "fetchOps":
                        ops = resp
                        if not isinstance(ops, list):
                            raise ValueError(f"ops should be list: {ops}")
                        self.log(
                            f"response fetchOps. operations:{len(ops)}",
                            True,
                        )
                        for op in ops:
                            opType = cl.checkAndGetValue(op, "type", 3)
                            param1 = cl.checkAndGetValue(op, "param1", 10)
                            param2 = cl.checkAndGetValue(op, "param2", 11)
                            if opType == 0:
                                if param1 is not None:
                                    cl.individualRev = param1.split("\x1e")[0]
                                    self.log(f"individualRev: {cl.individualRev}", True)
                                if param2 is not None:
                                    cl.globalRev = param2.split("\x1e")[0]
                                    self.log(f"globalRev: {cl.globalRev}", True)
                            cl.setRevision(cl.checkAndGetValue(op, "revision", 1))
                            if isinstance(self.hook_callback, Callable):
                                self.hook_callback(cl, serviceType, op)
                        # LOOP
                        fetch_req_data = {"revision": cl.revision}
                        self.buildAndSendSignOnRequest(
                            _conn, serviceType, **fetch_req_data
                        )
                    else:
                        # TODO:
                        # Callback resp to ReqId
                        if callback is not None:
                            callback(self, reqId, resp)
                except Exception as e:
                    raise Exception(f"[PUSH] response {methodName} error: {e}")
            else:
                raise ValueError(
                    f"[PUSH] receives invalid sign-on-response frame. requestId:{reqId}, service:{serviceType}"
                )

    def _OnPushResponse(self, pushFrame: LegyH2PushFrame):
        cl = self.line_client
        tcp = cl.TCompactProtocol(cl, passProtocol=True)
        if pushFrame.service_type == 3:
            tcp.data = pushFrame.push_payload
            d: Any = tcp.x(False)
            subscriptionId = d[1]
            if cl.subscriptionId != subscriptionId:
                self.log(
                    f"subscriptionId not sync: {cl.subscriptionId} -> {subscriptionId},",
                )
                cl.subscriptionId = subscriptionId
            for event in self.line_client._Poll__fetchMyEvents():  # type: ignore
                _type = cl.checkAndGetValue(event, "type", 3)
                self.log(
                    f"subscriptionId:{subscriptionId}, eventType:{_type}",
                    True,
                )
                if isinstance(self.hook_callback, Callable):
                    self.hook_callback(self.line_client, pushFrame.service_type, event)
        elif pushFrame.service_type == 10:
            if pushFrame.push_payload:
                poa = LegyPushOABot.unwrap(pushFrame.push_payload)
                if isinstance(poa, LegyPushOABotTyping):
                    if isinstance(self.hook_callback, Callable):
                        self.hook_callback(
                            self.line_client, pushFrame.service_type, poa
                        )
                else:
                    self.log(f"Unknown OaBotPushMessage Type: {poa._type}")
        else:
            raise NotImplementedError(f"Not support type: {pushFrame.service_type}")

    def _OnPingCallback(self, pingId):
        cl = self.line_client
        self.curr_ping_id = pingId

        # check subscriptionIds need refresh.
        # LOG:
        #   - 221227: change use ts.
        refreshIds = []
        t1 = time.time()
        for subscriptionId in self.subscriptionIds.keys():
            t2 = self.subscriptionIds[subscriptionId]
            if (t1 - t2) >= 3000:
                self.subscriptionIds[subscriptionId] = time.time()
                refreshIds.append(subscriptionId)
        if refreshIds:
            self.log(f"refresh subscriptionId: {refreshIds}")
            cl.refreshSquareSubscriptions(refreshIds)

        # when using the PUSH endpoint, you may not be able to update the AuthToken properly.
        # because you can't get the `x-line-next-access` header on the socket connection.
        # here use http protocol to check.
        if pingId % 3 == 0:
            cl.noop()
            oldToken = self.accessToken
            newToken = self.line_client.authToken
            if oldToken != newToken:
                self.log("renew push conn for new authToken...")
                self.accessToken = newToken
                self.conns[0].close()
