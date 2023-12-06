import os

from tvl.api.l2_api import TsL2MutableFwEraseReqRequest
from tvl.constants import L2StatusEnum
from tvl.host.host import Host

from ..base_test import BaseTest


class TestMutableFwEraseReq(BaseTest):
    def test_mutable_fw_erase_req(self, host: Host):
        response = host.send_request(
            TsL2MutableFwEraseReqRequest(bank_id=os.urandom(1))
        )
        assert response.status.value == L2StatusEnum.UNKNOWN_REQ
