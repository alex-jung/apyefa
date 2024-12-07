import pytest

from apyefa.commands.parsers.xml_parser import XmlParser


@pytest.fixture
def xml_parser():
    return XmlParser()


def test_parse(xml_parser):
    with pytest.raises(NotImplementedError):
        xml_parser.parse("text")
