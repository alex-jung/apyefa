from datetime import datetime

import pytest

from apyefa.data_classes import SystemInfo
from apyefa.exceptions import EfaParameterError, EfaResponseInvalid
from apyefa.requests.req_system_info import SystemInfoRequest


def test_init_name_and_macro():
    req = SystemInfoRequest()

    assert req._name == "XML_SYSTEMINFO_REQUEST"
    assert req._macro == "system"


def test_parse_success():
    req = SystemInfoRequest()

    data = {
        "version": "1.2.3",
        "ptKernel": {
            "dataFormat": "EFA10_04_00",
            "dataBuild": "example",
            "appVersion": "version",
        },
        "validity": {"from": "2024-11-01", "to": "2025-01-01"},
    }

    info = req.parse(data)

    assert isinstance(info, SystemInfo)
    assert info.version == "1.2.3"
    assert info.data_format == "EFA10_04_00"
    assert info.valid_from == datetime(2024, 11, 1).date()
    assert info.valid_to == datetime(2025, 1, 1).date()


@pytest.mark.parametrize("data", [None, {}, {"dummy": "value"}])
def test_parse_failed(data):
    req = SystemInfoRequest()

    with pytest.raises(EfaResponseInvalid):
        req.parse(data)


@pytest.mark.parametrize(
    "param, value",
    [("valid_param", "value"), ("itdDate", "my_name"), ("itdTime", "my_name")],
)
def test_add_valid_params(param, value):
    req = SystemInfoRequest()

    with pytest.raises(EfaParameterError):
        req.add_param(param, value)


@pytest.mark.parametrize("param, value", [("param", "value"), ("name_sf", "my_name")])
def test_add_invalid_params(param, value):
    req = SystemInfoRequest()

    with pytest.raises(EfaParameterError):
        req.add_param(param, value)
