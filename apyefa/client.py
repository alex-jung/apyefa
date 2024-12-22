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
    InfoPriority,
    InfoType,
    Line,
    LineRequestType,
    Location,
    LocationFilter,
    LocationType,
    SystemInfo,
)
from apyefa.exceptions import EfaConnectionError, EfaFormatNotSupported

from .commands.command_add_info import CommandAdditionalInfo
from .commands.command_line_list import CommandLineList

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

        Raises:
            ValueError: If no name is provided.

        Returns:
            list[Location]: A list of locations matching the search criteria.
        """
        _LOGGER.info(f"Request location search by name/id: {name}")
        _LOGGER.debug(f"filters: {filters}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"search_nearbly_stops: {search_nearbly_stops}")

        if not name:
            raise ValueError("No name provided")

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

    async def lines(
        self,
        branch_code: str | None = None,
        net_branch_code: str | None = None,
        sub_network: str | None = None,
        list_omc: str | None = None,
        mixed_lines: bool = False,
        merge_dir: bool = False,
        req_type: list[LineRequestType] = [],
    ) -> list[Location]:
        _LOGGER.info("Request lines")

        command = CommandLineList(self._format)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        if branch_code:
            command.add_param("lineListBranchCode", branch_code)
        if net_branch_code:
            command.add_param("lineListNetBranchCode", net_branch_code)
        if sub_network:
            command.add_param("lineListSubnetwork", sub_network)
        if list_omc:
            command.add_param("lineListOMC", list_omc)
        if mixed_lines:
            command.add_param("lineListMixedLines", mixed_lines)
        if merge_dir:
            command.add_param("mergeDir", merge_dir)
        if req_type:
            command.add_param("lineReqType", sum(req_type))

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def trip(self):
        raise NotImplementedError

    async def departures_by_location(
        self,
        location: Location | str,
        *,
        limit=40,
        arg_date: str | datetime | date | None = None,
        realtime: bool = True,
    ) -> list[Departure]:
        """
        Fetches departures for a given location.

        Args:
            location (Location | str): The location object or location ID as a string.
            limit (int, optional): The maximum number of departures to return. Defaults to 40.
            arg_date (str | datetime | date | None, optional): The date for which to fetch departures. Can be a string, datetime, date, or None. Defaults to None.
            realtime (bool, optional): Whether to use real-time data. Defaults to True.

        Returns:
            list[Departure]: A list of Departure objects.

        Raises:
            ValueError: If no location is provided.
        """
        _LOGGER.info(f"Request departures for location {location}")
        _LOGGER.debug(f"limit: {limit}")
        _LOGGER.debug(f"date: {arg_date}")

        if not location:
            raise ValueError("No location provided")

        if isinstance(location, Location):
            location = location.id

        command = CommandDepartures(self._format)

        # add parameters
        command.add_param("locationServerActive", 1)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)
        command.add_param("name_dm", location)
        command.add_param("type_dm", "any")

        if self._format == "rapidJSON":
            command.add_param("mode", "direct")
            command.add_param("useProxFootSearch", "0")
        else:
            command.add_param("mode", "any")

        command.add_param("useAllStops", "1")
        command.add_param("lsShowTrainsExplicit", "1")
        command.add_param("useRealtime", realtime)

        command.add_param_datetime(arg_date)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)[:limit]

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

        Raises:
            ValueError: If no line is provided.

        Returns:
            list[Line]: A list of Line objects matching the search criteria.
        """
        _LOGGER.info("Request lines by name")
        _LOGGER.debug(f"line:{line}")

        if not line:
            raise ValueError("No line provided")

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

        if not location:
            raise ValueError("No location provided")

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

    async def additional_info_line(
        self,
        incl_history: bool = False,
        only_valid: bool = False,
        filter_date: date | str | None = None,
        info_types: list[InfoType] = [],
        prio: list[InfoPriority] = [],
        mot_types: list[str] = [],
        operatos: list[str] = [],
        lines: list[str] = [],
        networks: list[str] = [],
        pn_lines: list[str] = [],
        pn_line_directions: list[str] = [],
        line: str | None = None,
        passed_stops: int = 0,
        id_stops: list[str] = [],
        info_id: str | None = None,
        show_line_list: bool = False,
        show_stop_list: bool = False,
        show_place_list: bool = False,
    ):
        _LOGGER.info("Request additional info")

        command = CommandAdditionalInfo(self._format)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        if not incl_history:
            command.add_param("filterPublished", "1")
        if only_valid:
            command.add_param("filterValid", "1")
        if filter_date:
            command.add_param("filterDateValid", filter_date)

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def additional_info_stop(self):
        pass

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
