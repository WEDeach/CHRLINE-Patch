# -*- coding: utf-8 -*-
from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class DeviceAttestationService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/api/primary/device-attestation"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "DeviceAttestationService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getAssertionChallenge(self):
        """Get assertion challenge."""
        METHOD_NAME = "getAssertionChallenge"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getAttestationChallenge(self):
        """Get attestation challenge."""
        METHOD_NAME = "getAttestationChallenge"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def verifyAssertion(
        self,
        sessionId: str,
        credentialId: str,
        assertionObject: str,
        clientDataJSON: str,
    ):
        """Verify assertion."""
        METHOD_NAME = "verifyAssertion"
        params = [
            [11, 1, sessionId],
            [11, 2, credentialId],
            [11, 3, assertionObject],
            [11, 4, clientDataJSON],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def verifyAttestation(
        self, sessionId: str, attestationObject: str, clientDataJSON: str
    ):
        """Verify attestation."""
        METHOD_NAME = "verifyAttestation"
        params = [
            [11, 1, sessionId],
            [11, 2, attestationObject],
            [11, 3, clientDataJSON],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
