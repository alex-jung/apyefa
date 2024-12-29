import pytest

from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser


@pytest.fixture
def json_parser():
    return RapidJsonParser()


@pytest.mark.parametrize("data", [None, ""])
def test_parse_empty_data(json_parser, data):
    assert json_parser.parse(data) == {}


def test_parse_success(json_parser):
    data = '{"hello":"world"}'

    assert json_parser.parse(data) == {"hello": "world"}
