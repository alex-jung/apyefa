import logging

import aiohttp

from apyefa.data_classes import (
    Departure,
    Location,
    LocationFilter,
    LocationType,
    SystemInfo,
    Transportation,
)
from apyefa.exceptions import EfaConnectionError
from apyefa.requests import (
    DeparturesRequest,
    Request,
    ServingLinesRequest,
    StopFinderRequest,
    SystemInfoRequest,
)

_LOGGER = logging.getLogger(__name__)


class EfaClient:
    async def __aenter__(self):
        self._client_session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._client_session.__aexit__(*args, **kwargs)

    def __init__(self, url: str, debug: bool = False):
        """Create a new instance of client.

        Args:
            url (str): url string to EFA endpoint

        Raises:
            ValueError: No url provided
        """
        if not url:
            raise ValueError("No EFA endpoint url provided")

        self._debug: bool = debug
        self._base_url: str = url if url.endswith("/") else f"{url}/"

    async def info(self) -> SystemInfo:
        """Get system info used by EFA endpoint.

        Returns:
            SystemInfo: info object
        """
        _LOGGER.info("Request system info")

        request = SystemInfoRequest()
        response = await self._run_query(self._build_url(request))

        return request.parse(response)

    async def locations_by_name(
        self, name: str, type="any", filters: list[LocationFilter] = []
    ) -> list[Location]:
        """Find location(s) by provided `name` (coordinates or stop name).

        Args:
            name (str): Name or ID of location to search (case insensitive)
            e.g. "Plärrer", "Nordostbanhof" or "de:09564:704"
            type (str, optional): ['any', 'coord']. Defaults to "any".
            filters (list[LocationFilter]): List of filters to apply for search. Defaults to empty.

        Returns:
            list[Location]: List of location(s) returned by endpoint. List is sorted by match quality.
        """
        _LOGGER.info(f"Request location search by name/id/coord {name}")
        _LOGGER.debug(f"type: {type}")
        _LOGGER.debug(f"filters: {filters}")

        request = StopFinderRequest(type, name)

        if filters:
            request.add_param("anyObjFilter_sf", sum(filters))

        # ToDo: add possibility for search by coordinates

        response = await self._run_query(self._build_url(request))

        return request.parse(response)

    async def location_by_coord(self) -> Location:
        pass

    async def trip(self):
        raise NotImplementedError

    async def departures_by_location(
        self,
        stop: Location | str,
        limit=40,
        date: str | None = None,
    ) -> list[Departure]:
        _LOGGER.info(f"Request departures for stop {stop}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"date: {date}")

        if isinstance(stop, Location):
            stop = stop.id

        request = DeparturesRequest(stop)

        # add parameters
        request.add_param("limit", limit)
        request.add_param_datetime(date)

        response = await self._run_query(self._build_url(request))

        return request.parse(response)

    async def transportations_by_name(self, line: str) -> list[Transportation]:
        _LOGGER.info("Request serving lines by name")
        _LOGGER.debug(f"line:{line}")

        request = ServingLinesRequest("line", line)

        response = await self._run_query(self._build_url(request))

        return request.parse(response)

    async def transportations_by_location(
        self, location: str | Location
    ) -> list[Transportation]:
        _LOGGER.info("Request lines by location")
        _LOGGER.debug(f"location:{location}")

        if isinstance(location, Location):
            if location.loc_type != LocationType.STOP:
                raise ValueError(
                    f"Only locations with type Stop are supported, provided {location.loc_type}"
                )
            location = location.id

        request = ServingLinesRequest("odv", location)

        response = await self._run_query(self._build_url(request))

        return request.parse(response)

    async def locations_by_transportation(
        self, line: str | Transportation
    ) -> list[Location]:
        pass

    async def _run_query(self, query: str) -> str:
        _LOGGER.info(f"Run query {query}")

        async with self._client_session.get(query) as response:
            _LOGGER.debug(f"Response status: {response.status}")

            if response.status == 200:
                text = await response.text()

                if self._debug:
                    _LOGGER.debug(text)

                return text
            else:
                raise EfaConnectionError(
                    f"Failed to fetch data from endpoint. Returned {response.status}"
                )

    def _build_url(self, request: Request):
        return self._base_url + str(request)
