import logging
from datetime import date, datetime
from typing import Final

import aiohttp

from apyefa.commands import (
    Command,
    CommandAdditionalInfo,
    CommandDepartures,
    CommandLineList,
    CommandLineStop,
    CommandServingLines,
    CommandStopFinder,
    CommandStopList,
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

_LOGGER: Final = logging.getLogger(__name__)
QUERY_TIMEOUT: Final = 30  # seconds


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

    async def list_lines(
        self,
        branch_code: str | None = None,
        net_branch_code: str | None = None,
        sub_network: str | None = None,
        list_omc: str | None = None,
        mixed_lines: bool = False,
        merge_directions: bool = True,
        req_types: list[LineRequestType] = [],
    ) -> list[Line]:
        """
        Asynchronously retrieves a list of lines based on the provided parameters.

        Args:
            branch_code (str | None): The branch code to filter lines.
            net_branch_code (str | None): The Network and optionally the code of the branch separated by colon.
            sub_network (str | None): The sub-network to filter lines.
            list_omc (str | None): The OMC(Open Method of Coordination) list to filter lines.
            mixed_lines (bool): Activates the search of composed services. Defaults to False.
            merge_directions (bool): Merges the inbound and outbound service. Thus only inbound services are listed. Defaults to True.
            req_type (list[LineRequestType]): The request types to filter lines. Defaults to an empty list.

        Returns:
            list[Line]: A list of Line objects representing the lines.
        """
        _LOGGER.info("Request lines")
        _LOGGER.debug(f"branch_code: {branch_code}")
        _LOGGER.debug(f"net_branch_code: {net_branch_code}")
        _LOGGER.debug(f"sub_network: {sub_network}")
        _LOGGER.debug(f"list_omc: {list_omc}")
        _LOGGER.debug(f"mixed_lines: {mixed_lines}")
        _LOGGER.debug(f"merge_directions: {merge_directions}")
        _LOGGER.debug(f"req_types: {req_types}")

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
        if not merge_directions:
            command.add_param("mergeDir", merge_directions)
        if req_types:
            command.add_param("lineReqType", sum(req_types))

        response = await self._run_query(self._build_url(command))

        return command.parse(response)

    async def list_stops(
        self,
        omc: str | None = None,
        place_id: str | None = None,
        omc_place_id: str | None = None,
        rtn: str | None = None,
        sub_network: str | None = None,
        from_stop: str | None = None,
        to_stop: str | None = None,
        serving_lines: bool = True,
        serving_lines_mot_type: bool = True,
        serving_lines_mot_types: bool = False,
        tarif_zones: bool = True,
    ) -> list[Location]:
        """
        Asynchronously retrieves a list of stops based on the provided parameters.

        Args:
            omc (str | None): Optional. The OMC (Operational Management Center) code.
            place_id (str | None): Optional. ID of the place. Can be combined with `omc`.
            omc_place_id (str | None): Optional. Combination of `omc` and `place_id`. OMC and ID of the place are separated by colon.
            rtn (str | None): Optional. Only stops within the network given by parameter value.
            sub_network (str | None): Optional. Only stops served by services from the network given by parameter value.
            from_stop (str | None): Optional. Only stops with IDs within the intervall restricted by these parameters. Must be combined with `to_stop`.
            to_stop (str | None): Optional. Only stops with IDs within the intervall restricted by these parameters. Must be combined with `from_stop`.
            serving_lines (bool): Optional. Services of each stop. Default is True.
            serving_lines_mot_type (bool): Optional. Mayor means of transport of each stop. The combination with `serving_lines_mot_types=True` is not possible. Default is True.
            serving_lines_mot_types (bool): Optional. All means of transport of each stop. Separated by comma. The combination with `serving_lines_mot_type=True` is not possible. Default is False.
            tarif_zones (bool): Optional. Tariff zone of each stop. Default is True.

        Returns:
            The parsed response from the command execution.
        """
        command = CommandStopList(self._format)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)

        if omc:
            command.add_param("stopListOMC", omc)
        if place_id:
            command.add_param("stopListPlaceId", place_id)
        if omc_place_id:
            command.add_param("stopListOMCPlaceId", omc_place_id)
        if rtn:
            command.add_param("rTN", rtn)
        if sub_network:
            command.add_param("stopListSubnetwork", sub_network)
        if from_stop:
            command.add_param("fromstop", from_stop)
        if to_stop:
            command.add_param("tostop", to_stop)

        command.add_param("servingLines", serving_lines)
        command.add_param("servingLinesMOTType", serving_lines_mot_type)
        command.add_param("servingLinesMOTTypes", serving_lines_mot_types)
        command.add_param("tariffZones", tarif_zones)

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

    async def line_stops(
        self, line_name: str, additional_info: bool = False
    ) -> list[Location]:
        """
        Retrieve the stops for a given line.

        Args:
            line_name (str): The name of the line for which to retrieve stops.
            additional_info (bool, optional): Whether to include additional stop information. Defaults to False.

        Returns:
            list[Location]: A list of Location objects representing the stops for the specified line.
        """
        _LOGGER.info("Request lise stops")
        _LOGGER.debug(f"line_name: {line_name}")

        if not line_name:
            raise ValueError("No line name provided")

        command = CommandLineStop(self._format)
        command.add_param("coordOutputFormat", CoordFormat.WGS84.value)
        command.add_param("line", line_name)
        command.add_param("allStopInfo", additional_info)

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
