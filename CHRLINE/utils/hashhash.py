import base64
import hashlib
import hmac
import math


def h_pwd_by_scrypt(
    password: str, hmac_key: bytes, salt: bytes, n: int, r: int, p: int, dklen: int = 32
):
    hmac_result = hmac.new(hmac_key, password.encode("utf-8"), hashlib.sha256).digest()
    b64_str = base64.b64encode(
        hashlib.scrypt(hmac_result, salt=salt, n=n, r=r, p=p, dklen=dklen)
    ).decode()
    b64_salt = base64.b64encode(salt).decode()
    log2_n = int(math.log2(n))
    nrp = (log2_n << 16) | (r << 8) | p
    return "$".join(["$s0", f"{nrp:05x}", b64_salt, b64_str])
