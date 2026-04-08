import struct

from .DummyProtocol import DummyThrift


class ProtobufSerializer:
    @staticmethod
    def serialize(ttype, field_id, data):
        payload = b""
        if data is None:
            return payload
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
    def deserialize(data: bytes, readableCls=None, wrap_fn=None):
        if readableCls is not None:
            cls = readableCls if isinstance(readableCls, type) else type(readableCls)
            spec = getattr(cls, "thrift_spec", None)
            if spec is not None:
                field0 = next((e for e in spec if e is not None and e[0] == 0), None)
                if field0 is not None and field0[1] == 12:
                    type_args = field0[3] if len(field0) > 3 else None
                    nested_cls = type_args[0] if type_args else None
                    nested_spec = (
                        type_args[1]
                        if type_args and type_args[1] is not None
                        else getattr(nested_cls, "thrift_spec", None)
                    )
                    if nested_cls is not None and nested_spec is not None:
                        success = __class__._decode_with_spec(
                            data, nested_spec, nested_cls, wrap_fn
                        )
                        if success is None:
                            raise ValueError("Invalid protobuf data")
                        result_ins = cls()
                        setattr(result_ins, field0[2], success)
                        return (
                            wrap_fn(result_ins) if wrap_fn is not None else result_ins
                        )
                result = __class__._decode_with_spec(data, spec, cls, wrap_fn)
                if result is None:
                    raise ValueError("Invalid protobuf data")
                return result
        result = __class__._decode_raw(data)
        if result is None:
            raise ValueError("Invalid protobuf data")
        return result

    @staticmethod
    def _decode_with_spec(data: bytes, thrift_spec, cls=None, wrap_fn=None):
        spec_map = {}
        for entry in thrift_spec:
            if entry is None:
                continue
            spec_map[entry[0]] = entry

        instance = cls() if cls is not None else None
        result = {}

        pos = 0
        while pos < len(data):
            field_key, n = __class__.unpack_varint(data, pos)
            pos += n
            field_id = field_key >> 3
            wire_type = field_key & 0x07
            if field_id == 0:
                return None

            spec_entry = spec_map.get(field_id)
            ttype = spec_entry[1] if spec_entry else None
            field_name = spec_entry[2] if spec_entry and len(spec_entry) > 2 else None
            type_args = spec_entry[3] if spec_entry and len(spec_entry) > 3 else None

            if wire_type == 0:
                val, n = __class__.unpack_varint(data, pos)
                pos += n
            elif wire_type == 1:
                if pos + 8 > len(data):
                    return None
                val = struct.unpack_from("<d", data, pos)[0]
                pos += 8
            elif wire_type == 2:
                length, n = __class__.unpack_varint(data, pos)
                pos += n
                if pos + length > len(data):
                    return None
                raw = data[pos : pos + length]
                pos += length
                val = __class__._interp_wire2(raw, ttype, type_args, wrap_fn)
            elif wire_type == 5:
                if pos + 4 > len(data):
                    return None
                val = struct.unpack_from("<f", data, pos)[0]
                pos += 4
            else:
                return None

            if instance is not None:
                if field_name is not None:
                    if ttype in (14, 15):
                        existing = getattr(instance, field_name, None)
                        if existing is None:
                            existing = []
                            setattr(instance, field_name, existing)
                        if isinstance(val, list):
                            existing.extend(val)
                        else:
                            existing.append(val)
                    else:
                        setattr(instance, field_name, val)
            else:
                if ttype in (14, 15):
                    if field_id not in result:
                        result[field_id] = []
                    if isinstance(val, list):
                        result[field_id].extend(val)
                    else:
                        result[field_id].append(val)
                else:
                    result[field_id] = val

        if pos != len(data):
            return None
        if instance is not None:
            return wrap_fn(instance) if wrap_fn is not None else instance
        return result

    @staticmethod
    def _interp_wire2(raw: bytes, ttype, type_args, wrap_fn=None):
        if ttype == 12:
            # type_args = [NestedClass, NestedClass.thrift_spec]
            if type_args and len(type_args) >= 2:
                nested_cls = type_args[0]
                nested_spec = (
                    type_args[1]
                    if type_args[1] is not None
                    else getattr(nested_cls, "thrift_spec", None)
                )
                if nested_spec is not None:
                    return __class__._decode_with_spec(
                        raw, nested_spec, nested_cls, wrap_fn
                    )
            return __class__._decode_raw(raw)
        elif ttype in (14, 15):
            # type_args = (elem_ttype, [ElemClass, ElemClass.thrift_spec], bool)
            elem_ttype = type_args[0] if type_args else None
            elem_args = type_args[1] if type_args and len(type_args) > 1 else None
            if elem_ttype == 12:
                # elem_args = [ElemClass, ElemClass.thrift_spec]
                elem_cls = None
                elem_spec = None
                if isinstance(elem_args, (list, tuple)) and len(elem_args) >= 2:
                    elem_cls = elem_args[0]
                    elem_spec = (
                        elem_args[1]
                        if elem_args[1] is not None
                        else getattr(elem_cls, "thrift_spec", None)
                    )
                if elem_spec is not None and elem_cls is not None:
                    item = __class__._decode_with_spec(
                        raw, elem_spec, elem_cls, wrap_fn
                    )
                    return [item] if item is not None else []
            elif elem_ttype in (8, 10):
                vals = []
                p = 0
                while p < len(raw):
                    v, n = __class__.unpack_varint(raw, p)
                    p += n
                    vals.append(v)
                return vals
            elif elem_ttype == 11:
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError:
                    return raw
            return __class__._decode_raw(raw) or raw
        elif ttype == 13:
            return __class__._decode_raw(raw) or raw
        elif ttype == 11:
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw
        else:
            nested = __class__._decode_raw(raw)
            if nested is not None:
                return nested
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw

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
        if isinstance(data, DummyThrift):
            data = data.dd_slist()
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
        vtype = data[0]
        vdata = data[1]
        result = b""
        for item in vdata:
            result += __class__.serialize(vtype, field_id, item)
        return result
