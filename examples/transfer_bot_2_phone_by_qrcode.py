"""
Qrcode migration example.
Line version limit: 12.10.0
Author: YinMo0913
CreatedTime: 2022/09/19
UpdatedTime: 2024/09/13
"""

import base64
import json
import os
import time

import axolotl_curve25519 as curve
import msgpack
from CHRLINE import *
from CHRLINE.hooks import HooksTracer
from Crypto.Cipher import AES
from Crypto.Util import Counter
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class QrMigMgr:

    def __init__(self, ins):
        self.ins = ins
        self.session = None
        self.key = curve.generatePrivateKey(os.urandom(32))
        self.key2 = curve.generatePublicKey(self.key)
        self.qi = None
        self.st = [b"BACKUP_SEED", b"RESTORE_SEED"]
        self.rk = None
        self.bk = None
        self.pks = cl.getAllE2EESelfKey()
        if len(self.pks) == 0:
            cl.registerE2EESelfKey()
            self.pks = cl.getAllE2EESelfKey()

    @property
    def recovery_key(self):
        return [1, self.rk]

    @property
    def blob_payload(self):
        return [1, self.blob_payload_metadata, self.bk]

    @property
    def blob_payload_metadata(self):
        return [[1, pk["keyId"]] for pk in self.pks] + [[2]]

    @property
    def e2ee_keys(self):
        r = []
        for pk in self.pks:
            r.append(
                json.dumps(
                    {
                        "encoded_private_key": base64.b64decode(pk["privKey"])
                        .hex()
                        .upper(),
                        "encoded_public_key": base64.b64decode(pk["pubKey"])
                        .hex()
                        .upper(),
                        "created_time": pk["createdTime"],
                        "version": pk["e2eeVersion"],
                    }
                ).encode()
            )
        return r + [""]

    def create_session(self):
        self.session = self.ins.createQRMigrationSession()[1]
        self.qi = os.urandom(32)
        qr_text = json.dumps(
            {"si": self.session, "qi": self.qi.hex(), "pk": self.key2.hex()}
        )
        qr_img_path = self.ins.genQrcodeImageAndPrint(qr_text)
        print(f"QrCode image in {qr_img_path}")

    def send_key(self, ins, op):
        a1, a2, a3 = range(10, 13)
        key = bytes.fromhex(op[a1])
        qi = bytes.fromhex(op[a2])
        qi = self.ins.decryptEncryptedQrIdentifier(qi, self.key, key)
        m = None
        n = 16
        if qi != self.qi:
            raise ValueError(f"check failed: qi -> {qi} ({op[11]})")

        sk = self.ins.generateSharedSecret(self.key, key)
        t = self._HKDF(sk, m, n, n)
        rk = b"\xc3hJ\x00\xa89\xd7\x0eB\xe8\xd1}\xeb\xf0\xf8\xe6"
        self.rk = self._CTR(t[:n], t[n:], rk)

        t2 = self._HKDF(rk, m, n, a3)
        aad = self._pack(self.blob_payload_metadata)
        bks = self._pack(self.e2ee_keys)
        self.bk = self._GCM(t2[:n], t2[n:], bks, aad)

        recovery_key = self._pack(self.recovery_key)
        blob_payload = self._pack(self.blob_payload)

        time.sleep(2)
        self.ins.sendEncryptedE2EEKey(self.session, recovery_key, blob_payload)

    def _pack(self, v):
        # NOTE: message pack have old and new encode mode.
        return msgpack.packb(v, strict_types=True, use_bin_type=True)

    def _HKDF(self, k, s, *args):
        return HKDF(
            algorithm=hashes.SHA256(),
            length=sum(args),
            salt=s,
            info=self.st.pop(),
        ).derive(k)

    def _CTR(self, k, i, s):
        ctr = Counter.new(128, initial_value=int.from_bytes(i, byteorder="big"))
        cipher = AES.new(k, AES.MODE_CTR, counter=ctr)
        return cipher.encrypt(s)

    def _GCM(self, k, n, s, a):
        aesgcm = AESGCM(k)
        return aesgcm.encrypt(n, s, a)


if __name__ == "__main__":
    cl = CHRLINE(
        TOKEN,
        device="IOS",
        useThrift=True,
        version="14.14.1",
    )

    mgr = QrMigMgr(cl)
    mgr.create_session()

    tracer = HooksTracer(
        cl,
        prefixes=[""],
    )

    @tracer.Operation(143)
    def recv_pin(self, op, cl):
        mgr.send_key(cl, op)

    tracer.run(
        2,
        **{"initServices": [5]},
    )
