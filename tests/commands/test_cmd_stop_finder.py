from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_stop_finder import CommandStopFinder
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_STOPFINDER_REQUEST"


@pytest.fixture
def command():
    yield CommandStopFinder("rapidJSON")


def test_init_name_and_macro(command):
    assert command._name == NAME


def test_init_params(command):
    assert command._parameters == {"outputFormat": "rapidJSON"}


# test 'add_param()'
@pytest.mark.parametrize(
    "param, value",
    [("outputFormat", "rapidJSON"), ("name_sf", "my_value"), ("type_sf", "my_type")],
)
def test_add_param_success(command, param, value):
    command.add_param(param, value)


@pytest.mark.parametrize("param, value", [("param", "value"), ("name", "my_name")])
def test_add_param_failed(command, param, value):
    with pytest.raises(EfaParameterError):
        command.add_param(param, value)


# test '__str()__'
def test_to_str():
    command = CommandStopFinder("rapidJSON")
    assert str(command) == f"{NAME}?outputFormat=rapidJSON"

    command = CommandStopFinder("rapidJSON")
    command.add_param("coordOutputFormat", "WGS84[dd.ddddd]")

    assert (
        str(command)
        == f"{NAME}?outputFormat=rapidJSON&coordOutputFormat=WGS84[dd.ddddd]"
    )


def test_parse_success(command):
    data = {
        "version": "version",
        "locations": [
            {
                "id": "global_id",
                "isGlobalId": True,
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

    with patch.object(RapidJsonParser, "parse") as parse_mock:
        parse_mock.return_value = data
        result = command.parse(data)

    assert len(result) == 1


def test_parse_failed(command):
    with patch.object(RapidJsonParser, "parse") as parse_mock:
        parse_mock.side_effect = EfaParseError

        with pytest.raises(EfaParseError):
            command.parse("this is a test response")
