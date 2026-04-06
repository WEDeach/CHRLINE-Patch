import struct


class ProtobufSerializer:
    @staticmethod
    def serialize(ttype, field_id, data):
        payload = b""
        if ttype == 2:
            payload += __class__.pack_bool(field_id, data)
        elif ttype == 3:
            payload += __class__.pack_byte(field_id, data)
        elif ttype == 4:
            payload += __class__.pack_float(field_id, data)
        elif ttype == 8:
            payload += __class__.pack_int32(field_id, data)
        elif ttype == 10:
            payload += __class__.pack_int64(field_id, data)
        elif ttype == 11:
            payload += __class__.pack_string(field_id, data)
        elif ttype == 12:
            payload += __class__.pack_struct(field_id, data)
        elif ttype == 13:
            payload += __class__.pack_map(field_id, data)
        elif ttype in (14, 15):
            payload += __class__.pack_list(field_id, data)
        return payload

    @staticmethod
    def deserialize(data: bytes) -> dict:
        result = __class__._decode_raw(data)
        if result is None:
            raise ValueError("Invalid protobuf data")
        return result

    @staticmethod
    def _decode_raw(data: bytes):
        result = {}
        pos = 0
        while pos < len(data):
            field_key, n = __class__.unpack_varint(data, pos)
            pos += n
            field_id = field_key >> 3
            wire_type = field_key & 0x07
            if field_id == 0:
                return None
            if wire_type == 0:
                val, n = __class__.unpack_varint(data, pos)
                pos += n
                result[field_id] = val
            elif wire_type == 1:
                if pos + 8 > len(data):
                    return None
                result[field_id] = struct.unpack_from("<d", data, pos)[0]
                pos += 8
            elif wire_type == 2:
                length, n = __class__.unpack_varint(data, pos)
                pos += n
                if pos + length > len(data):
                    return None
                raw = data[pos : pos + length]
                pos += length
                result[field_id] = __class__._decode_wire2(raw)
            elif wire_type == 5:
                if pos + 4 > len(data):
                    return None
                result[field_id] = struct.unpack_from("<f", data, pos)[0]
                pos += 4
            else:
                return None
        if pos != len(data):
            return None
        return result

    @staticmethod
    def _decode_wire2(raw: bytes):
        if len(raw) > 0:
            nested = __class__._decode_raw(raw)
            if nested is not None:
                return nested
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw

    @staticmethod
    def pack_varint(value):
        result = bytearray()
        value = value & 0xFFFFFFFFFFFFFFFF
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)

    @staticmethod
    def unpack_varint(data: bytes, pos: int = 0):
        result = 0
        shift = 0
        n = 0
        while True:
            b = data[pos + n]
            result |= (b & 0x7F) << shift
            n += 1
            if not (b & 0x80):
                break
            shift += 7
        return result, n

    @staticmethod
    def pack_bool(field_id, value):
        field_key = (field_id << 3) | 0
        return __class__.pack_varint(field_key) + __class__.pack_varint(
            1 if value else 0
        )

    @staticmethod
    def pack_byte(field_id, value):
        field_key = (field_id << 3) | 0
        return __class__.pack_varint(field_key) + __class__.pack_varint(value & 0xFF)

    @staticmethod
    def pack_float(field_id, value):
        field_key = (field_id << 3) | 5
        return __class__.pack_varint(field_key) + struct.pack("<f", value)

    @staticmethod
    def pack_int32(field_id, value):
        field_key = (field_id << 3) | 0
        return __class__.pack_varint(field_key) + __class__.pack_varint(value)

    @staticmethod
    def pack_int64(field_id, value):
        field_key = (field_id << 3) | 0
        return __class__.pack_varint(field_key) + __class__.pack_varint(value)

    @staticmethod
    def pack_string(field_id, value):
        field_key = (field_id << 3) | 2
        content = value.encode("utf-8") if isinstance(value, str) else value
        return (
            __class__.pack_varint(field_key)
            + __class__.pack_varint(len(content))
            + content
        )

    @staticmethod
    def pack_struct(field_id, data):
        field_key = (field_id << 3) | 2
        if isinstance(data, bytes):
            content = data
        else:
            content = b""
            for item in data:
                content += __class__.serialize(item[0], item[1], item[2])
        return (
            __class__.pack_varint(field_key)
            + __class__.pack_varint(len(content))
            + content
        )

    @staticmethod
    def pack_map(field_id, data):
        field_key = (field_id << 3) | 2
        ktype = data[0]
        vtype = data[1]
        vdata = data[2]
        content = b""
        for k, v in vdata.items():
            content += __class__.serialize(ktype, 1, k)
            content += __class__.serialize(vtype, 2, v)
        return (
            __class__.pack_varint(field_key)
            + __class__.pack_varint(len(content))
            + content
        )

    @staticmethod
    def pack_list(field_id, data):
        field_key = (field_id << 3) | 2
        vtype = data[0]
        vdata = data[1]
        content = b""
        for item in vdata:
            content += __class__.serialize(vtype, 1, item)
        return (
            __class__.pack_varint(field_key)
            + __class__.pack_varint(len(content))
            + content
        )
