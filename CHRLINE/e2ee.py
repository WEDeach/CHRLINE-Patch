# -*- coding: utf-8 -*-
"""
Author: YinMo
Version: 2.3.2
Description: support pm & group chat and encrypted-media!
"""
import base64
import hashlib
import json
import os
import secrets
from typing import Any, Optional, Union

import axolotl_curve25519 as Curve25519
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .exceptions import E2EESelfKeyNotFoundException, LineServiceException
from .helper import ChrHelperProtocol


class E2EE(ChrHelperProtocol):

    def __init__(self) -> None:
        self.__logger = self.client.get_logger("E2EE")
        self.__e2ee_key_id = None
        self.__cache_key = {}
        r = self.client.getE2EEPublicKeys()
        if isinstance(r, list):
            self.__e2ee_key_id = r[0][2]
            try:
                selfKeyData = self.client.getE2EESelfKeyData(self.client.mid)
                if selfKeyData["keyId"] != self.__e2ee_key_id:
                    # check e2ee key
                    r2 = self.client.getE2EESelfKeyDataByKeyId(self.__e2ee_key_id)
                    if r2 is None:
                        self.__logger.warn(f"E2EE Key not found: {self.__e2ee_key_id}")
            except E2EESelfKeyNotFoundException as e:
                self.__logger.warn(e.hint)

    def getE2EELocalPublicKey(self, mid, keyId, renewKey=False):
        toType = self.client.getToType(mid)
        cache_key = f"{mid}_{keyId}"
        if toType == 0:
            fd = ".e2eePublicKeys"
            fn = f"key_id_{keyId}.json"
            key = None
            if keyId is not None:
                key = self.client.getCacheData(fd, fn, False)
            if key is None:
                if cache_key not in self.__cache_key or renewKey:
                    self.__cache_key[cache_key] = self.client.negotiateE2EEPublicKey(
                        mid
                    )
                receiver_key_data = self.__cache_key[cache_key]
                specVersion = self.client.checkAndGetValue(
                    receiver_key_data, "specVersion", 3
                )
                if specVersion == -1:
                    raise Exception(f"Not support E2EE on {mid}")
                publicKey = self.client.checkAndGetValue(
                    receiver_key_data, "publicKey", 2
                )
                receiverKeyId = self.client.checkAndGetValue(publicKey, "keyId", 2)
                receiverKeyData = self.client.checkAndGetValue(publicKey, "keyData", 4)
                if receiverKeyData is not None:
                    key = base64.b64encode(receiverKeyData)
                    if receiverKeyId == keyId:
                        self.client.saveCacheData(fd, fn, key.decode(), False)
                    elif keyId is None:
                        return receiver_key_data
                    else:
                        raise Exception(
                            f"E2EE key id-{keyId} not found on {mid}, key id should be {receiverKeyId}"
                        )
                else:
                    raise Exception(f"E2EE key id-{keyId} not found on {mid}")
        else:
            fd = ".e2eeGroupKeys"
            fn = f"{mid}.json"
            key = self.client.getCacheData(fd, fn, False)
            if keyId is not None and key is not None:
                keyData = json.loads(key)
                if keyId != keyData["keyId"]:
                    self.__logger.warn(f"keyId mismatch: {mid}")
                    key = None
            else:
                key = None
            if key is None:
                E2EEGroupSharedKey = None
                if cache_key not in self.__cache_key or renewKey:
                    try:
                        E2EEGroupSharedKey = self.client.getLastE2EEGroupSharedKey(
                            2, mid
                        )
                    except LineServiceException as e:
                        if e.code == 5:
                            self.__logger.info(
                                f"E2EE key not registered on {mid}: {e.message}"
                            )
                            E2EEGroupSharedKey = self.tryRegisterE2EEGroupKey(mid)
                    self.__cache_key[cache_key] = E2EEGroupSharedKey
                E2EEGroupSharedKey = self.__cache_key[cache_key]
                groupKeyId = self.client.checkAndGetValue(
                    E2EEGroupSharedKey, "groupKeyId", 2
                )
                creator = self.client.checkAndGetValue(E2EEGroupSharedKey, "creator", 3)
                creatorKeyId = self.client.checkAndGetValue(
                    E2EEGroupSharedKey, "creatorKeyId", 4
                )
                receiver = self.client.checkAndGetValue(
                    E2EEGroupSharedKey, "receiver", 5
                )
                receiverKeyId = self.client.checkAndGetValue(
                    E2EEGroupSharedKey, "receiverKeyId", 6
                )
                encryptedSharedKey = self.client.checkAndGetValue(
                    E2EEGroupSharedKey, "encryptedSharedKey", 7
                )
                if not isinstance(encryptedSharedKey, bytes):
                    raise ValueError(
                        f"encryptedSharedKey should be bytes. (E2EEGroupSharedKey: {E2EEGroupSharedKey})"
                    )
                selfKeyData = self.client.getE2EESelfKeyDataByKeyId(receiverKeyId)
                if selfKeyData is None:
                    raise ValueError(
                        f"E2EE Self Key Data is None. (receiverKeyId: {receiverKeyId})"
                    )
                selfKey = base64.b64decode(selfKeyData["privKey"])
                creatorKey = self.getE2EELocalPublicKey(creator, creatorKeyId)
                aesKey = self.generateSharedSecret(selfKey, creatorKey)
                aes_key = self.getSHA256Sum(aesKey, b"Key")
                aes_iv = self._xor(self.getSHA256Sum(aesKey, b"IV"))
                aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
                try:
                    decrypted = unpad(aes.decrypt(encryptedSharedKey), 16)
                except ValueError:
                    decrypted = aes.decrypt(encryptedSharedKey)
                self.__logger.debug(f"[getE2EELocalPublicKey] decrypted: {decrypted}")
                data = {
                    "privKey": base64.b64encode(decrypted).decode(),
                    "keyId": groupKeyId,
                }
                key = json.dumps(data)
                self.client.saveCacheData(fd, fn, key, False)
            return json.loads(key)
        return base64.b64decode(key)

    def generateSharedSecret(self, private_key, public_key):
        return Curve25519.calculateAgreement(bytes(private_key), bytes(public_key))

    def tryRegisterE2EEGroupKey(self, group_mid: str):
        E2EEPublicKeys = self.client.getLastE2EEPublicKeys(group_mid)
        if not isinstance(E2EEPublicKeys, dict):
            raise ValueError(
                f"E2EEPublicKeys should be list. (E2EEPublicKeys: {E2EEPublicKeys})"
            )
        members = []
        keyIds = []
        encryptedSharedKeys = []
        selfKeyId = [
            self.client.checkAndGetValue(E2EEPublicKeys[key], "keyId", 2)
            for key in E2EEPublicKeys
            if key == self.client.mid
        ][0]
        selfKeyData = self.client.getE2EESelfKeyDataByKeyId(selfKeyId)
        if selfKeyData is None:
            raise ValueError(f"E2EE Self Key Data is None. (selfKeyId: {selfKeyId})")
        selfKey = base64.b64decode(selfKeyData["privKey"])
        private_key = Curve25519.generatePrivateKey(bytes(32))  # ios patch
        # you can use bytes(32) for LINE Android & PC ver. but it will failed to decrypt on iOS & ChromeOS
        for key_mid in E2EEPublicKeys:
            members.append(key_mid)
            key = E2EEPublicKeys[key_mid]
            keyId = self.client.checkAndGetValue(key, "keyId", 2)
            keyData = self.client.checkAndGetValue(key, "keyData", 4)
            keyIds.append(keyId)
            aesKey = self.generateSharedSecret(selfKey, keyData)
            aes_key = self.getSHA256Sum(aesKey, b"Key")
            aes_iv = self._xor(self.getSHA256Sum(aesKey, b"IV"))
            aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
            encryptedSharedKey = aes.encrypt(pad(private_key, 16))
            encryptedSharedKeys.append(encryptedSharedKey)
        E2EEGroupSharedKey = self.client.registerE2EEGroupKey(
            1, group_mid, members, keyIds, encryptedSharedKeys
        )
        self.__logger.info(f"E2EE key register on {group_mid}: {E2EEGroupSharedKey}")
        return E2EEGroupSharedKey

    def _xor(self, buf):
        buf_length = int(len(buf) / 2)
        buf2 = bytearray(buf_length)
        for i in range(buf_length):
            buf2[i] = buf[i] ^ buf[buf_length + i]
        return bytes(buf2)

    def getSHA256Sum(self, *args):
        instance = hashlib.sha256()
        for arg in args:
            if isinstance(arg, str):
                arg = arg.encode()
            instance.update(arg)
        return instance.digest()

    def _encryptAESECB(self, aes_key, plain_data):
        aes = AES.new(aes_key, AES.MODE_ECB)
        return aes.encrypt(plain_data)

    def _encryptAESCTR(self, aes_key, nonce, data):
        aes = AES.new(aes_key, AES.MODE_CTR, nonce=nonce)
        return aes.encrypt(data)

    def _decryptAESCTR(self, aes_key, nonce, data):
        aes = AES.new(aes_key, AES.MODE_CTR, nonce=nonce)
        return aes.decrypt(data)

    def _decryptAESGCMSIV(
        self, gtg: bytes, nonce: bytes, data: bytes, aad: Optional[bytes] = None
    ):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

        aes = AESGCMSIV(gtg)
        return aes.decrypt(nonce, data, aad)

    def decryptKeyChain(self, publicKey, privateKey, encryptedKeyChain):
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        aes_key = self.getSHA256Sum(shared_secret, "Key")
        aes_iv = self._xor(self.getSHA256Sum(shared_secret, "IV"))
        aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        keychain_data = aes.decrypt(encryptedKeyChain)
        key = keychain_data.hex()
        key = bin2bytes(key)
        tc = self.client.TCompactProtocol(self, passProtocol=True)
        tc.data = key
        r: Any = tc.x(False)
        if r is None:
            raise ValueError(f"decryptKeyChain failed: {key}")
        key_data = r[1]
        public_key = bytes(key_data[0][4])
        private_key = bytes(key_data[0][5])
        return [private_key, public_key]

    def encryptDeviceSecret(self, publicKey, privateKey, encryptedKeyChain):
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        aes_key = self.getSHA256Sum(shared_secret, "Key")
        encryptedKeyChain = self._xor(self.getSHA256Sum(encryptedKeyChain))
        keychain_data = self._encryptAESECB(aes_key, encryptedKeyChain)
        return keychain_data

    def generateAAD(self, a, b, c, d, e: Union[str, int] = 2, f=0):
        aad = b""
        aad += a.encode()
        aad += b.encode()
        aad += bytes(self.client.getIntBytes(c))
        aad += bytes(self.client.getIntBytes(d))
        aad += bytes(self.client.getIntBytes(e))  # e2ee version
        aad += bytes(self.client.getIntBytes(f))  # content type
        return aad

    def encryptE2EEMessage(
        self, to, text, specVersion=2, isCompact=False, contentType=0, renewKey=False
    ):
        _from = self.client.mid
        selfKeyData = self.client.getE2EESelfKeyDataByKeyId(self.__e2ee_key_id)
        if selfKeyData is None:
            raise ValueError(f"E2EE Self Key Data is None. (id: {self.__e2ee_key_id})")
        if len(to) == 0 or self.client.getToType(to) not in [0, 1, 2]:
            raise Exception("Invalid mid")
        senderKeyId = selfKeyData["keyId"]
        if self.client.getToType(to) == 0:
            private_key = base64.b64decode(selfKeyData["privKey"])
            receiver_key_data = self.getE2EELocalPublicKey(to, None, renewKey)
            specVersion = self.client.checkAndGetValue(
                receiver_key_data, "specVersion", 3
            )
            if specVersion == -1:
                raise Exception(f"Not support E2EE on {to}")
            publicKey = self.client.checkAndGetValue(receiver_key_data, "publicKey", 2)
            receiverKeyId = self.client.checkAndGetValue(publicKey, "keyId", 2)
            receiverKeyData = self.client.checkAndGetValue(publicKey, "keyData", 4)
            keyData = self.generateSharedSecret(bytes(private_key), receiverKeyData)
        else:
            groupK: Any = self.getE2EELocalPublicKey(to, None, renewKey)
            privK = base64.b64decode(groupK["privKey"])
            pubK = base64.b64decode(selfKeyData["pubKey"])
            receiverKeyId = groupK["keyId"]
            keyData = self.generateSharedSecret(privK, pubK)
        if contentType == 15:
            chunks = self.encryptE2EELocationMessage(
                senderKeyId,
                receiverKeyId,
                keyData,
                specVersion,
                text,
                to,
                _from,
                isCompact=isCompact,
            )
        else:
            e2ee_enc = self.encryptE2EETextMessage
            if isinstance(text, dict):
                e2ee_enc = self.encryptE2EEMessageByData
            chunks = e2ee_enc(
                senderKeyId,
                receiverKeyId,
                keyData,
                specVersion,
                text,
                to,
                _from,
                isCompact=isCompact,
                contentType=contentType,
            )
        return chunks

    def encryptE2EETextMessage(
        self,
        senderKeyId,
        receiverKeyId,
        keyData,
        specVersion,
        text,
        to,
        _from,
        isCompact=False,
        contentType=0,
    ):
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b"Key")
        aad = self.generateAAD(
            to, _from, senderKeyId, receiverKeyId, specVersion, contentType
        )
        sign = os.urandom(16)
        data = json.dumps({"text": text}).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        bSenderKeyId = bytes(self.client.getIntBytes(senderKeyId))
        bReceiverKeyId = bytes(self.client.getIntBytes(receiverKeyId))
        if isCompact:
            compact = self.client.TCompactProtocol(self)
            bSenderKeyId = bytes(compact.writeI32(int(senderKeyId)))
            bReceiverKeyId = bytes(compact.writeI32(int(receiverKeyId)))
        self.__logger.debug(f"senderKeyId: {senderKeyId} ({bSenderKeyId})")
        self.__logger.debug(f"receiverKeyId: {receiverKeyId} ({bReceiverKeyId})")
        return [salt, encData, sign, bSenderKeyId, bReceiverKeyId]

    def encryptE2EELocationMessage(
        self,
        senderKeyId,
        receiverKeyId,
        keyData,
        specVersion,
        location,
        to,
        _from,
        isCompact=False,
    ):
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b"Key")
        aad = self.generateAAD(to, _from, senderKeyId, receiverKeyId, specVersion, 15)
        sign = os.urandom(16)
        data = json.dumps({"location": location}).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        bSenderKeyId = bytes(self.client.getIntBytes(senderKeyId))
        bReceiverKeyId = bytes(self.client.getIntBytes(receiverKeyId))
        if isCompact:
            compact = self.client.TCompactProtocol(self)
            bSenderKeyId = bytes(compact.writeI32(int(senderKeyId)))
            bReceiverKeyId = bytes(compact.writeI32(int(receiverKeyId)))
        self.__logger.debug(f"senderKeyId: {senderKeyId} ({bSenderKeyId})")
        self.__logger.debug(f"receiverKeyId: {receiverKeyId} ({bReceiverKeyId})")
        return [salt, encData, sign, bSenderKeyId, bReceiverKeyId]

    def encryptE2EEMessageByData(
        self,
        senderKeyId,
        receiverKeyId,
        keyData,
        specVersion,
        dict_data,
        to,
        _from,
        isCompact=False,
        contentType=0,
    ):
        salt = os.urandom(16)
        gcmKey = self.getSHA256Sum(keyData, salt, b"Key")
        aad = self.generateAAD(
            to, _from, senderKeyId, receiverKeyId, specVersion, contentType
        )
        sign = os.urandom(16)
        data = json.dumps(dict_data).encode()
        encData = self.encryptE2EEMessageV2(data, gcmKey, sign, aad)
        bSenderKeyId = bytes(self.client.getIntBytes(senderKeyId))
        bReceiverKeyId = bytes(self.client.getIntBytes(receiverKeyId))
        if isCompact:
            compact = self.client.TCompactProtocol(self)
            bSenderKeyId = bytes(compact.writeI32(int(senderKeyId)))
            bReceiverKeyId = bytes(compact.writeI32(int(receiverKeyId)))
        self.__logger.debug(f"senderKeyId: {senderKeyId} ({bSenderKeyId})")
        self.__logger.debug(f"receiverKeyId: {receiverKeyId} ({bReceiverKeyId})")
        return [salt, encData, sign, bSenderKeyId, bReceiverKeyId]

    def encryptE2EEMessageV2(self, data, gcmKey, nonce, aad):
        aesgcm = AESGCM(gcmKey)
        return aesgcm.encrypt(nonce, data, aad)

    def decryptE2EETextMessage(self, messageObj, isSelf=True):
        return self.decryptE2EEMessage(messageObj, isSelf).get("text", "")

    def decryptE2EELocationMessage(self, messageObj, isSelf=True):
        return self.decryptE2EEMessage(messageObj, isSelf).get("location", None)

    def decryptE2EEMessage(self, messageObj, isSelf=True) -> dict:
        _from = messageObj.sender.mid
        to = messageObj.receiver.mid
        if _from is None or to is None:
            raise ValueError
        toType = self.client.checkAndGetValue(messageObj, "toType", 3)
        metadata = self.client.checkAndGetValue(messageObj, "contentMetadata", 18)
        if metadata is None:
            metadata = {}
        specVersion: str = metadata.get("e2eeVersion", "2")
        contentType = self.client.checkAndGetValue(messageObj, "contentType", 15)
        if contentType is None:
            raise ValueError("contentType should not be None.", contentType)
        chunks = self.client.checkAndGetValue(messageObj, "chunks", 20)
        if chunks is None:
            raise ValueError("chunks should not be None.")
        for i in range(len(chunks)):
            if isinstance(chunks[i], str):
                chunks[i] = chunks[i].encode()
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])
        self.__logger.debug(f"senderKeyId: {senderKeyId}")
        self.__logger.debug(f"receiverKeyId: {receiverKeyId}")

        selfKey = self.client.getE2EESelfKeyData(self.client.mid)
        privK = base64.b64decode(selfKey["privKey"])
        if toType == 0:
            # patch to use correct key by id
            selfKey = self.client.getE2EESelfKeyDataByKeyId(receiverKeyId)
            if selfKey is None:
                raise ValueError(f"selfKey should not be None. KeyId={receiverKeyId}")
            privK = base64.b64decode(selfKey["privKey"])
            pubK = self.getE2EELocalPublicKey(_from, senderKeyId)
        else:
            selfKey = self.client.getE2EESelfKeyDataByKeyId(self.__e2ee_key_id)
            if selfKey is None:
                raise ValueError(f"selfKey should not be None. KeyId={receiverKeyId}")
            groupK: Any = self.getE2EELocalPublicKey(to, receiverKeyId)
            privK = base64.b64decode(groupK["privKey"])
            pubK = base64.b64decode(selfKey["pubKey"])
            if _from != self.client.mid:
                pubK = self.getE2EELocalPublicKey(_from, senderKeyId)

        if specVersion == "2":
            decrypted = self.decryptE2EEMessageV2(
                messageObj[2],
                messageObj[1],
                chunks,
                privK,
                pubK,
                specVersion,
                contentType,
            )
        else:
            decrypted = self.decryptE2EEMessageV1(chunks, privK, pubK)
        return decrypted

    def decryptE2EEMessageV1(self, chunks, privK, pubK):
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        aesKey = self.generateSharedSecret(privK, pubK)
        aes_key = self.getSHA256Sum(aesKey, salt, b"Key")
        aes_iv = self._xor(self.getSHA256Sum(aesKey, salt, "IV"))
        aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        decrypted = aes.decrypt(message)
        self.__logger.debug(f"decrypted: {decrypted}")
        decrypted = unpad(decrypted, 16)
        return json.loads(decrypted)

    def decryptE2EEMessageV2(
        self,
        to,
        _from,
        chunks,
        privK,
        pubK,
        specVersion: Union[str, int] = 2,
        contentType=0,
    ):
        salt = chunks[0]
        message = chunks[1]
        sign = chunks[2]
        senderKeyId = byte2int(chunks[3])
        receiverKeyId = byte2int(chunks[4])

        aesKey = self.generateSharedSecret(privK, pubK)
        gcmKey = self.getSHA256Sum(aesKey, salt, b"Key")
        _senderKeyId = senderKeyId
        _receiverKeyId = receiverKeyId
        to2 = to
        _from2 = _from
        aad = self.generateAAD(
            to2, _from2, _senderKeyId, _receiverKeyId, specVersion, contentType
        )

        aesgcm = AESGCM(gcmKey)
        decrypted = aesgcm.decrypt(sign, message, aad)
        self.__logger.debug(f"decrypted: {decrypted}")
        return json.loads(decrypted)

    def sign_data(self, data: bytes, key: bytes):
        """Sign data by SHA256."""
        hmac_key = hmac.HMAC(key, hashes.SHA256())
        hmac_key.update(data)
        return hmac_key.finalize()

    def deriveKeyMaterial(self, key_material: bytes):
        """Derive key material for file encryption."""
        # 使用私鑰導入
        t = HKDF(
            algorithm=hashes.SHA256(),
            length=32 + 32 + 12,
            salt=None,
            info=b"FileEncryption",
        ).derive(key_material)

        return {"encKey": t[:32], "macKey": t[32:64], "nonce": t[64:]}

    def encryptByKeyMaterial(self, raw_data: Any, keyMateria: Optional[bytes] = None):
        """Encrypt file for E2EE Next."""
        if keyMateria is None:
            keyMateria = secrets.token_bytes(32)
        keys = self.deriveKeyMaterial(keyMateria)
        enc_data = self._encryptAESCTR(keys["encKey"], keys["nonce"], raw_data)
        sign = self.sign_data(enc_data, keys["macKey"])
        return base64.b64encode(keyMateria).decode(), enc_data + sign

    def decryptByKeyMaterial(self, raw_data: Any, keyMateria: Union[bytes, str]):
        """Decrypt file for E2EE Next."""
        if isinstance(keyMateria, str):
            keyMateria = base64.b64decode(keyMateria)
        keys = self.deriveKeyMaterial(keyMateria)
        return self._decryptAESCTR(keys["encKey"], keys["nonce"], raw_data)

    def decryptEncryptedQrIdentifier(
        self, encryptedQrIdentifier: bytes, privateKey: bytes, publicKey: bytes
    ):
        """Decrypt encrypted qr identifier."""
        shared_secret = self.generateSharedSecret(privateKey, publicKey)
        nonce_size = 12
        return self._decryptAESGCMSIV(
            shared_secret,
            encryptedQrIdentifier[:nonce_size],
            encryptedQrIdentifier[nonce_size:],
        )


def byte2int(t):
    e = 0
    i = 0
    s = len(t)
    for i in range(s):
        e = 256 * e + t[i]
    return e


def bin2bytes(k):
    e = []
    for i in range(int(len(k) / 2)):
        _i = int(k[i * 2 : i * 2 + 2], 16)
        e.append(_i)
    return bytearray(e)
