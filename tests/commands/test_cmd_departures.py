import pytest
import requests

from apyefa.commands.command_departures import CommandDepartures
from apyefa.exceptions import EfaParameterError


@pytest.fixture
def command():
    return CommandDepartures("my_stop")


def run_departures_query():
    r = requests.get(
        "https://efa.vgn.de/vgnExt_oeffi/XML_DM_REQUEST?commonMacro=dm&outputFormat=rapidJSON&name_dm=de:09564:704&limit=3&itdTime=2216&itdDate=20241110&mode=direct&type_dm=stop&useRealtime=1"
    )
    assert r.status_code == 200

    return r.text


def test_init_name_and_macro(command):
    assert command._name == "XML_DM_REQUEST"
    assert command._macro == "dm"


def test_init_params(command):
    assert command._parameters.get("name_dm") == "my_stop"


def test_parse_success(command):
    response = run_departures_query()

    info = command.parse(response)

    assert len(info) > 0


@pytest.mark.parametrize("data", [True, 123])
def test_parse_failed(data, command):
    with pytest.raises(TypeError):
        command.parse(data)


@pytest.mark.parametrize("value", ["any", "coord"])
def test_add_valid_param(value, command):
    command.add_param("type_dm", value)

    # no exceptions occured


@pytest.mark.parametrize("invalid_param", ["dummy", "STOP"])
def test_add_invalid_param(invalid_param, command):
    with pytest.raises(EfaParameterError):
        command.add_param(invalid_param, "valid_value")
