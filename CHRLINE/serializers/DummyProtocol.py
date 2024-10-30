from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from ..client import CHRLINE


class DummyProtocolData:
    def __init__(self, id, type, data, subType: Optional[list] = None):
        self.id = id
        self.type = type
        self.data = data
        self.subType = []
        if subType is not None:
            for _subType in subType:
                self.addSubType(_subType)

    def addSubType(self, type):
        self.subType.append(type)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, __class__):
            return super().__eq__(__o)
        return self.data == __o

    def __hash__(self):
        return hash(self.data)

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))


class DummyProtocol:
    def __init__(self, protocol: int = 5, data: Optional[DummyProtocolData] = None):
        self.protocol = protocol
        self.data = data

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))


class DummyThrift:
    __ins: object = None
    __is_dummy = True
    __is_raw = False
    _ref: Union[Any, "DummyThrift"]
    _sync_wrapper = True

    def __init__(
        self,
        name: Optional[str] = None,
        ins: object = None,
        cl: Optional["CHRLINE"] = None,
        **kwargs,
    ):
        self.__field_map__ = {}
        if name is not None:
            self.__name__ = name
        if ins is not None:
            self.__ins = ins
        if cl is not None:
            self.__cl = cl
        if kwargs:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    @property
    def client(self) -> "CHRLINE":
        if self.__cl is None:
            raise NotImplementedError
        return self.__cl

    @property
    def thrift_ins(self):
        return self.__ins

    @property
    def is_dummy(self):
        return self.__is_dummy

    @is_dummy.setter
    def is_dummy(self, val: bool):
        self.__is_dummy = val

        def patch(dv):
            if isinstance(dv, DummyThrift):
                dv.is_dummy = val
            if isinstance(dv, dict):
                _d = {}
                for dk2, dv2 in dv.items():
                    _dk = patch(dk2)
                    _dv = patch(dv2)
                    _d[_dk] = _dv
                dv.clear()
                dv.update(_d)
            if type(dv) in [list, set]:
                _d = []
                for dv2 in dv:
                    _d.append(patch(dv2))
                if isinstance(dv, list):
                    dv.clear()
                    dv.extend(_d)
                elif isinstance(dv, set):
                    dv.clear()
                    dv.update(set(_d))
            return dv

        for dk, dv in self.dd().items():
            patch(dv)

    @property
    def is_raw(self):
        return self.__is_raw

    @is_raw.setter
    def is_raw(self, val: bool):
        self.__is_raw = val

    @property
    def sync_wrapper(self):
        return self._sync_wrapper

    @sync_wrapper.setter
    def sync_wrapper(self, val: bool):
        self._sync_wrapper = val

        def patch(dv):
            if isinstance(dv, DummyThrift):
                dv.sync_wrapper = val
            if isinstance(dv, dict):
                _d = {}
                for dk2, dv2 in dv.items():
                    _dk = patch(dk2)
                    _dv = patch(dv2)
                    _d[_dk] = _dv
                dv.clear()
                dv.update(_d)
            if type(dv) in [list, set]:
                _d = []
                for dv2 in dv:
                    _d.append(patch(dv2))
                if isinstance(dv, list):
                    dv.clear()
                    dv.extend(_d)
                elif isinstance(dv, set):
                    dv.clear()
                    dv.update(set(_d))
            return dv

        for dk, dv in self.dd().items():
            patch(dv)

    @property
    def get(self):
        return self.__getitem__

    def check_fid(self, key: int, default=None):
        r = self.dd()
        return r[key] if key in r else default

    @property
    def __ins_name__(self):
        ins = self.thrift_ins
        if ins is None:
            ins = self
        m = ins.__class__.__module__
        n = ins.__class__.__name__
        m = m.split(".")[-1]
        return m + "." + n

    @property
    def field_names(self):
        r: List[str] = []
        r2 = self.thrift_ins
        if r2 is not None:
            thrift_spec: Optional[Tuple[Any]] = getattr(r2, "thrift_spec", None)
            if thrift_spec is not None:
                for spec in thrift_spec:
                    if spec is None:
                        continue
                    fid, ftype, fname, fttypes, _ = spec
                    r.append(fname)
        return r

    def dd(self):
        r = {}
        r2 = self.thrift_ins
        if r2 is not None and not self.is_dummy:
            # thrift dict
            thrift_spec: Optional[Tuple[Any]] = getattr(self, "thrift_spec", None)
            if thrift_spec is not None:
                for spec in thrift_spec:
                    if spec is None:
                        continue
                    fid, ftype, fname, fttypes, _ = spec
                    r[fid] = self[fid]

        # dummy dict
        for key, rv in self.__dict__.items():
            rk = key
            if key.startswith("val_"):
                rk = int(key.split("val_")[1])
                if rk not in r:
                    r[rk] = rv
        return r

    def dd_diff(self):
        r: Dict[str, Any] = {}
        r2 = self.thrift_ins
        if r2 is not None:
            # dummy dict
            for key, rv in self.__dict__.items():
                if key.startswith("val_"):
                    r[key] = rv

            # thrift dict
            thrift_spec: Optional[Tuple[Any]] = getattr(r2, "thrift_spec", None)
            if thrift_spec is not None:
                for spec in thrift_spec:
                    if spec is None:
                        continue
                    fid, ftype, fname, fttypes, _ = spec
                    rk = f"val_{fid}"
                    if rk in r:
                        del r[rk]
        return r

    def dd_loc(self):
        r: Dict[str, Any] = {}
        for key, rv in self.__dict__.items():
            if not key.startswith("val_") and not key.startswith("_"):
                r[key] = rv
        return r

    def read(self, iprot):
        r = self.thrift_ins
        read_org = getattr(r, "read")
        read_org(iprot)

        # 思路是先跑原本的read 再去取代值
        def warp_spec(r: DummyThrift, thrift_spec):
            for spec in thrift_spec:
                if spec is None:
                    continue
                fid, ftype, fname, fttypes, _ = spec
                r2 = r.thrift_ins
                data = getattr(r2, fname)

                def warp(r: DummyThrift, fname, ftype, data, fttypes):
                    if isinstance(r.thrift_ins, BaseException):
                        pass
                    elif data is not None:
                        if ftype == 12:
                            data2 = warp_struct(r, data)
                            if fname is not None:
                                setattr(r, fname, data2)
                            return data2
                        if ftype in [13]:
                            data2 = {}
                            for dk, dv in data.items():
                                dk2 = warp(r, None, fttypes[0], dk, fttypes[1])
                                dv2 = warp(r, None, fttypes[2], dv, fttypes[3])
                                data2[dk2] = dv2
                            data.clear()
                            data.update(data2)
                            return data2
                        if ftype in [14, 15]:
                            data2 = []
                            for _data in data:
                                data2.append(
                                    warp(r, None, fttypes[0], _data, fttypes[1])
                                )
                            if ftype == 14:
                                data.clear()
                                data.update(set(data2))
                            elif ftype == 15:
                                data.clear()
                                data.extend(data2)
                            return data2
                        return data

                def warp_struct(r: DummyThrift, rd):
                    r2 = self.wrap_thrift(self.client, rd, self.is_dummy)
                    r2.set_ref(r)
                    warp_spec(r2, rd.thrift_spec)
                    return r2

                warp(r, fname, ftype, data, fttypes)

        thrift_spec: Optional[Tuple[Any]] = getattr(r, "thrift_spec", None)
        if thrift_spec is not None:
            warp_spec(self, thrift_spec)

    @staticmethod
    def wrap_thrift(cl, thrift_ins, isDummy=True):
        n = thrift_ins.__class__.__name__
        b = {"ins": thrift_ins, "cl": cl}
        r = DummyThrift(n, **b)
        w = cl.getTypeWrapper(r.__ins_name__)
        if w is not None:
            r = w(n, **b)
        r.is_dummy = isDummy
        if isinstance(thrift_ins, BaseException):
            r.is_raw = True
        return r

    def set_ref(self, ref: "DummyThrift"):
        self._ref = ref

    def dd_specs(self):
        r: Optional[tuple] = None
        r2 = self.thrift_ins
        thrift_spec: Optional[Tuple[Any]] = getattr(r2, "thrift_spec", None)
        if thrift_spec is not None:
            return thrift_spec
        if self.__field_map__:
            r = ()
            for fk, fv in self.__field_map__.items():
                if isinstance(fv, DummyProtocolData):
                    ft = fv.type
                    fts = None
                    if ft == 11:
                        fts = "UTF8"
                    elif ft == 13:
                        fts = (
                            fv.subType[0],
                            None,
                            fv.subType[1],
                            None,
                            False,
                        )
                    elif ft in [14, 15]:
                        fts = (
                            fv.subType[0],
                            None,
                            False,
                        )
                    r = r + (
                        (
                            fv.id,
                            fv.type,
                            "",
                            fts,
                            None,
                        ),
                    )
        return r

    def dd_slist(self):
        r = []
        specs = self.dd_specs()
        if specs is not None:
            for spec in specs:
                if spec is None:
                    continue
                fid, ftype, fname, fts, _ = spec
                data = self.get(fid)
                if data:

                    def dd(t, d):
                        if t == 12:
                            if isinstance(d, DummyThrift):
                                return d.dd_slist()
                            if isinstance(d, list):
                                dl = []
                                for d2 in d:
                                    if isinstance(d2, DummyThrift):
                                        dl.append(d2.dd_slist())
                                    else:
                                        dl.append(d2)
                                return dl
                        elif t == 13:
                            if fts is None:
                                raise ValueError
                            return [fts[0], fts[2], d]
                        elif t in [14, 15]:
                            if fts is None:
                                raise ValueError
                            return [fts[0], dd(fts[0], d)]
                        return d

                    r.append([ftype, fid, dd(ftype, data)])
        return r

    def __getitem__(self, index):
        # PRIORITY: thrift > dummy
        r = self.thrift_ins
        if r is not None:
            thrift_spec: Optional[Tuple[Any]] = getattr(r, "thrift_spec", None)
            if thrift_spec is not None:
                for spec in thrift_spec:
                    if spec is None:
                        continue
                    fid, ftype, fname, fttypes, _ = spec
                    if fid == index:
                        return getattr(r, fname)
        return getattr(self, f"val_{index}")

    def __setitem__(self, key, value):
        return self.__setattr__(f"val_{key}", value)

    def __getattr__(self, name):
        if name not in ["_DummyThrift__ins", "thrift_ins"]:
            r = self.thrift_ins
            if r is not None:
                ns = self.field_names
                if name in ns:
                    r2 = getattr(r, name, None)
                    if r2 is not None:
                        if isinstance(r2, DummyThrift) and r2.is_raw:
                            return r2.thrift_ins
                    return r2
        return super().__getattribute__(name)

    def __setattr__(self, k, v):
        _k = k
        if isinstance(k, DummyProtocolData):
            _k = k
            k = k.data
        if isinstance(v, DummyProtocolData):
            self.__field_map__[_k] = v
            v = v.data
        if not self.sync_wrapper:
            return super().__setattr__(k, v)
        k2: Union[int, None] = None
        if isinstance(k, str) and k.startswith("val_"):
            k2 = int(k.split("val_")[1])
        elif isinstance(k, int):
            # conv int to field id.
            k2 = k
            k = f"val_{k}"
        if k2 is not None:
            # patch int to thrift field
            r2 = self.thrift_ins
            if r2 is not None and not self.is_raw:
                thrift_spec = getattr(r2, "thrift_spec", None)
                if thrift_spec is not None:
                    for spec in thrift_spec:
                        if spec is None:
                            continue
                        fid, ftype, fname, fttypes, _ = spec
                        if fid == k2:

                            def setter(r1, r2, v):
                                if r1 is not None:
                                    r3 = getattr(r1, r2)
                                else:
                                    r3 = r2
                                if isinstance(r3, DummyThrift):
                                    for vk, vv in v.__dict__.items():
                                        setattr(r3, vk, vv)
                                    return r3
                                elif isinstance(r3, dict):
                                    v2 = {}
                                    for vk, vv in v.items():
                                        v2[vk] = setter(None, r3[vk], vv)
                                    if r1 is not None:
                                        setattr(r1, r2, v2)
                                    return v2
                                elif type(r3) in [list, set]:
                                    i = 0
                                    v2 = []
                                    for _r3 in r3:
                                        v2.append(setter(None, _r3, v[i]))
                                        i += 1
                                    if r1 is not None:
                                        setattr(r1, r2, v2)
                                    return v2
                                elif r1 is not None:
                                    _r = getattr(r1, r2)
                                else:
                                    _r = r2
                                vt = type(_r)
                                if issubclass(vt, Enum):
                                    if v in vt._value2member_map_:
                                        v = vt(v)
                                    else:
                                        log = self.client.get_logger("DUMMY").overload(
                                            "THRIFT"
                                        )
                                        log.warn(
                                            f"Enum '{_r.__class__.__name__}' missing value: {v}"
                                        )
                                if r1 is not None:
                                    object.__setattr__(r1, r2, v)
                                return v

                            setter(r2, fname, v)
        elif k in self.field_names:
            # patch thrift field to int
            r2 = self.thrift_ins
            thrift_spec = getattr(r2, "thrift_spec")
            for spec in thrift_spec:
                if spec is None:
                    continue
                fid, ftype, fname, fttypes, _ = spec
                if fname == k:
                    setattr(self, f"val_{fid}", v)
                    return
            return setattr(self.thrift_ins, k, v)
        super().__setattr__(k, v)

    def __repr__(self):
        d = self.dd()
        if self.is_dummy:
            d.update(self.dd_loc())
            return str(d)
        if self.thrift_ins is not None:
            d = self.thrift_ins.__dict__
            d.update(self.dd_diff())
            d.update(self.dd_loc())
        L = ["%s=%r" % (key, value) for key, value in d.items()]
        return "%s(%s)" % (self.__name__, ", ".join(L))


class DummyProtocolSerializer:
    def __init__(self, instance: Any, name: str, data: list, protocol: int):
        self.instance = instance
        self.name = name
        self.data = data
        self.protocol = protocol

    def __bytes__(self):
        """Convert to proto data."""
        data = []
        instance = self.instance
        protocol = self.protocol
        if protocol == 3:
            data = [128, 1, 0, 1] + instance.getStringBytes(self.name) + [0, 0, 0, 0]
        elif protocol in [4, 5]:
            protocol = 4
            data = [130, 33, 0] + instance.getStringBytes(self.name, isCompact=True)
        else:
            raise ValueError(f"Unknower protocol: {protocol}")
        data += instance.generateDummyProtocolField(self.data, protocol) + [0]
        return bytes(data)

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))
