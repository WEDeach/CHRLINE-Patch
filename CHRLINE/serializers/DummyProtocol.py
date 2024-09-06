from typing import Any, Dict, List, Optional, Tuple


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
    __is_dummy = True
    __is_raw = False

    def __init__(
        self,
        name: Optional[str] = None,
        ins: object = None,
        **kwargs,
    ):
        if name is not None:
            self.__name__ = name
        if ins is not None:
            self.__ins = ins
        if kwargs:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __getitem__(self, index):
        thrift_spec: Optional[Tuple[Any]] = getattr(self, "thrift_spec", None)
        if thrift_spec is not None:
            for spec in thrift_spec:
                if spec is None:
                    continue
                fid, ftype, fname, fttypes, _ = spec
                if fid == index:
                    return getattr(self, fname)
        return getattr(self, f"val_{index}")

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
    def get(self):
        return self.__getitem__

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
            thrift_spec: Optional[Tuple[Any]] = getattr(self, "thrift_spec", None)
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
            thrift_spec: Optional[Tuple[Any]] = getattr(self, "thrift_spec", None)
            if thrift_spec is not None:
                for spec in thrift_spec:
                    if spec is None:
                        continue
                    fid, ftype, fname, fttypes, _ = spec
                    rk = f"val_{fid}"
                    if rk in r:
                        del r[rk]
        return r

    def read(self, iprot):
        r = self.thrift_ins
        read_org = getattr(r, "read")
        read_org(iprot)

        # 思路是先跑原本的read 再去取代值
        def warp_spec(r, thrift_spec):
            for spec in thrift_spec:
                if spec is None:
                    continue
                fid, ftype, fname, fttypes, _ = spec
                data = getattr(r, fname)

                def warp(r, fname, ftype, data, fttypes):
                    if isinstance(r, Exception):
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

                def warp_struct(r, rd):
                    r2 = self.wrap_thrift(rd, self.is_dummy)
                    warp_spec(r2.thrift_ins, rd.thrift_spec)
                    return r2

                warp(r, fname, ftype, data, fttypes)

        thrift_spec: Optional[Tuple[Any]] = getattr(r, "thrift_spec", None)
        if thrift_spec is not None:
            warp_spec(r, thrift_spec)

    @staticmethod
    def wrap_thrift(thrift_ins, isDummy=True):
        r = DummyThrift(thrift_ins.__class__.__name__, ins=thrift_ins)
        r.is_dummy = isDummy
        if isinstance(thrift_ins, BaseException):
            r.is_raw = True
        return r

    def __getattr__(self, name):
        if name not in ["_DummyThrift__ins", "thrift_ins"]:
            r = self.thrift_ins
            if r is not None:
                r2 = getattr(r, name, None)
                if r2 is not None:
                    if isinstance(r2, DummyThrift) and r2.is_raw:
                        return r2.thrift_ins
                    return r2
        return None

    def __setattr__(self, k, v):
        if k.startswith("val_"):
            k2 = k.split("val_")[1]
            r2 = self.thrift_ins
            if r2 is not None:
                # patch thrift field
                r3 = self[int(k2)]

                def setter(r3, v):
                    if type(r3) in [list, set]:
                        i = 0
                        for _r3 in r3:
                            setter(_r3, v[i])
                            i += 1
                    elif isinstance(r3, DummyThrift):
                        for vk, vv in v.__dict__.items():
                            setattr(r3, vk, vv)
                    return r3

                setter(r3, v)
        super().__setattr__(k, v)

    def __repr__(self):
        d = self.__dict__
        if self.is_dummy:
            return str(self.dd())
        if self.thrift_ins is not None:
            d = self.thrift_ins.__dict__
            d.update(self.dd_diff())
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
