from typing import Final

import pytest

from apyefa.client import EfaClient
from apyefa.data_classes import LocationFilter, LocationType, SystemInfo

ENDPOINTS: Final = [
    "https://www3.vvs.de/mngvvs",
    "https://www.efa.de/efa/",
    "https://www.vrn.de/mngvrn/",
    "https://bahnland-bayern.de/efa/",
    "https://efa.vgn.de/vgnExt_oeffi/",
]

LOCATIONS: Final = ["de:09564:704"]


@pytest.mark.parametrize("url", ENDPOINTS)
async def test_async_info(url):
    async with EfaClient(url) as client:
        info = await client.info()

    assert info is not None
    assert isinstance(info, SystemInfo)


class TestLocationsByName:
    LOCATION_NAME: Final = "Königstraße"

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_no_filter(self, url):
        async with EfaClient(url) as client:
            # no filters
            locations = await client.locations_by_name(self.LOCATION_NAME)

            assert len(locations) > 0

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_stops(self, url):
        async with EfaClient(url) as client:
            # only stops
            locations_stops = await client.locations_by_name(
                self.LOCATION_NAME, filters=[LocationFilter.STOPS]
            )

            assert len(locations_stops) > 0
            assert all(loc.loc_type == LocationType.STOP for loc in locations_stops)

    @pytest.mark.parametrize("url", ENDPOINTS)
    async def test_async_locations_by_name_streets(self, url):
        async with EfaClient(url) as client:
            # only streets
            locations_addresses = await client.locations_by_name(
                self.LOCATION_NAME, filters=[LocationFilter.STREETS]
            )

            assert len(locations_addresses) > 0
            assert all(
                loc.loc_type == LocationType.STREET for loc in locations_addresses
            )
