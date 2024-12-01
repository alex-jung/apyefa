import pytest

from apyefa.commands.command_stop_finder import CommandStopFinder
from apyefa.exceptions import EfaParameterError, EfaResponseInvalid


@pytest.fixture
def command():
    return CommandStopFinder("my_type", "my_name")


def test_init_name_and_macro(command):
    assert command._name == "XML_STOPFINDER_REQUEST"
    assert command._macro == "stopfinder"


def test_init_params(command):
    assert command._parameters.get("type_sf") == "my_type"
    assert command._parameters.get("name_sf") == "my_name"


@pytest.mark.parametrize(
    "isGlobalId, expected_id", [(True, "global_id"), (False, "stop_id_1")]
)
def test_parse_success(isGlobalId, expected_id, command):
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

    info = command.parse(data)

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
