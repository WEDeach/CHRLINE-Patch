import base64
import hashlib
import hmac
import os
import time

import axolotl_curve25519 as Curve25519
from CHRLINE import CHRLINE
from CHRLINE.exceptions import LineServiceException
from CHRLINE.utils.hashhash import h_pwd_by_scrypt


def getSHA256Sum(*args):
    instance = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            arg = arg.encode()
        instance.update(arg)
    return instance.digest()


def get_issued_at() -> bytes:
    return base64.b64encode(f"iat: {int(time.time()) * 60}\n".encode("utf-8")) + b"."


def get_digest(key: bytes, iat: bytes) -> bytes:
    return base64.b64encode(hmac.new(key, iat, hashlib.sha1).digest())


def create_token(auth_key: str) -> str:
    mid, key = auth_key.partition(":")[::2]
    key = base64.b64decode(key.encode("utf-8"))
    iat = get_issued_at()

    digest = get_digest(key, iat).decode("utf-8")
    iat = iat.decode("utf-8")

    return mid + ":" + iat + "." + digest


UPDATE_NAME = True
DISPLAY_NAME = "yinmo"
PWD = "test2021Chrline"
OS_MODEL = "SM-G975N"
APP_VER = "15.7.1"


cl = CHRLINE(device="ANDROID", version=APP_VER, noLogin=True)
cl.register_headers["User-Agent"] = f"Line/{APP_VER}"
session = cl.openPrimarySession()

print(f"[SESSION] {session}")
info = cl.getCountryInfo(session)
phone = input("input your phone number(0936....): ")
region = input("input phone number region(TW or JP or...): ")

allowedRegMethod = cl.getAllowedRegistrationMethod(session, region)
phone2 = cl.getPhoneVerifMethodForRegistration(session, phone, region, OS_MODEL)
availableMethods = phone2[1]
prettifiedPhoneNumber = phone2[2]

print(f"[PHONE] {prettifiedPhoneNumber}")
print(f"[VerifMethod] {availableMethods}")

try:
    sendPin = cl.requestToSendPhonePinCode(session, prettifiedPhoneNumber, region, 1)
    print(f"[SEND PIN CODE] {sendPin}")
except LineServiceException as e:
    if e.code == 5:
        _auth = e.raw["_data"][11]
        _url = _auth[1]
        _token = _auth[2]
        HumanVerif(_url, _token)
    else:
        raise e

for _ in range(2):
    # 1 for Human verif
    # 2 for resend pin code
    if input("Need resend Pincode?(y/n): ").lower() == "y":
        cl.requestToSendPhonePinCode(session, prettifiedPhoneNumber, region, 1)
    else:
        break  # break for next

recvPincode = False
while not recvPincode:
    pin = input("Enter Pin code (enter `exit` to exit): ")
    if pin.lower() == "exit":
        exit()
    try:
        verify = cl.verifyPhonePinCode(session, prettifiedPhoneNumber, region, pin)
        print(f"[VERIFY PIN CODE] {verify}")
        recvPincode = True
    except LineServiceException as e:
        if e.code == 2:
            print(f"[VERIFY PIN CODE] {e.message}")
        else:
            raise e

cl.validateProfile(session, "yinmo")

res_pwd_hash_params = cl.getPasswordHashingParametersForPwdReg(session)
print(f"res_pwd_hash_params: {res_pwd_hash_params}")

pwd_params = res_pwd_hash_params[1]
hmac_key = base64.b64decode(pwd_params[1])
scrypt_params = pwd_params[2]
scrypt_salt = base64.b64decode(scrypt_params[1])
scrypt_nrp = scrypt_params[2]
scrypt_dkLen = scrypt_params[3]

i_nrp = int(scrypt_nrp, 16)
i_n = 2 ** ((i_nrp >> 16) & 0xFFFF)
i_r = (i_nrp >> 8) & 0xFF
i_p = i_nrp & 0xFF

encPwd = h_pwd_by_scrypt(
    PWD, hmac_key, salt=scrypt_salt, n=i_n, r=i_r, p=i_p, dklen=scrypt_dkLen
)
print(f"[encPwd] {encPwd}")

setPwd = cl.setHashedPassword(session, encPwd)
print(f"[setPassword] {setPwd}")

register = cl.registerPrimaryUsingPhoneWithTokenV3(session)
print(f"[REGISTER] {register}")
print("---------------------------")
authKey = register[1]
tokenV3IssueResult = register[2]
mid = register[3]
primaryToken = create_token(authKey)
print(f"[AuthKey]: {authKey}")
print(f"[PrimaryToken]: {primaryToken}")
print(f"[UserMid]: {mid}")
print("---------------------------")
accessTokenV3 = tokenV3IssueResult[1]
print(f"[accessTokenV3]: {accessTokenV3}")
refreshToken = tokenV3IssueResult[2]
print(f"[refreshToken]: {refreshToken}")
durationUntilRefreshInSec = tokenV3IssueResult[3]
print(f"[durationUntilRefreshInSec]: {durationUntilRefreshInSec}")
refreshApiRetryPolicy = tokenV3IssueResult[4]
loginSessionId = tokenV3IssueResult[5]
print(f"[loginSessionId]: {loginSessionId}")
tokenIssueTimeEpochSec = tokenV3IssueResult[6]
print(f"[tokenIssueTimeEpochSec]: {tokenIssueTimeEpochSec}")

cl = CHRLINE(primaryToken, version=APP_VER, device="ANDROID")  # login

if UPDATE_NAME:
    cl.updateProfileAttribute(2, DISPLAY_NAME)  # update display name

# for i in range(100):
# accessTokenV3 = cl.refreshAccessToken(refreshToken)
# print(f"[accessTokenV3_2]: {accessTokenV3}")
