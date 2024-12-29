from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_departures import CommandDepartures
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_DM_REQUEST"


@pytest.fixture
def command():
    return CommandDepartures("rapidJSON")


def test_init_name(command):
    assert command._name == NAME


def test_init_params(command):
    expected_params = {
        "outputFormat": "rapidJSON",
    }

    assert command._parameters == expected_params


def test_parse_success(command):
    data = {
        "version": "version",
        "stopEvents": [
            {
                "location": {
                    "id": "de:09564:510:11:U1_2",
                    "name": "Nürnberg Hbf",
                    "disassembledName": "Bstg. 1",
                    "type": "platform",
                    "pointType": "PLATFORM",
                    "coord": [49.446386, 11.081653],
                    "properties": {
                        "stopId": "80001020",
                        "area": "20",
                        "platform": "1",
                        "platformName": "Bstg. 1",
                        "plannedPlatformName": "Bstg. 1",
                    },
                    "parent": {
                        "id": "de:09564:510",
                        "isGlobalId": True,
                        "name": "Nürnberg Hbf",
                        "type": "stop",
                        "parent": {"name": "Nürnberg", "type": "locality"},
                        "properties": {"stopId": "80001020"},
                    },
                },
                "departureTimePlanned": "2024-12-21T14:00:00Z",
                "departureTimeBaseTimetable": "2024-12-21T14:00:06Z",
                "departureTimeEstimated": "2024-12-21T14:00:00Z",
                "transportation": {
                    "id": "van:01001: :H:j25",
                    "name": "U-Bahn U1",
                    "disassembledName": "U1",
                    "number": "U1",
                    "description": "Fürth Hardhöhe-Nürnberg Langwasser Süd",
                    "product": {"id": 1, "class": 2, "name": "U-Bahn", "iconId": 1},
                    "destination": {
                        "id": "3001507",
                        "name": "Langwasser Süd",
                        "type": "stop",
                    },
                    "properties": {
                        "trainType": "ICE",
                        "tripCode": 2750,
                        "lineDisplay": "LINE",
                        "globalId": "de:vgn:402_U1:0",
                    },
                    "origin": {
                        "id": "3000703",
                        "name": "Nürnberg Gostenhof",
                        "type": "stop",
                    },
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


@pytest.mark.parametrize("value", ["any", "stop"])
def test_validate_success(value, command):
    # add required params
    command.add_param("name_dm", "dummy name")

    # param to test
    command.add_param("type_dm", value)
    command.validate_params()


@pytest.mark.parametrize("invalid_param", ["dummy", "STOP"])
def test_validate_failed(invalid_param, command):
    command.add_param(invalid_param, "valid_value")

    with pytest.raises(EfaParameterError):
        command.validate_params()
