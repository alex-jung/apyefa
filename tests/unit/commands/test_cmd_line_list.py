from typing import Final
from unittest.mock import patch

import pytest

from apyefa.commands.command_line_list import CommandLineList
from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaParameterError, EfaParseError

NAME: Final = "XML_LINELIST_REQUEST"


@pytest.fixture
def command():
    return CommandLineList("rapidJSON")


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
        "lineListBranchCode",
        "lineListNetBranchCode",
        "lineListSubnetwork",
        "lineListOMC",
        "lineListMixedLines",
        "mergeDir",
        "lineReqType",
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
        "transportations": [
            {
                "id": "vgn:63109: :H:j25",
                "disassembledName": "109",
                "description": "Bocksbeutel - Express Iphofen  -  Bullenheim  -  Weigenheim  -  Uffenheim",
                "product": {"id": 2, "class": 6, "name": "Regionalbus", "iconId": 3},
                "operator": {"code": "THUE", "id": "TH", "name": "Thuerauf GmbH"},
                "destination": {"name": "Uffenheim", "type": "stop"},
                "properties": {
                    "isTTB": True,
                    "isSTT": True,
                    "isROP": True,
                    "tripCode": 0,
                    "timetablePeriod": "Jahresfahrplan 2025",
                    "validity": {"from": "2024-12-15", "to": "2025-12-13"},
                    "lineDisplay": "TRAIN",
                    "globalId": "de:vgn:700_109:0",
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
