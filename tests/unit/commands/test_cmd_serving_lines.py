from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_serving_lines import CommandServingLines
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_SERVINGLINES_REQUEST"


@pytest.fixture
def command():
    return CommandServingLines("rapidJSON")


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


@pytest.mark.parametrize("param, value", [("param", "value"), ("name", "my_name")])
def test_add_param_failed(command, param, value):
    with pytest.raises(EfaParameterError):
        command.add_param(param, value)


def test_parse_success(command):
    data = {
        "version": "version",
        "lines": [
            {
                "id": "van:02067: :H:j24",
                "name": "Bus 67",
                "number": "67",
                "description": "Nürnberg Frankenstr.-Fürth Hauptbahnhof",
                "product": {"id": 3, "class": 5, "name": "Bus", "iconId": 3},
                "destination": {
                    "id": "80000931",
                    "name": "Fürth Hauptbahnhof",
                    "type": "stop",
                },
                "properties": {
                    "tripCode": 0,
                    "timetablePeriod": "Jahresfahrplan 2024",
                    "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                    "lineDisplay": "LINE",
                },
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