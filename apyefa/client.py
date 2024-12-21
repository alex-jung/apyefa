import logging
from datetime import date, datetime
from typing import Final

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

_LOGGER: Final = logging.getLogger(__name__)
QUERY_TIMEOUT: Final = 10  # seconds


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
        """
        Asynchronously search for locations by name with optional filters and limits.

        Args:
            name (str): The name or ID of the location to search for.
            filters (list[LocationFilter], optional): A list of filters to apply to the search. Defaults to an empty list.
            limit (int, optional): The maximum number of locations to return. Defaults to 30.
            search_nearbly_stops (bool, optional): Whether to include nearby stops in the search. Defaults to False.

        Returns:
            list[Location]: A list of locations matching the search criteria.
        """
        _LOGGER.info(f"Request location search by name/id: {name}")
        _LOGGER.debug(f"filters: {filters}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"search_nearbly_stops: {search_nearbly_stops}")

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
        *,
        format: CoordFormat = CoordFormat.WGS84,
        limit: int = 10,
        search_nearbly_stops: bool = False,
    ) -> Location:
        """
        Asynchronously fetches location information based on given coordinates.

        Args:
            coord_x (float): The X coordinate (longitude).
            coord_y (float): The Y coordinate (latitude).
            format (CoordFormat, optional): The coordinate format. Defaults to CoordFormat.WGS84.
            limit (int, optional): The maximum number of locations to return. Defaults to 10.
            search_nearbly_stops (bool, optional): Whether to search for nearby stops. Defaults to False.

        Returns:
            Location: The location information based on the provided coordinates.
        """
        _LOGGER.info("Request location search by coordinates")
        _LOGGER.debug(f"coord_x: {coord_x}")
        _LOGGER.debug(f"coord_y: {coord_y}")
        _LOGGER.debug(f"format: {format}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"search_nearbly_stops: {search_nearbly_stops}")

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
        *,
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

    async def lines_by_name(
        self,
        line: str,
        *,
        merge_directions: bool = False,
        show_trains_explicit: bool = False,
    ) -> list[Line]:
        """
        Asynchronously fetches lines by name.

        Args:
            line (str): The name of the line to search for.
            merge_directions (bool, optional): Whether to merge directions. Defaults to False.
            show_trains_explicit (bool, optional): Whether to explicitly show trains. Defaults to False.

        Returns:
            list[Line]: A list of Line objects matching the search criteria.
        """
        _LOGGER.info("Request lines by name")
        _LOGGER.debug(f"line:{line}")

        command = CommandServingLines(self._format)
        command.add_param("mode", "line")
        command.add_param("lineName", line)
        command.add_param("locationServerActive", 1)
        command.add_param("mergeDir", merge_directions)
        command.add_param("lsShowTrainsExplicit", show_trains_explicit)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def lines_by_location(
        self,
        location: str | Location,
        *,
        req_types: list[LineRequestType] = [],
        merge_directions: bool = False,
        show_trains_explicit: bool = False,
    ) -> list[Line]:
        """
        Fetches lines by location.

        Args:
            location (str | Location): The location identifier or Location object.
            req_types (list[LineRequestType], optional): List of request types for lines. Defaults to [].
            merge_directions (bool, optional): Whether to merge directions. Defaults to False.
            show_trains_explicit (bool, optional): Whether to explicitly show trains. Defaults to False.

        Returns:
            list[Line]: A list of Line objects.

        Raises:
            ValueError: If the location is a Location object and its type is not STOP.
        """
        _LOGGER.info("Request lines by location")
        _LOGGER.debug(f"location:{location}")
        _LOGGER.debug(f"req_types :{req_types}")

        if isinstance(location, Location):
            if location.loc_type != LocationType.STOP:
                raise ValueError(
                    f"Only locations with type Stop are supported, provided {location.loc_type}"
                )
            location = location.id

        command = CommandServingLines(self._format)
        command.add_param("mode", "odv")
        command.add_param("locationServerActive", 1)
        command.add_param("type_sl", "stopID")
        command.add_param("name_sl", location)
        command.add_param("mergeDir", merge_directions)
        command.add_param("lsShowTrainsExplicit", show_trains_explicit)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

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
