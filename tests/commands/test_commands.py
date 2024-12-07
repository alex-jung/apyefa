import pytest

from apyefa.commands.command_departures import CommandDepartures
from apyefa.commands.command_serving_lines import CommandServingLines
from apyefa.commands.command_stop_finder import CommandStopFinder
from apyefa.commands.command_system_info import CommandSystemInfo
from apyefa.commands.command_trip import CommandTrip


@pytest.fixture(scope="module")
def system_info_command():
    return CommandSystemInfo()


@pytest.fixture(scope="module")
def departures_command():
    return CommandDepartures("my_stop")


@pytest.fixture(scope="module")
def trip_command():
    return CommandTrip()


@pytest.fixture(scope="module")
def serving_lines_command():
    return CommandServingLines("odv", "test")


@pytest.fixture(scope="module")
def stop_finder_command():
    return CommandStopFinder(req_type="line", name="my_name")


@pytest.mark.parametrize(
    "command, cmd_name, cmd_macro",
    [
        ("system_info_command", "XML_SYSTEMINFO_REQUEST", "system"),
        ("departures_command", "XML_DM_REQUEST", "dm"),
        ("trip_command", "XML_TRIP_REQUEST2", "trip"),
        ("serving_lines_command", "XML_SERVINGLINES_REQUEST", "servingLines"),
        ("stop_finder_command", "XML_STOPFINDER_REQUEST", "stopfinder"),
    ],
)
def test_init_macro_and_name(command, cmd_name, cmd_macro, request):
    cmd = request.getfixturevalue(command)
    assert cmd._name == cmd_name
    assert cmd._macro == cmd_macro


@pytest.mark.parametrize(
    "command, expected",
    [
        (
            "system_info_command",
            {"outputFormat": "rapidJSON", "coordOutputFormat": "WGS84"},
        ),
        (
            "departures_command",
            {
                "outputFormat": "rapidJSON",
                "coordOutputFormat": "WGS84",
                "name_dm": "my_stop",
            },
        ),
        ("trip_command", {"outputFormat": "rapidJSON", "coordOutputFormat": "WGS84"}),
    ],
)
def test_init_parameters(command, expected, request):
    cmd = request.getfixturevalue(command)

    assert len(cmd._parameters) == len(expected.keys())
    for key, value in cmd._parameters.items():
        assert key in expected.keys()
        assert value == expected[key]


def test_init_parameters_serving_lines():
    cmd = CommandServingLines("line", "my_value")
    assert cmd._parameters == {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "WGS84",
        "lineName": "my_value",
        "mode": "line",
    }

    cmd = CommandServingLines("odv", "my_value")
    assert cmd._parameters == {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "WGS84",
        "type_sl": "stopID",
        "name_sl": "my_value",
        "mode": "odv",
    }


def test_init_invalid_params():
    pass
