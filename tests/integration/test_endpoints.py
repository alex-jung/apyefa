from datetime import datetime
from typing import Final

import pytest

from apyefa.client import EfaClient
from apyefa.data_classes import LocationFilter, LocationType, SystemInfo

ENDPOINTS: Final = [
    "https://www3.vvs.de/mngvvs",
    "https://www.efa.de/efa/",
    "https://www.vrn.de/mngvrn/",
    "https://bahnland-bayern.de/efa/",
    # "https://efa.vgn.de/vgnExt_oeffi/", vgn.de supports domestic locations only
]

LOCATIONS: Final = ["de:09564:704"]


@pytest.mark.parametrize("url", ENDPOINTS)
async def test_async_info(url):
    try:
        async with EfaClient(url) as client:
            info = await client.info()

            assert info is not None
            assert isinstance(info, SystemInfo)
    except TimeoutError:
        pass


class TestLocationsByName:
    LOCATION_NAME: Final = "Königstraße"

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_no_filter(self, url):
        try:
            async with EfaClient(url) as client:
                # no filters
                locations = await client.locations_by_name(self.LOCATION_NAME)

                assert len(locations) > 0
        except TimeoutError:
            pass

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_stops(self, url):
        try:
            async with EfaClient(url) as client:
                # only stops
                locations_stops = await client.locations_by_name(
                    self.LOCATION_NAME, filters=[LocationFilter.STOPS]
                )

                assert len(locations_stops) > 0
                assert all(loc.loc_type == LocationType.STOP for loc in locations_stops)
        except TimeoutError:
            pass

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_streets(self, url):
        try:
            async with EfaClient(url) as client:
                # only streets
                locations_addresses = await client.locations_by_name(
                    self.LOCATION_NAME, filters=[LocationFilter.STREETS]
                )

                assert len(locations_addresses) > 0
                assert all(
                    loc.loc_type == LocationType.STREET for loc in locations_addresses
                )
        except TimeoutError:
            pass


class TestTrip:
    ORIGIN_ID: Final = "de:08111:6118"  # Stuttgart Hauptbahnhof
    DESTINATION_ID: Final = "de:08111:6056"  # Stuttgart Marienplatz

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_trip_without_datetime(self, url):
        try:
            async with EfaClient(url) as client:
                # trip without datetime
                journeys = await client.trip(self.ORIGIN_ID, self.DESTINATION_ID)

                assert len(journeys) > 0
        except TimeoutError:
            pass

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_trip_with_datetime(self, url):
        try:
            async with EfaClient(url) as client:
                # trip with datetime (test the bug fix)
                trip_datetime = datetime.now()
                journeys = await client.trip(
                    self.ORIGIN_ID, self.DESTINATION_ID, trip_datetime=trip_datetime
                )

                assert len(journeys) > 0
        except TimeoutError:
            pass

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_trip_with_datetime_departure(self, url):
        try:
            async with EfaClient(url) as client:
                # trip with datetime and explicit departure
                trip_datetime = datetime.now()
                journeys = await client.trip(
                    self.ORIGIN_ID,
                    self.DESTINATION_ID,
                    trip_departure=True,
                    trip_datetime=trip_datetime,
                )

                assert len(journeys) > 0
        except TimeoutError:
            pass
