import pytest
from voluptuous import Optional, Required, Schema

from apyefa.exceptions import EfaParameterError
from apyefa.requests.req import Request


class MockRequest(Request):
    def parse(data: str):
        pass

    def _get_params_schema(self):
        return Schema(
            {
                Required("outputFormat"): str,
                Optional("valid_param"): str,
                Optional("itdDate"): str,
                Optional("itdTime"): str,
            },
            required=False,
        )

    def _get_response_schema(self):
        return Schema(
            {
                Required("req_param"): str,
                Optional("opt_param_1"): str,
                Optional("opt_param_2"): str,
            },
            required=False,
        )


@pytest.fixture
def mock_request() -> MockRequest:
    return MockRequest("my_name", "my_macro")


def test_request_init(mock_request: MockRequest):
    assert mock_request._name == "my_name"
    assert mock_request._macro == "my_macro"
    assert len(mock_request._parameters) == 1  # outputFormat=rapidJSON set as default


def test_request_to_str_default_params(mock_request):
    assert str(mock_request) == "my_name?commonMacro=my_macro&outputFormat=rapidJSON"


def test_request_unknown_parameters(mock_request):
    mock_request._parameters = {
        "outputFormat": "rapidJSON",
        "opt1": "value1",
        "opt2": "value2",
        "opt3": "value3",
    }

    with pytest.raises(EfaParameterError):
        str(mock_request)


@pytest.mark.parametrize(
    "params, expected",
    [
        ({}, ""),
        ({"opt1": "value"}, "&opt1=value"),
        ({"opt1": "value1", "opt2": "value2"}, "&opt1=value1&opt2=value2"),
    ],
)
def test_request_params_str(mock_request, params, expected):
    mock_request._parameters = params
    assert mock_request._params_str() == expected


@pytest.mark.parametrize(
    "param, value", [(None, None), (None, "value"), ("param", None), ("", "")]
)
def test_request_add_param_empty(mock_request: MockRequest, param, value):
    before = mock_request._parameters.copy()

    mock_request.add_param(param, value)

    after = mock_request._parameters

    assert before == after


def test_request_add_param_success(mock_request: MockRequest):
    assert len(mock_request._parameters) == 1

    mock_request.add_param("valid_param", "value1")

    assert len(mock_request._parameters) == 2


@pytest.mark.parametrize("value", [None, ""])
def test_request_add_param_datetime_empty(mock_request: MockRequest, value):
    assert len(mock_request._parameters) == 1

    mock_request.add_param_datetime(value)

    assert len(mock_request._parameters) == 1


@pytest.mark.parametrize("date", [123, {"key": "value"}, "202422-16:34"])
def test_request_add_param_datetime_exception(mock_request: MockRequest, date):
    with pytest.raises(ValueError):
        mock_request.add_param_datetime(date)


def test_request_add_param_datetime_datetime(mock_request: MockRequest):
    datetime = "20201212 10:41"

    assert mock_request._parameters.get("itdDate", None) is None
    assert mock_request._parameters.get("itdTime", None) is None

    mock_request.add_param_datetime(datetime)

    assert mock_request._parameters.get("itdDate", None) == "20201212"
    assert mock_request._parameters.get("itdTime", None) == "1041"


def test_request_add_param_datetime_date(mock_request: MockRequest):
    date = "20201212"

    assert mock_request._parameters.get("itdDate", None) is None
    assert mock_request._parameters.get("itdTime", None) is None

    mock_request.add_param_datetime(date)

    assert mock_request._parameters.get("itdTime", None) is None
    assert mock_request._parameters.get("itdDate", None) == "20201212"


def test_request_add_param_datetime_time(mock_request: MockRequest):
    time = "16:34"

    assert mock_request._parameters.get("itdDate", None) is None
    assert mock_request._parameters.get("itdTime", None) is None

    mock_request.add_param_datetime(time)

    assert mock_request._parameters.get("itdDate", None) is None
    assert mock_request._parameters.get("itdTime", None) == "1634"
