from typing import Final

import pytest

from apyefa.commands.command_serving_lines import CommandServingLines
from apyefa.exceptions import EfaParameterError

NAME: Final = "XML_SERVINGLINES_REQUEST"
MACRO: Final = "servingLines"


@pytest.fixture(scope="module")
def query_url():
    return f"https://efa.vgn.de/vgnExt_oeffi/{NAME}?commonMacro={MACRO}&outputFormat=rapidJSON&type_sl=stopID&name_sl=de:09564:1976&mode=odv"


@pytest.fixture
def command():
    return CommandServingLines("odv", "my_name")


def test_init_name_and_macro(command):
    assert command._name == NAME
    assert command._macro == MACRO


def test_init_params_mode_odv():
    cmd = CommandServingLines("odv", "my_value")

    expected_params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "WGS84",
        "mode": "odv",
        "name_sl": "my_value",
        "type_sl": "stopID",
    }

    assert cmd._parameters == expected_params


def test_init_params_mode_line():
    cmd = CommandServingLines("line", "my_value")

    expected_params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "WGS84",
        "mode": "line",
        "lineName": "my_value",
    }

    assert cmd._parameters == expected_params


def test_init_params_mode_unknown():
    with pytest.raises(ValueError):
        CommandServingLines("invalid", "my_value")


# test 'add_param()'
@pytest.mark.parametrize(
    "param",
    [
        "outputFormat",
        "mode",
        "type_sl",
        "name_sl",
        "lineName",
        "lineReqType",
        "mergeDir",
        "lsShowTrainsExplicit",
        "line",
    ],
)
def test_add_param_success(command, param):
    command.add_param(param, "any_value")


def test_parse_success(command, run_query):
    transportations = command.parse(run_query)

    assert len(transportations) > 0


@pytest.mark.parametrize("param, value", [("param", "value"), ("name", "my_name")])
def test_add_param_failed(command, param, value):
    with pytest.raises(EfaParameterError):
        command.add_param(param, value)


# test 'to_str() and __str()__'
def test_to_str(command):
    expected_str = f"{NAME}?commonMacro={MACRO}&outputFormat=rapidJSON&coordOutputFormat=WGS84&type_sl=stopID&name_sl=my_name&mode=odv"

    assert command.to_str() == expected_str and str(command) == expected_str
