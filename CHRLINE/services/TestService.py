# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol


class TestService(ChrHelperProtocol):

    def __init__(self):
        pass

    def testRequest(
        self,
        m_name: str,
        m_args: list,
        api_path: str,
        req_thrift_type: int = 3,
        res_thrift_type: int = 3,
    ):
        """
        Test request.

        - m_name:
            func name, eg. fetchOps
        - m_args:
            func args for DummyProtocol, eg:
            [
                [12, 1, [
                    [11, 1, 'im string']
                ]]
            ]
        - api_path:
            request path, eg. /C5
        """
        params = m_args
        sqrd = self.client.generateDummyProtocol(m_name, params, req_thrift_type)
        return self.client.postPackDataAndGetUnpackRespData(
            api_path, sqrd, res_thrift_type
        )
