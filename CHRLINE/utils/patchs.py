

@classmethod
def f_enum_missing(cls, value):
    if isinstance(value, int):
        m = int.__new__(cls, value)
        m._name_ = "_NOTSET_"
        m._value_ = value
        return m
    raise ValueError

def p_json_serializable():
    # https://stackoverflow.com/a/68926979

    from json import JSONEncoder
    def wrapped_default(self, obj):
        return getattr(obj.__class__, "__json__", wrapped_default.default)(obj)
    wrapped_default.default = JSONEncoder().default
    
    # apply the patch
    JSONEncoder.original_default = JSONEncoder.default
    JSONEncoder.default = wrapped_default

def p_patch_all():
    from enum import Enum

    if Enum:
        setattr(Enum, "_missing_", f_enum_missing)

    p_json_serializable()