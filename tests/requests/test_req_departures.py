import pytest

import requests
from apyefa.exceptions import EfaParameterError
from apyefa.requests.req_departures import DeparturesRequest


def run_departures_query():
    r = requests.get(
        "https://efa.vgn.de/vgnExt_oeffi/XML_DM_REQUEST?commonMacro=dm&outputFormat=rapidJSON&name_dm=de:09564:704&limit=3&itdTime=2216&itdDate=20241110&mode=direct&type_dm=stop&useRealtime=1"
    )
    assert r.status_code == 200

    return r.text


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
        "locations": [],
        "stopEvents": [],
    }

    response = run_departures_query()

    info = req.parse(response)

    assert len(info) > 0


@pytest.mark.parametrize("data", [True, 123])
def test_parse_failed(data):
    req = DeparturesRequest("my_stop")

    with pytest.raises(TypeError):
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
