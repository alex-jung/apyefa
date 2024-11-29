import pytest

from apyefa.exceptions import EfaParameterError, EfaResponseInvalid
from apyefa.requests.req_departures import DeparturesRequest


def test_init_name_and_macro():
    req = DeparturesRequest("my_stop")

    assert req._name == "XML_DM_REQUEST"
    assert req._macro == "dm"


def test_init_params():
    req = DeparturesRequest("my_stop")

    assert req._parameters.get("name_dm") == "my_stop"


def test_parse_success():
    req = DeparturesRequest("my_stop")

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
        "stopEvents": [
            {
                "location": {
                    "id": "de:09564:704:8:3",
                    "isGlobalId": True,
                    "name": "Nürnberg Plärrer",
                    "disassembledName": "U Gleis 3",
                    "type": "platform",
                    "coord": [5648722.0, 1231669.0],
                    "properties": {
                        "stopId": "3000704",
                        "area": "8",
                        "platform": "3",
                        "platformName": "U Gleis 3",
                    },
                    "parent": {
                        "id": "de:09564:704",
                        "isGlobalId": True,
                        "name": "Nürnberg Plärrer",
                        "disassembledName": "Plärrer",
                        "type": "stop",
                        "parent": {"name": "Nürnberg", "type": "locality"},
                        "properties": {"stopId": "3000704"},
                    },
                },
                "departureTimePlanned": "2024-11-27T21:16:00Z",
                "departureTimeEstimated": "2024-11-27T21:20:00Z",
                "transportation": {
                    "id": "vgn:11003: :R:j24",
                    "name": "U-Bahn U3",
                    "disassembledName": "U3",
                    "number": "U3",
                    "description": "Nordwestring - Hauptbahnhof - Plärrer - Großreuth bei Schweinau",
                    "product": {"id": 6, "class": 2, "name": "U-Bahn", "iconId": 1},
                    "operator": {"code": "VAG", "id": "VA", "name": "VAG"},
                    "destination": {
                        "id": "3001180",
                        "name": "Nürnberg Großreuth b. Schweinau",
                        "type": "stop",
                    },
                    "properties": {
                        "trainNumber": "4038429",
                        "isTTB": True,
                        "isSTT": True,
                        "isROP": True,
                        "tripCode": 939,
                        "lineDisplay": "LINE",
                        "globalId": "de:vgn:402_U3:0",
                    },
                    "origin": {
                        "id": "3000275",
                        "name": "Nürnberg Nordwestring",
                        "type": "stop",
                    },
                },
            }
        ],
    }

    info = req.parse(data)

    assert len(info) == 1


@pytest.mark.parametrize(
    "data", [{"locations": None}, {"locations": "value"}, {"locations": 123}]
)
def test_parse_failed(data):
    req = DeparturesRequest("my_stop")

    with pytest.raises(EfaResponseInvalid):
        req.parse(data)


@pytest.mark.parametrize("value", ["any", "coord"])
def test_add_valid_param(value):
    req = DeparturesRequest("my_stop")

    req.add_param("type_dm", value)

    # no exceptions occured


@pytest.mark.parametrize("invalid_param", ["dummy", "STOP"])
def test_add_invalid_param(invalid_param):
    req = DeparturesRequest("my_stop")

    with pytest.raises(EfaParameterError):
        req.add_param(invalid_param, "valid_value")
