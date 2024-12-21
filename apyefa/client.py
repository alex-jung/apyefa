import logging
from datetime import date, datetime

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
    LineRequestType,
    Location,
    LocationFilter,
    LocationType,
    SystemInfo,
)
from apyefa.exceptions import EfaConnectionError, EfaFormatNotSupported

_LOGGER = logging.getLogger(__name__)
QUERY_TIMEOUT = 10  # seconds


class EfaClient:
    async def __aenter__(self):
        self._client_session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._client_session.__aexit__(*args, **kwargs)

    def __init__(self, url: str, debug: bool = False, format: str = "rapidJSON"):
        """Create a new instance of client.

        Args:
            url(str): EFA endpoint url
            format(str, optional): Format of the response. Defaults to "rapidJSON".

        Raises:
            ValueError: If no url provided
            EfaFormatNotSupported: If format is not supported
        """
        if not url:
            raise ValueError("No EFA endpoint url provided")

        if format != "rapidJSON":
            raise EfaFormatNotSupported(f"Format {format} is not supported")

        self._debug: bool = debug
        self._format: str = format
        self._base_url: str = url if url.endswith("/") else f"{url}/"

    async def info(self) -> SystemInfo:
        """Get EFA endpoint system info.

        Returns:
            SystemInfo: info object
        """
        _LOGGER.info("Request system info")

        command = CommandSystemInfo(self._format)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def locations_by_name(
        self,
        name: str,
        *,
        filters: list[LocationFilter] = [],
        limit: int = 30,
        search_nearbly_stops: bool = False,
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

        command = CommandStopFinder(self._format)

        command.add_param("locationServerActive", 1)
        command.add_param("type_sf", "any")
        command.add_param("name_sf", name)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)
        command.add_param("doNotSearchForStops_sf", not search_nearbly_stops)

        if filters:
            command.add_param("anyObjFilter_sf", sum(filters))

        response = await self._run_query(self._build_url(command))

        return command.parse(response)[:limit]

    async def location_by_coord(
        self,
        coord_x: float,
        coord_y: float,
        format: CoordFormat = CoordFormat.WGS84,
        limit: int = 10,
        search_nearbly_stops: bool = False,
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

        command = CommandStopFinder(self._format)
        command.add_param("locationServerActive", 1)
        command.add_param("type_sf", "coord")
        command.add_param("name_sf", f"{coord_x}:{coord_y}:{format}")
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)
        command.add_param("doNotSearchForStops_sf", not search_nearbly_stops)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)[:limit]

    async def trip(self):
        raise NotImplementedError

    async def departures_by_location(
        self,
        stop: Location | str,
        limit=40,
        arg_date: str | datetime | date | None = None,
    ) -> list[Departure]:
        _LOGGER.info(f"Request departures for stop {stop}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"date: {arg_date}")

        if isinstance(stop, Location):
            stop = stop.id

        command = CommandDepartures(stop)

        # add parameters
        command.add_param("limit", limit)
        command.add_param("name_dm", stop)
        command.add_param("locationServerActive", 1)

        command.add_param_datetime(arg_date)

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

        command = CommandServingLines(self._format)
        command.add_param("lineName", line)
        command.add_param("mode", "line")
        command.add_param("locationServerActive", 1)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def lines_by_location(
        self, location: str | Location, req_types: list[LineRequestType] = []
    ) -> list[Line]:
        """Search for lines that pass `location`. Location can be location ID like `de:08111:6221` or a `Location` object

        Args:
            location (str | Location): Location
            req_types (list[LineRequestType], optional): List of types for the request. Defaults to empty.

        Raises:
            ValueError: Wrong location type provided e.g. LocationType.POI or LocationType.ADDRESS

        Returns:
            list[Transport]: List of lines
        """
        _LOGGER.info("Request lines by location")
        _LOGGER.debug(f"location:{location}")
        _LOGGER.debug(f"filters :{req_types}")

        if isinstance(location, Location):
            if location.loc_type != LocationType.STOP:
                raise ValueError(
                    f"Only locations with type Stop are supported, provided {location.loc_type}"
                )
            location = location.id

        command = CommandServingLines()
        command.add_param("mode", "odv")
        command.add_param("locationServerActive", 1)
        command.add_param("type_sl", "stopID")
        command.add_param("name_sl", location)

        if req_types:
            command.add_param("lineReqType", sum(req_types))

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def locations_by_line(self, line: str | Line) -> list[Location]:
        raise NotImplementedError

    async def _run_query(self, query: str) -> str:
        _LOGGER.info(f"Run query {query}")

        async with self._client_session.get(
            query, ssl=False, timeout=QUERY_TIMEOUT
        ) as response:
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
