import pytest

from apyefa.exceptions import EfaParameterError, EfaResponseInvalid
from apyefa.requests.req_stop_finder import StopFinderRequest


def test_init_name_and_macro():
    req = StopFinderRequest("my_type", "my_name")

    assert req._name == "XML_STOPFINDER_REQUEST"
    assert req._macro == "stopfinder"


def test_init_params():
    req = StopFinderRequest("my_type", "my_name")

    assert req._parameters.get("type_sf") == "my_type"
    assert req._parameters.get("name_sf") == "my_name"


@pytest.mark.parametrize(
    "isGlobalId, expected_id", [(True, "global_id"), (False, "stop_id_1")]
)
def test_parse_success(isGlobalId, expected_id):
    req = StopFinderRequest("my_type", "my_name")

    data = {
        "version": "version",
        "locations": [
            {
                "id": "global_id",
                "isGlobalId": isGlobalId,
                "name": "my location name",
                "properties": {"stopId": "stop_id_1"},
                "disassembledName": "disassembled name",
                "coord": [],
                "type": "stop",
                "productClasses": [1, 2, 3],
                "matchQuality": 0,
            }
        ],
    }

    info = req.parse(data)

    assert len(info) == 1
    assert info[0].id == expected_id


@pytest.mark.parametrize(
    "data", [{"locations": None}, {"locations": "value"}, {"locations": 123}]
)
def test_parse_failed(data):
    req = StopFinderRequest("my_type", "my_name")

    with pytest.raises(EfaResponseInvalid):
        req.parse(data)


@pytest.mark.parametrize("value", ["any", "coord"])
def test_add_valid_param(value):
    req = StopFinderRequest("my_type", "my_name")

    req.add_param("type_sf", value)

    # no exceptions occured


@pytest.mark.parametrize("invalid_param", ["dummy", "STOP"])
def test_add_invalid_param(invalid_param):
    req = StopFinderRequest("my_type", "my_name")

    with pytest.raises(EfaParameterError):
        req.add_param(invalid_param, "valid_value")
