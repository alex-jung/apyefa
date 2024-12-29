from datetime import datetime

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


@pytest.fixture
def mock_command() -> MockCommand:
    return MockCommand("my_name", "my_format")


def test_command_init(mock_command):
    assert mock_command._name == "my_name"
    assert mock_command._parameters == {"outputFormat": "my_format"}


def test_command_to_str_default_params(mock_command):
    assert str(mock_command) == "my_name?outputFormat=my_format"


@pytest.mark.parametrize(
    "params, expected",
    [
        ({}, ""),
        ({"opt1": "value"}, "?opt1=value"),
        ({"opt1": "value1", "opt2": "value2"}, "?opt1=value1&opt2=value2"),
    ],
)
def test_command_params_str(mock_command, params, expected):
    mock_command._parameters = params
    assert mock_command._get_params_as_str() == expected


@pytest.mark.parametrize(
    "param, value", [(None, None), (None, "value"), ("param", None), ("", "")]
)
def test_command_add_param_empty(mock_command, param, value):
    mock_command.add_param(param, value)

    assert mock_command._parameters == {"outputFormat": "my_format"}


def test_command_add_param_success(mock_command):
    mock_command.add_param("valid_param", "value1")

    assert mock_command._parameters == {
        "outputFormat": "my_format",
        "valid_param": "value1",
    }


@pytest.mark.parametrize("bool_value, expected_value", [(True, "1"), (False, "0")])
def test_command_add_param_bool(mock_command, bool_value, expected_value):
    mock_command.add_param("valid_param", bool_value)

    assert mock_command._parameters == {
        "outputFormat": "my_format",
        "valid_param": expected_value,
    }


@pytest.mark.parametrize("value", [None, ""])
def test_command_add_param_datetime_empty(mock_command, value):
    assert len(mock_command._parameters) == 1

    mock_command.add_param_datetime(value)

    assert len(mock_command._parameters) == 1


@pytest.mark.parametrize("param, value", [("test_param", "test_value")])
def test_command_add_param_missmatch_schema(mock_command, param, value):
    with pytest.raises(EfaParameterError):
        mock_command.add_param(param, value)
        mock_command.validate_params()


@pytest.mark.parametrize("date", [123, {"key": "value"}, "202422-16:34"])
def test_command_add_param_datetime_exception(mock_command, date):
    with pytest.raises(ValueError):
        mock_command.add_param_datetime(date)


def test_command_add_param_datetime_str_datetime(mock_command):
    datetime = "20201212 10:41"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(datetime)

    assert mock_command._parameters.get("itdDate", None) == "20201212"
    assert mock_command._parameters.get("itdTime", None) == "1041"


def test_command_add_param_datetime_str_date(mock_command):
    date = "20201212"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(date)

    assert mock_command._parameters.get("itdTime", None) is None
    assert mock_command._parameters.get("itdDate", None) == "20201212"


def test_command_add_param_datetime_str_time(mock_command):
    time = "16:34"

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(time)

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) == "1634"


def test_command_add_param_datetime_datetime(mock_command):
    dt = datetime(2020, 12, 12, 16, 34)

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(dt)

    assert mock_command._parameters.get("itdDate", None) == "20201212"
    assert mock_command._parameters.get("itdTime", None) == "1634"


def test_command_add_param_datetime_date(mock_command):
    dt = datetime(2020, 12, 12, 16, 34).date()

    assert mock_command._parameters.get("itdDate", None) is None
    assert mock_command._parameters.get("itdTime", None) is None

    mock_command.add_param_datetime(dt)

    assert mock_command._parameters.get("itdDate", None) == "20201212"
    assert mock_command._parameters.get("itdTime", None) is None
