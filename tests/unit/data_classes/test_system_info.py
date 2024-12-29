from datetime import datetime
from typing import Final

import pytest
from voluptuous import MultipleInvalid

from apyefa.data_classes import SystemInfo

DATA: Final = {
    "version": "10.6.14.22",
    "ptKernel": {
        "appVersion": "10.4.30.6 build 16.09.2024 01:30:57",
        "dataFormat": "EFA10_04_00",
        "dataBuild": "2024-11-28T16:54:20Z",
    },
    "validity": {"from": "2024-11-01", "to": "2025-12-13"},
}


@pytest.mark.parametrize("data", [None, ""])
def test_no_data(data):
    assert not SystemInfo.from_dict(data)


@pytest.mark.parametrize("data", [1, True, "test"])
def test_invalid_data_type(data):
    with pytest.raises(ValueError):
        SystemInfo.from_dict(data)


def test_invalid_data_content():
    with pytest.raises(MultipleInvalid):
        SystemInfo.from_dict({"wrong": "data"})


def test_from_dict():
    info = SystemInfo.from_dict(DATA)
    assert info.version == "10.6.14.22"
    assert info.app_version == "10.4.30.6 build 16.09.2024 01:30:57"
    assert info.data_format == "EFA10_04_00"
    assert info.data_build == "2024-11-28T16:54:20Z"
    assert info.valid_from == datetime(2024, 11, 1).date()
    assert info.valid_to == datetime(2025, 12, 13).date()


def test_to_dict():
    info = SystemInfo.from_dict(DATA)

    assert DATA == info.to_dict()
