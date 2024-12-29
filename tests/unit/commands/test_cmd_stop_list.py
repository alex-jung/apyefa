from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_stop_list import CommandStopList
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_STOPLIST_REQUEST"


@pytest.fixture
def command():
    return CommandStopList("rapidJSON")


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
        ("stopListOMC", "08111000"),
        ("stopListPlaceId", "de:08111:2"),
        ("stopListOMCPlaceId", "de:08111:2"),
        ("rTN", "de:08111:2"),
        ("stopListSubnetwork", "sub"),
        ("fromstop", "de:08111:2"),
        ("tostop", "de:08111:2"),
        ("servingLines", "1"),
        ("servingLinesMOTType", "1"),
        ("servingLinesMOTTypes", "1"),
        ("tariffZones", "0"),
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
        "locations": [
            {
                "isGlobalId": True,
                "id": "de:08111:2",
                "name": "Waldburgstraße",
                "type": "stop",
                "parent": {
                    "id": "51",
                    "name": "Stuttgart",
                    "type": "locality",
                    "properties": {"omc": "8111000"},
                },
                "properties": {"stopId": "5000002"},
                "coord": [48.725457, 9.107399],
                "transportations": [
                    {
                        "id": "vvs:30081: :R:j25",
                        "name": "Bus 81",
                        "disassembledName": "81",
                        "number": "81",
                        "description": "Dürrlewang - Vaihingen - Büsnau",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5002590",
                            "name": "Büsnauer Platz",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30081_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:30081: :H:j25",
                        "name": "Bus 81",
                        "disassembledName": "81",
                        "number": "81",
                        "description": "Büsnau - Vaihingen - Dürrlewang",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5002614",
                            "name": "Lambertweg",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30081_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:30082: :H:j25",
                        "name": "Bus 82",
                        "disassembledName": "82",
                        "number": "82",
                        "description": "Waldeck - Vaihingen - Hans-Rehn-Stift - Rohr Mitte (- Leinfelden Bf)",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5006014",
                            "name": "Rohr Mitte",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30082_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:30082: :R:j25",
                        "name": "Bus 82",
                        "disassembledName": "82",
                        "number": "82",
                        "description": "(Leinfelden Bf -) Rohr Mitte - Hans-Rehn-Stift - Vaihingen - Waldeck",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5006010",
                            "name": "Waldeck",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30082_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:30086: :H:j25",
                        "name": "Bus 86",
                        "disassembledName": "86",
                        "number": "86",
                        "description": "Vaihingen - Rohr Mitte - Leinfelden",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5000175",
                            "name": "Leinfelden",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30086_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:30086: :R:j25",
                        "name": "Bus 86",
                        "disassembledName": "86",
                        "number": "86",
                        "description": "Leinfelden - Rohr Mitte - Vaihingen",
                        "product": {"id": 5, "class": 5, "name": "Bus", "iconId": 3},
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5006002",
                            "name": "Vaihingen",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:30086_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                    {
                        "id": "vvs:33010: :H:j25",
                        "name": "Nachtbus N10",
                        "disassembledName": "N10",
                        "number": "N10",
                        "description": "Schlossplatz - Rohrer Höhe  - Schlossplatz",
                        "product": {
                            "id": 6,
                            "class": 5,
                            "name": "Nachtbus",
                            "iconId": 3,
                        },
                        "operator": {"id": "01", "name": "SSB"},
                        "destination": {
                            "id": "5006014",
                            "name": "Rohr Mitte",
                            "type": "stop",
                        },
                        "properties": {
                            "tripCode": 0,
                            "timetablePeriod": "Fahrplan 2025",
                            "validity": {"from": "2024-12-01", "to": "2025-06-14"},
                            "lineDisplay": "LINE",
                            "globalId": "de:vvs:33010_:",
                            "OperatorURL": "www.ssb-ag.de/kontakt",
                        },
                    },
                ],
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
