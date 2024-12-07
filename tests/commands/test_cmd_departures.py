from typing import Final

import pytest

from apyefa.commands.command_departures import CommandDepartures
from apyefa.exceptions import EfaParameterError

NAME: Final = "XML_DM_REQUEST"
MACRO: Final = "dm"
STOP_ID_PLAERRER: Final = "de:09564:704"


@pytest.fixture(scope="module")
def query_url():
    return f"https://efa.vgn.de/vgnExt_oeffi/{NAME}?commonMacro={MACRO}&outputFormat=rapidJSON&name_dm={STOP_ID_PLAERRER}&itdTime=2216&itdDate=20241110&mode=direct&type_dm=stop"


@pytest.fixture
def command():
    return CommandDepartures("my_stop")


def test_init_name_and_macro(command):
    assert command._name == NAME
    assert command._macro == MACRO


def test_init_params(command):
    expected_params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "WGS84",
        "name_dm": "my_stop",
    }

    assert command._parameters == expected_params


def test_parse_success(command, run_query):
    departures = command.parse(run_query)

    assert len(departures) > 0


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
