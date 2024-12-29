from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_system_info import CommandSystemInfo
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_SYSTEMINFO_REQUEST"


@pytest.fixture()
def command():
    return CommandSystemInfo("rapidJSON")


# test constructor
def test_init_name(command):
    assert command._name == NAME


def test_init_parameters(command):
    assert command._parameters == {"outputFormat": "rapidJSON"}


# test 'add_param()'
@pytest.mark.parametrize(
    "param, value",
    [("outputFormat", "rapidJSON")],
)
def test_add_param_success(command, param, value):
    command.add_param(param, value)
    command.validate_params()  # no exception occured


@pytest.mark.parametrize("param, value", [("param", "value"), ("name_sf", "my_name")])
def test_validate_failed(command, param, value):
    command.add_param(param, value)

    with pytest.raises(EfaParameterError):
        command.validate_params()


# test '__str()__'
def test_to_str(command):
    assert str(command) == f"{NAME}?outputFormat=rapidJSON"


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
