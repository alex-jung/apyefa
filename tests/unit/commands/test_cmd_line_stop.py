from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_line_stop import CommandLineStop
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_LINESTOP_REQUEST"


@pytest.fixture
def command():
    return CommandLineStop("rapidJSON")


def test_init_name(command):
    assert command._name == NAME


def test_init_params(command):
    expected_params = {
        "outputFormat": "rapidJSON",
    }

    assert command._parameters == expected_params
    assert str(command) == f"{NAME}?outputFormat=rapidJSON"


# test 'add_param()'
@pytest.mark.parametrize(
    "param, value",
    [
        ("line", "my line"),
        ("allStopInfo", 1),
    ],
)
def test_validate_success(command, param, value):
    command.add_param(param, value)
    command.validate_params()


@pytest.mark.parametrize("param, value", [("param", "value"), ("name", "my_name")])
def test_validate_failed(command, param, value):
    command.add_param(param, value)

    with pytest.raises(EfaParameterError):
        command.validate_params()


def test_parse_success(command):
    data = {
        "version": "version",
        "locationSequence": [
            {
                "isGlobalId": True,
                "id": "de:09576:8000",
                "name": "Roth",
                "type": "stop",
                "parent": {
                    "id": "placeID:9576143:1",
                    "name": "Roth (Mittelfr)",
                    "type": "locality",
                },
                "properties": {"stopId": "80001085"},
            },
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
