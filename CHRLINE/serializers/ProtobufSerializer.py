import inspect
import re
import struct

from thrift.protocol.TCompactProtocol import TCompactProtocol as _tcProtocol
from thrift.transport.TTransport import TMemoryBuffer as _TMemoryBuffer

from .DummyProtocol import DummyThrift

FLOW_PROTOBUF_DECODER = 1
_ENUM_MAP_CACHE: dict = {}


def _extract_enum_map(cls) -> dict:
    if cls in _ENUM_MAP_CACHE:
        return _ENUM_MAP_CACHE[cls]
    result = {}
    try:
        source = inspect.getsource(cls.read)
        module = inspect.getmodule(cls)
        if module is not None:
            current_fid = None
            for line in source.splitlines():
                m = re.search(r"fid\s*==\s*(\d+)", line)
                if m:
                    current_fid = int(m.group(1))
                elif current_fid is not None:
                    m = re.search(r"=\s*(\w+)\(iprot\.readI32\(\)\)", line)
                    if m:
                        enum_cls = getattr(module, m.group(1), None)
                        if enum_cls is not None and isinstance(enum_cls, type):
                            result[current_fid] = enum_cls
    except (TypeError, OSError):
        pass
    _ENUM_MAP_CACHE[cls] = result
    return result


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
                if FLOW_PROTOBUF_DECODER == 2:
                    return __class__._deserialize_v2(data, cls, spec, field0, wrap_fn)
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
    def _deserialize_v2(data: bytes, cls, spec, field0, wrap_fn):
        if field0 is not None and field0[1] == 12:
            type_args = field0[3] if len(field0) > 3 else None
            target_cls = type_args[0] if type_args else None
            target_spec = (
                (
                    type_args[1]
                    if type_args and type_args[1] is not None
                    else getattr(target_cls, "thrift_spec", None)
                )
                if target_cls
                else None
            )
            is_wrapped = True
        else:
            target_cls = cls
            target_spec = spec
            is_wrapped = False

        if target_cls is None or target_spec is None:
            raise ValueError("Invalid protobuf data")

        slist = __class__._decode_to_slist(data, target_spec)
        if slist is None:
            raise ValueError("Invalid protobuf data")

        compact_bytes = __class__._slist_to_compact_bytes(slist)
        fresh_ins = target_cls()
        read_proto = _tcProtocol(_TMemoryBuffer(compact_bytes))
        if wrap_fn is not None:
            dt = wrap_fn(fresh_ins)
            dt.read(read_proto)
        else:
            fresh_ins.read(read_proto)
            dt = fresh_ins

        if is_wrapped:
            result_ins = cls()
            setattr(result_ins, field0[2], dt)
            return wrap_fn(result_ins) if wrap_fn is not None else result_ins
        return dt

    @staticmethod
    def _parse_pb_fields(data: bytes):
        fields = []
        pos = 0
        try:
            while pos < len(data):
                field_key, n = __class__.unpack_varint(data, pos)
                pos += n
                fid = field_key >> 3
                wt = field_key & 0x07
                if fid == 0:
                    return None
                if wt == 0:
                    val, n = __class__.unpack_varint(data, pos)
                    pos += n
                elif wt == 1:
                    if pos + 8 > len(data):
                        return None
                    val = struct.unpack_from("<d", data, pos)[0]
                    pos += 8
                elif wt == 2:
                    length, n = __class__.unpack_varint(data, pos)
                    pos += n
                    if pos + length > len(data):
                        return None
                    val = data[pos : pos + length]
                    pos += length
                elif wt == 5:
                    if pos + 4 > len(data):
                        return None
                    val = struct.unpack_from("<f", data, pos)[0]
                    pos += 4
                else:
                    return None
                fields.append((fid, wt, val))
        except (ValueError, struct.error):
            return None
        if pos != len(data):
            return None
        return fields

    @staticmethod
    def _decode_to_slist(data: bytes, thrift_spec):
        spec_map = {e[0]: e for e in thrift_spec if e is not None}
        fields = __class__._parse_pb_fields(data)
        if fields is None:
            return None
        result = []
        for fid, wt, val in fields:
            spec_entry = spec_map.get(fid)
            ttype = spec_entry[1] if spec_entry else None
            type_args = spec_entry[3] if spec_entry and len(spec_entry) > 3 else None
            if wt == 2:
                val = __class__._interp_wire2_slist(val, ttype, type_args)
            if ttype in (14, 15):
                existing = next((item for item in result if item[1] == fid), None)
                if existing is None:
                    if wt == 2:
                        result.append([ttype, fid, val])
                    else:
                        elem_ttype = type_args[0] if type_args else 8
                        result.append([ttype, fid, [elem_ttype, [val]]])
                else:
                    if wt == 2:
                        existing[2][1].extend(
                            val[1] if isinstance(val, list) and len(val) == 2 else [val]
                        )
                    else:
                        existing[2][1].append(val)
            else:
                result.append([ttype, fid, val])
        return result

    @staticmethod
    def _interp_wire2_slist(raw: bytes, ttype, type_args):
        if ttype == 12:
            if type_args and len(type_args) >= 2:
                nested_cls = type_args[0]
                nested_spec = (
                    type_args[1]
                    if type_args[1] is not None
                    else getattr(nested_cls, "thrift_spec", None)
                )
                if nested_spec is not None:
                    return __class__._decode_to_slist(raw, nested_spec)
            return __class__._decode_raw(raw)
        elif ttype in (14, 15):
            elem_ttype = type_args[0] if type_args else None
            elem_args = type_args[1] if type_args and len(type_args) > 1 else None
            if elem_ttype == 12:
                elem_cls = elem_spec = None
                if isinstance(elem_args, (list, tuple)) and len(elem_args) >= 2:
                    elem_cls = elem_args[0]
                    elem_spec = (
                        elem_args[1]
                        if elem_args[1] is not None
                        else getattr(elem_cls, "thrift_spec", None)
                    )
                if elem_spec and elem_cls:
                    item = __class__._decode_to_slist(raw, elem_spec)
                    return [elem_ttype, [item] if item is not None else []]
            elif elem_ttype in (8, 10):
                vals = []
                p = 0
                while p < len(raw):
                    v, n = __class__.unpack_varint(raw, p)
                    p += n
                    vals.append(v)
                return [elem_ttype, vals]
            return [elem_ttype, [raw]]
        elif ttype == 11:
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw
        else:
            return raw

    @staticmethod
    def _slist_to_compact_bytes(slist: list) -> bytes:
        buf = _TMemoryBuffer()
        proto = _tcProtocol(buf)
        proto.writeStructBegin("")
        __class__._write_slist_fields(proto, slist)
        proto.writeFieldStop()
        proto.writeStructEnd()
        return buf.getvalue()

    @staticmethod
    def _write_slist_fields(proto, slist: list):
        for entry in slist:
            ttype, fid, val = entry[0], entry[1], entry[2]
            if val is None:
                continue
            proto.writeFieldBegin("", ttype, fid)
            __class__._write_value(proto, ttype, val)
            proto.writeFieldEnd()

    @staticmethod
    def _write_value(proto, ttype, val):
        if ttype == 2:
            proto.writeBool(bool(val))
        elif ttype == 3:
            proto.writeByte(val)
        elif ttype == 4:
            proto.writeDouble(val)
        elif ttype == 8:
            proto.writeI32(val)
        elif ttype == 10:
            proto.writeI64(val)
        elif ttype == 11:
            proto.writeString(val)
        elif ttype == 12:
            proto.writeStructBegin("")
            if isinstance(val, list):
                __class__._write_slist_fields(proto, val)
            proto.writeFieldStop()
            proto.writeStructEnd()
        elif ttype in (14, 15):
            elem_ttype = val[0] if isinstance(val, list) and len(val) >= 2 else 11
            items = val[1] if isinstance(val, list) and len(val) >= 2 else []
            if items is None:
                items = []
            if ttype == 14:
                proto.writeSetBegin(elem_ttype, len(items))
            else:
                proto.writeListBegin(elem_ttype, len(items))
            for item in items:
                __class__._write_value(proto, elem_ttype, item)
            if ttype == 14:
                proto.writeSetEnd()
            else:
                proto.writeListEnd()
        elif ttype == 13:
            ktype, vtype, kvdata = val[0], val[1], val[2]
            proto.writeMapBegin(ktype, vtype, len(kvdata))
            for k, v in kvdata.items():
                __class__._write_value(proto, ktype, k)
                __class__._write_value(proto, vtype, v)
            proto.writeMapEnd()

    @staticmethod
    def _decode_with_spec(data: bytes, thrift_spec, cls=None, wrap_fn=None):
        spec_map = {e[0]: e for e in thrift_spec if e is not None}
        fields = __class__._parse_pb_fields(data)
        if fields is None:
            return None
        instance = cls() if cls is not None else None
        result = {}
        enum_map = (
            _extract_enum_map(cls)
            if cls is not None and FLOW_PROTOBUF_DECODER == 1
            else {}
        )
        for fid, wt, val in fields:
            spec_entry = spec_map.get(fid)
            ttype = spec_entry[1] if spec_entry else None
            field_name = spec_entry[2] if spec_entry and len(spec_entry) > 2 else None
            type_args = spec_entry[3] if spec_entry and len(spec_entry) > 3 else None
            if wt == 0 and ttype == 8:
                enum_cls = enum_map.get(fid)
                if enum_cls is not None:
                    try:
                        val = enum_cls(val)
                    except (ValueError, KeyError):
                        pass
            elif wt == 2:
                val = __class__._interp_wire2(val, ttype, type_args, wrap_fn)
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
                    if fid not in result:
                        result[fid] = []
                    if isinstance(val, list):
                        result[fid].extend(val)
                    else:
                        result[fid].append(val)
                else:
                    result[fid] = val
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
        fields = __class__._parse_pb_fields(data)
        if fields is None:
            return None
        result = {}
        for fid, wt, val in fields:
            if wt == 2:
                val = __class__._decode_wire2(val)
            if fid in result:
                existing = result[fid]
                if isinstance(existing, list):
                    existing.append(val)
                else:
                    result[fid] = [existing, val]
            else:
                result[fid] = val
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
            if pos + n >= len(data):
                raise ValueError("varint truncated")
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
        if not isinstance(value, (str, bytes)):
            value = str(value)
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
        if vdata is not None:
            for item in vdata:
                result += __class__.serialize(vtype, field_id, item)
        return result
