# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os

from tvl.api.l2_api import TsL2MutableFwUpdateReqRequest, TsL2MutableFwUpdateReqResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host


def test_mutable_fw_update_req(host: Host):
    response = host.send_request(
        TsL2MutableFwUpdateReqRequest(
            signature=os.urandom(64),
            hash=os.urandom(32),
            type=os.urandom(4),
            version=os.urandom(4),
        )
    )
    assert isinstance(response, TsL2MutableFwUpdateReqResponse)
    assert response.status.value == L2StatusEnum.REQ_OK
