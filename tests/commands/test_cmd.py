import pytest
from voluptuous import Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.exceptions import EfaParameterError


class MockCommand(Command):
    def parse(data: str):
        pass

    def _get_params_schema(self):
        return Schema(
            {
                Required("outputFormat"): str,
                Required("coordOutputFormat"): str,
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
def mock_command() -> MockCommand:
    return MockCommand("my_name", "my_macro")


def test_command_init(mock_command):
    assert mock_command._name == "my_name"
    assert mock_command._macro == "my_macro"
    assert (
        len(mock_command._parameters) == 2
    )  # outputFormat=rapidJSON and coordOutputFormas set as default


def test_command_to_str_default_params(mock_command):
    assert (
        str(mock_command)
        == "my_name?commonMacro=my_macro&outputFormat=rapidJSON&coordOutputFormat=WGS84"
    )


def test_command_validation_failed(mock_command):
    mock_command._parameters = {
        "outputFormat": "rapidJSON",
        "opt1": "value1",
        "opt2": "value2",
        "opt3": "value3",
    }

    with pytest.raises(EfaParameterError):
        mock_command.validate()


@pytest.mark.parametrize(
    "params, expected",
    [
        ({}, ""),
        ({"opt1": "value"}, "&opt1=value"),
        ({"opt1": "value1", "opt2": "value2"}, "&opt1=value1&opt2=value2"),
    ],
)
def test_command_params_str(mock_command, params, expected):
    mock_command._parameters = params
    assert mock_command._get_params_as_str() == expected


@pytest.mark.parametrize(
    "param, value", [(None, None), (None, "value"), ("param", None), ("", "")]
)
def test_command_add_param_empty(mock_command, param, value):
    before = mock_command._parameters.copy()

    mock_command.add_param(param, value)

    after = mock_command._parameters

    assert before == after


def test_command_add_param_success(mock_command):
    assert len(mock_command._parameters) == 2

    mock_command.add_param("valid_param", "value1")

    assert len(mock_command._parameters) == 3


@pytest.mark.parametrize("value", [None, ""])
def test_command_add_param_datetime_empty(mock_command, value):
    assert len(mock_command._parameters) == 2

    mock_command.add_param_datetime(value)

    assert len(mock_command._parameters) == 2


@pytest.mark.parametrize("param, value", [("test_param", "test_value")])
def test_command_add_param_missmatch_schema(mock_command, param, value):
    with pytest.raises(EfaParameterError):
        mock_command.add_param(param, value)


@pytest.mark.parametrize("date", [123, {"key": "value"}, "202422-16:34"])
def test_command_add_param_datetime_exception(mock_command, date):
    with pytest.raises(ValueError):
        mock_command.add_param_datetime(date)


def test_command_add_param_datetime_datetime(mock_command):
    datetime = "20201212 10:41"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(datetime)

    assert mock_command._parameters.get("itdDate", None) == "20201212"
    assert mock_command._parameters.get("itdTime", None) == "1041"


def test_command_add_param_datetime_date(mock_command):
    date = "20201212"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(date)

    assert mock_command._parameters.get("itdTime", None) is None
    assert mock_command._parameters.get("itdDate", None) == "20201212"


def test_command_add_param_datetime_time(mock_command):
    time = "16:34"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(time)

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) == "1634"
