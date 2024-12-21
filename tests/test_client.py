from typing import Final
from unittest.mock import AsyncMock, Mock, patch

import pytest

from apyefa.client import QUERY_TIMEOUT, EfaClient
from apyefa.data_classes import CoordFormat, Location, LocationFilter, LocationType
from apyefa.exceptions import EfaConnectionError, EfaFormatNotSupported

API_TEST_URL: Final = "https://test_api.com/"


@pytest.fixture
async def test_async_client():
    async with EfaClient(API_TEST_URL) as client:
        yield client


class TestInit:
    @pytest.mark.parametrize("url", ["https://test_api.com", "https://test_api.com/"])
    async def test_default_arguments(self, url):
        async with EfaClient(url) as client:
            assert client._format == "rapidJSON"
            assert not client._debug
            assert client._base_url == API_TEST_URL

    async def test_no_url(self):
        with pytest.raises(ValueError):
            async with EfaClient(None):
                ...

    async def test_invalid_format(self):
        with pytest.raises(EfaFormatNotSupported):
            async with EfaClient(API_TEST_URL, format="xml"):
                ...


class TestFunctionInfo:
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_success(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_system_info.CommandSystemInfo.add_param"
        ) as mock_add_param:
            await test_async_client.info()

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)


class TestFunctionLocationsByName:
    @pytest.mark.parametrize("name", ["test"])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_default_parameters(self, _, test_async_client: EfaClient, name):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.locations_by_name(name)

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("locationServerActive", 1)
        mock_add_param.assert_any_call("type_sf", "any")
        mock_add_param.assert_any_call("name_sf", name)
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)
        mock_add_param.assert_any_call("doNotSearchForStops_sf", True)

    async def test_no_name(self, test_async_client: EfaClient):
        with pytest.raises(ValueError):
            await test_async_client.locations_by_name(None)

    @pytest.mark.parametrize("limit", [0, 1, 10])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_limit(self, _, test_async_client: EfaClient, limit):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.parse"
        ) as mock_parse:
            mock_parse.return_value = [x for x in range(limit * 2)]

            result = await test_async_client.locations_by_name("any name", limit=limit)

            assert len(result) == limit

    @pytest.mark.parametrize("search_nearbly_stops", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_search_nearbly_stops(
        self, _, test_async_client: EfaClient, search_nearbly_stops
    ):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.locations_by_name(
                "any name", search_nearbly_stops=search_nearbly_stops
            )

            mock_add_param.assert_any_call(
                "doNotSearchForStops_sf", not search_nearbly_stops
            )

    @pytest.mark.parametrize(
        "filters",
        [
            [LocationFilter.ADDRESSES, LocationFilter.POST_CODES],
            [LocationFilter.NO_FILTER],
        ],
    )
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_filters(self, _, test_async_client: EfaClient, filters):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.locations_by_name("any name", filters=filters)

            mock_add_param.assert_called_with("anyObjFilter_sf", sum(filters))


class TestFunctionLocationsByCoord:
    @pytest.mark.parametrize("x,y", [(0, 0), (-1, 1)])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_default_parameters(self, _, test_async_client: EfaClient, x, y):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.location_by_coord(x, y)

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("locationServerActive", 1)
        mock_add_param.assert_any_call("type_sf", "coord")
        mock_add_param.assert_any_call("name_sf", f"{x}:{y}:{CoordFormat.WGS84}")
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)

    @pytest.mark.parametrize("limit", [0, 1, 10])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_limit(self, _, test_async_client: EfaClient, limit):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.parse"
        ) as mock_parse:
            mock_parse.return_value = [x for x in range(limit * 2)]

            result = await test_async_client.location_by_coord(0, 0, limit=limit)

            assert len(result) == limit

    @pytest.mark.parametrize(
        "format",
        [CoordFormat.WGS84, "myFormat"],
    )
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_format(self, _, test_async_client: EfaClient, format):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.location_by_coord(0, 0, format=format)

            mock_add_param.assert_any_call("name_sf", f"0:0:{format}")

    @pytest.mark.parametrize("search_nearbly_stops", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_search_nearbly_stops(
        self, _, test_async_client: EfaClient, search_nearbly_stops
    ):
        with patch(
            "apyefa.commands.command_stop_finder.CommandStopFinder.add_param"
        ) as mock_add_param:

            await test_async_client.location_by_coord(
                0, 0, search_nearbly_stops=search_nearbly_stops
            )

            mock_add_param.assert_any_call(
                "doNotSearchForStops_sf", not search_nearbly_stops
            )


class TestFunctionRunQuery:
    @patch("aiohttp.ClientSession.get")
    async def test_success_status_200(self, mock_get, test_async_client: EfaClient):
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text.return_value = "test"

        await test_async_client._run_query("test_url")

        mock_get.assert_called_with("test_url", ssl=False, timeout=QUERY_TIMEOUT)

    @patch("aiohttp.ClientSession.get")
    async def test_failed_status_400(self, mock_get, test_async_client: EfaClient):
        mock_get.return_value.__aenter__.return_value.status = 400
        mock_get.return_value.__aenter__.return_value.text.return_value = "test"

        with pytest.raises(EfaConnectionError):
            await test_async_client._run_query("test_url")

        mock_get.assert_called_with("test_url", ssl=False, timeout=QUERY_TIMEOUT)

    @pytest.mark.skip(reason="no way of currently testing this")
    @patch("aiohttp.ClientSession.get")
    async def test_failed_timeout(self, mock_get, test_async_client: EfaClient):
        mock_get.return_value.__aenter__.return_value = AsyncMock(
            side_effect=TimeoutError
        )
        # mock_get.return_value.__aenter__.return_value.status = 200
        # mock_get.return_value.__aenter__.return_value.text.return_value =

        with pytest.raises(TimeoutError):
            await test_async_client._run_query("test_url")


class TestFunctionLinesByName:
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_default_parameters(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_name("any name")

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)
        mock_add_param.assert_any_call("mode", "line")
        mock_add_param.assert_any_call("lineName", "any name")
        mock_add_param.assert_any_call("locationServerActive", 1)

    async def test_no_name(self, test_async_client: EfaClient):
        with pytest.raises(ValueError):
            await test_async_client.lines_by_name(None)

    @pytest.mark.parametrize("merge_dirs", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_merge_dirs(self, _, test_async_client: EfaClient, merge_dirs):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_name(
                "any name", merge_directions=merge_dirs
            )

        mock_add_param.assert_any_call("mergeDir", merge_dirs)

    @pytest.mark.parametrize("show_trains_explicit", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_show_trains_explicit(
        self, _, test_async_client: EfaClient, show_trains_explicit
    ):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_name(
                "any name", show_trains_explicit=show_trains_explicit
            )

        mock_add_param.assert_any_call("lsShowTrainsExplicit", show_trains_explicit)


class TestFunctionLinesByLocation:
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_location_str(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_location("any location")

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)
        mock_add_param.assert_any_call("mode", "odv")
        mock_add_param.assert_any_call("type_sl", "stopID")
        mock_add_param.assert_any_call("name_sl", "any location")
        mock_add_param.assert_any_call("locationServerActive", 1)

    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_location(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:
            location = Mock(spec=Location)
            location.id = "de:06412:1975"
            location.name = "any location"
            location.loc_type = LocationType.STOP

            await test_async_client.lines_by_location(location)

        mock_add_param.assert_any_call("name_sl", location.id)

    async def test_no_location(self, test_async_client: EfaClient):
        with pytest.raises(ValueError):
            await test_async_client.lines_by_location(None)

    @pytest.mark.parametrize(
        "loc_type",
        [
            LocationType.ADDRESS,
            LocationType.POI,
            LocationType.STREET,
            LocationType.UNKNOWN,
        ],
    )
    async def test_location_invalid_type(self, test_async_client: EfaClient, loc_type):
        with pytest.raises(ValueError):
            location = Mock(spec=Location)
            location.id = "de:06412:1975"
            location.name = "any location"
            location.loc_type = loc_type

            await test_async_client.lines_by_location(location)

    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_req_types(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_location("any name", req_types=[1, 2, 3])

        mock_add_param.assert_any_call("lineReqType", sum([1, 2, 3]))

    @pytest.mark.parametrize("merge_dirs", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_merge_dirs(self, _, test_async_client: EfaClient, merge_dirs):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_location(
                "any name", merge_directions=merge_dirs
            )

        mock_add_param.assert_any_call("mergeDir", merge_dirs)

    @pytest.mark.parametrize("show_trains_explicit", [True, False])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_show_trains_explicit(
        self, _, test_async_client: EfaClient, show_trains_explicit
    ):
        with patch(
            "apyefa.commands.command_serving_lines.CommandServingLines.add_param"
        ) as mock_add_param:

            await test_async_client.lines_by_location(
                "any name", show_trains_explicit=show_trains_explicit
            )

        mock_add_param.assert_any_call("lsShowTrainsExplicit", show_trains_explicit)


class TestFunctionDeparturesByLocation:
    @pytest.mark.parametrize("location", ["test"])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_default_parameters(self, _, test_async_client: EfaClient, location):
        with patch(
            "apyefa.commands.command_departures.CommandDepartures.add_param"
        ) as mock_add_param:

            await test_async_client.departures_by_location(location)

        mock_add_param.assert_any_call("outputFormat", "rapidJSON")
        mock_add_param.assert_any_call("coordOutputFormat", CoordFormat.WGS84.value)
        mock_add_param.assert_any_call("locationServerActive", 1)
        mock_add_param.assert_any_call("name_dm", location)
        mock_add_param.assert_any_call("mode", "direct")
        mock_add_param.assert_any_call("useAllStops", "1")
        mock_add_param.assert_any_call("lsShowTrainsExplicit", "1")
        mock_add_param.assert_any_call("useProxFootSearch", "0")
        mock_add_param.assert_any_call("useRealtime", True)

    async def test_no_location(self, test_async_client: EfaClient):
        with pytest.raises(ValueError):
            await test_async_client.departures_by_location(None)

    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_location_object(self, _, test_async_client: EfaClient):
        with patch(
            "apyefa.commands.command_departures.CommandDepartures.add_param"
        ) as mock_add_param:
            location = Mock(spec=Location)
            location.id = "de:06412:1975"

            await test_async_client.departures_by_location(location)

        mock_add_param.assert_any_call("name_dm", location.id)

    @pytest.mark.parametrize("format, mode", [("rapidJSON", "direct"), ("xml", "any")])
    @patch.object(EfaClient, "_run_query", return_value="")
    async def test_different_mode(self, _, test_async_client: EfaClient, format, mode):
        with patch(
            "apyefa.commands.command_departures.CommandDepartures.add_param"
        ) as mock_add_param:
            with patch(
                "apyefa.commands.command_departures.CommandDepartures.parse"
            ) as mock_parse:
                mock_parse.return_value = ""

                test_async_client._format = format

                await test_async_client.departures_by_location("my_location")

                mock_add_param.assert_any_call("mode", mode)
