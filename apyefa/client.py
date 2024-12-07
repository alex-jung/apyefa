import logging

import aiohttp

from apyefa.commands import (
    Command,
    CommandDepartures,
    CommandServingLines,
    CommandStopFinder,
    CommandSystemInfo,
)
from apyefa.data_classes import (
    CoordFormat,
    Departure,
    Line,
    Location,
    LocationFilter,
    LocationType,
    SystemInfo,
)
from apyefa.exceptions import EfaConnectionError

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

        command = CommandSystemInfo()
        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def locations_by_name(
        self, name: str, *, filters: list[LocationFilter] = [], limit: int = 30
    ) -> list[Location]:
        """Find location(s) by provided `name`.

        Args:
            name (str): Name or ID of location to search (case insensitive)
            e.g. "Plärrer", "Nordostbanhof" or "de:09564:704"
            filters (list[LocationFilter], optional): List of filters to apply for search. Defaults to empty.
            limit (int, optional): Max size of returned list. Defaults to 30.

        Returns:
            list[Location]: List of location(s) returned by endpoint. List is sorted by match quality.
        """
        _LOGGER.info(f"Request location search by name/id: {name}")
        _LOGGER.debug(f"filters: {filters}")
        _LOGGER.debug(f"limit: {limit}")

        command = CommandStopFinder("any", name)
        command.add_param("anyMaxSizeHitList", limit)

        if filters:
            command.add_param("anyObjFilter_sf", sum(filters))

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def location_by_coord(
        self,
        coord_x: float,
        coord_y: float,
        format: CoordFormat = CoordFormat.WGS84,
        limit: int = 10,
    ) -> Location:
        """Find location(s) by provided `coordinates`.

        Args:
            coord_x (float): X coordinate
            coord_y (float): Y coordinate
            format (CoordFormat, optional): Coordinate format. Defaults to CoordFormat.WGS84.
            limit (int, optional): Max size of returned list. Defaults to 10.

        Returns:
            Location: List of location(s) returned by endpoint. List is sorted by match quality.
        """
        _LOGGER.info("Request location search by coordinates")
        _LOGGER.debug(f"coord_x: {coord_x}")
        _LOGGER.debug(f"coord_y: {coord_y}")
        _LOGGER.debug(f"format: {format}")
        _LOGGER.debug(f"limit: {limit}")

        command = CommandStopFinder("coord", f"{coord_x}:{coord_y}:{format}")
        command.add_param("anyMaxSizeHitList", limit)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

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

        command = CommandDepartures(stop)

        # add parameters
        command.add_param("limit", limit)
        command.add_param_datetime(date)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def lines_by_name(self, line: str) -> list[Line]:
        """Search lines by name. e.g. subway `U3` or bus `65`

        Args:
            line (str): Line name to search

        Returns:
            list[Transport]: List of lines
        """
        _LOGGER.info("Request lines by name")
        _LOGGER.debug(f"line:{line}")

        command = CommandServingLines("line", line)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def lines_by_location(self, location: str | Location) -> list[Line]:
        """Search for lines that pass `location`. Location can be location ID like `de:08111:6221` or a Location object

        Args:
            location (str | Location): Location

        Raises:
            ValueError: If not a stop location provided but e.g. POI or Address

        Returns:
            list[Transport]: List of lines
        """
        _LOGGER.info("Request lines by location")
        _LOGGER.debug(f"location:{location}")

        if isinstance(location, Location):
            if location.loc_type != LocationType.STOP:
                raise ValueError(
                    f"Only locations with type Stop are supported, provided {location.loc_type}"
                )
            location = location.id

        command = CommandServingLines("odv", location)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def locations_by_line(self, line: str | Line) -> list[Location]:
        raise NotImplementedError

    async def _run_query(self, query: str) -> str:
        _LOGGER.info(f"Run query {query}")

        async with self._client_session.get(query, ssl=False) as response:
            _LOGGER.debug(f"Response status: {response.status}")

            if response.status == 200:
                text = await response.text()

                if self._debug:
                    _LOGGER.debug(text)

                return text
            else:
                raise EfaConnectionError(
                    f"Failed to fetch data from endpoint. Returned status: {response.status}"
                )

    def _build_url(self, cmd: Command):
        return self._base_url + str(cmd)
