

@classmethod
def enum_missing(cls, value):
    if isinstance(value, int):
        m = int.__new__(cls, value)
        m._name_ = "_NOTSET_"
        m._value_ = value
        return m
    raise ValueError