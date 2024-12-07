from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_system_info import CommandSystemInfo
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_SYSTEMINFO_REQUEST"
MACRO: Final = "system"


@pytest.fixture(scope="module")
def command():
    return CommandSystemInfo()


# test constructor
def test_init_name_and_macro(command):
    assert command._name == NAME
    assert command._macro == MACRO


def test_init_parameters(command):
    expected_params = {"outputFormat": "rapidJSON", "coordOutputFormat": "WGS84"}

    assert command._parameters == expected_params


# test 'add_param()'
@pytest.mark.parametrize(
    "param, value",
    [("outputFormat", "rapidJSON")],
)
def test_add_param_success(command, param, value):
    command.add_param(param, value)


@pytest.mark.parametrize("param, value", [("param", "value"), ("name_sf", "my_name")])
def test_add_param_failed(command, param, value):
    with pytest.raises(EfaParameterError):
        command.add_param(param, value)


# test 'to_str() and __str()__'
def test_to_str(command):
    expected_str = (
        f"{NAME}?commonMacro={MACRO}&outputFormat=rapidJSON&coordOutputFormat=WGS84"
    )

    assert command.to_str() == expected_str and str(command) == expected_str


# test 'parse()'
def test_parse_success(command):
    with patch.object(RapidJsonParser, "parse") as parse_mock:
        parse_mock.return_value = {}

        command.parse("this is a test response")

    parse_mock.assert_called_once()


def test_parse_failed(command):
    with patch.object(RapidJsonParser, "parse") as parse_mock:
        parse_mock.side_effect = EfaParseError

        with pytest.raises(EfaParseError):
            command.parse("this is a test response")

    parse_mock.assert_called_once()
