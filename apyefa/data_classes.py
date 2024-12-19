from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import IntEnum, StrEnum
from typing import Final, Self

import voluptuous as vol

from apyefa.helpers import parse_date, parse_datetime


# Enums
class LocationType(StrEnum):
    STOP = "stop"
    POI = "poi"
    ADDRESS = "address"
    STREET = "street"
    LOCALITY = "locality"
    SUBURB = "suburb"
    PLATFORM = "platform"
    UNKNOWN = "unknown"


class InfoType(StrEnum):
    AREA_INFO = "areaInfo"
    STOP_INFO = "stopInfo"
    STOP_BLOCKING = "stopBlocking"
    LINE_INFO = "lineInfo"
    LINE_BLOCKING = "lineBlocking"
    ROUTE_INFO = "routeInfo"
    ROUTE_BLOCKING = "routeBlocking"
    GENERAL_INFO = "generalInfo"
    BANNER_INFO = "bannerInfo"
    TRAFFIC_INFO = "trafficInformation"


class InfoPriority(StrEnum):
    VERY_LOW = "veryLow"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "veryHigh"


class TransportType(IntEnum):
    TRAIN = 0  # Zug
    SUBURBAN = 1  # S-Bahn
    SUBWAY = 2  # U-Bahn
    CITY_RAIL = 3  # Stadtbahn
    TRAM = 4  # Straßenbahn
    CITY_BUS = 5  # Stadtbus
    REGIONAL_BUS = 6  # Regionalbus
    EXPRESS_BUS = 7  # Schnellbus
    CABLE_RAIL = 8  # Seilbahn
    FERRY = 9  # Schief
    AST = 10  # Anruf-Sammel-Taxi
    SUSPENSION_RAIL = 11  # Schwebebahn
    AIRPLANE = 12  # Flugzeug
    REGIONAL_TRAIN = 13  # Reginalzug (z.B. IRE, RE und RB)
    NATIONAL_TRAIN = 14  # Nationaler Zug (z.B. IR und D)
    INTERNATINAL_TRAIN = 15  # Internationaler Zug (z.B. IC und EC)
    HIGH_SPEED_TRAIN = 16  # Hochgeschwindigkeitzüge (z.B. ICE)
    RAIL_REPLACEMENT_TRANSPORT = 17  # Schienenersatzverkehr
    SHUTTLE_TRAIN = 18  # Schuttlezug
    CITIZEN_BUS = 19  # Bürgerbus


class LocationFilter(IntEnum):
    NO_FILTER = 0
    LOCATIONS = 1
    STOPS = 2
    STREETS = 4
    ADDRESSES = 8
    INTERSACTIONS = 16
    POIS = 32
    POST_CODES = 64


class LineRequestType(IntEnum):
    NONE = 0
    DEPARTURE_MONITOR = 1
    STOP_TIMETABLE = 2
    TIMETABLE = 4
    ROUTE_MAPS = 8
    STATION_TIMETABLE = 16


class CoordFormat(StrEnum):
    WGS84 = "WGS84[dd.ddddd]"


# Validation schemas
def IsLocationType(type: str):
    if type not in [x.value for x in LocationFilter]:
        raise ValueError


SCHEMA_PROPERTIES = vol.Schema(
    {
        vol.Required("stopId"): str,
        vol.Optional("downloads"): list,
        vol.Optional("area"): str,
        vol.Optional("platform"): str,
        vol.Optional("platformName"): str,
    },
    extra=vol.ALLOW_EXTRA,
)

SCHEMA_LINE_PROPERTIES: Final = vol.Schema(
    {
        vol.Required("globalId"): str,
        vol.Required("isROP"): bool,
        vol.Required("isSTT"): bool,
        vol.Required("isTTB"): bool,
        vol.Required("lineDisplay"): str,
        vol.Required("timetablePeriod"): str,
        vol.Required("tripCode"): int,
        vol.Required("validity"): vol.Schema(
            {
                vol.Required("from"): vol.Date("%Y-%m-%d"),
                vol.Required("to"): vol.Date("%Y-%m-%d"),
            }
        ),
    }
)

SCHEMA_PRODUCT = vol.Schema(
    {
        vol.Required("id"): int,
        vol.Required("class"): int,
        vol.Required("name"): str,
        vol.Optional("iconId"): int,
    }
)

SCHEMA_STOP = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("type"): IsLocationType,
        vol.Optional("id"): str,
    }
)

SCHEMA_PARENT = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("type"): str,
        vol.Optional("id"): str,
        vol.Optional("isGlobalId"): vol.Boolean,
        vol.Optional("disassembledName"): str,
        vol.Optional("parent"): vol.Self,
        vol.Optional("properties"): SCHEMA_PROPERTIES,
    }
)

SCHEMA_OPERATOR = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
        vol.Optional("code"): str,
    }
)

SCHEMA_LOCATION: Final = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("type"): vol.In([x.value for x in LocationType]),
        vol.Optional("id"): str,
        vol.Optional("disassembledName"): str,
        vol.Optional("coord"): list,
        vol.Optional("isGlobalId"): vol.Boolean,
        vol.Optional("isBest"): vol.Boolean,
        vol.Optional("productClasses"): list[vol.Range(min=0, max=10)],
        vol.Optional("parent"): SCHEMA_PARENT,
        vol.Optional("assignedStops"): [vol.Self],
        vol.Optional("properties"): SCHEMA_PROPERTIES,
        vol.Optional("matchQuality"): int,
    },
    extra=vol.ALLOW_EXTRA,
)

SCHEMA_TRANSPORTATION: Final = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
        vol.Required("number"): str,
        vol.Required("product"): SCHEMA_PRODUCT,
        vol.Optional("description"): str,
        vol.Optional("operator"): SCHEMA_OPERATOR,
        vol.Optional("destination"): SCHEMA_LOCATION,
        vol.Optional("origin"): SCHEMA_LOCATION,
        vol.Optional("properties"): dict,
        vol.Optional("disassembledName"): str,
    }
)

SCHEMA_SYSTEM_INFO: Final = vol.Schema(
    {
        vol.Required("version"): str,
        vol.Required("ptKernel"): vol.Schema(
            {
                vol.Required("appVersion"): str,
                vol.Required("dataFormat"): str,
                vol.Required("dataBuild"): str,
            }
        ),
        vol.Required("validity"): vol.Schema(
            {
                vol.Required("from"): vol.Date("%Y-%m-%d"),
                vol.Required("to"): vol.Date("%Y-%m-%d"),
            }
        ),
    }
)

SCHEMA_DEPARTURE: Final = vol.Schema(
    {
        vol.Required("location"): SCHEMA_LOCATION,
        vol.Required("departureTimePlanned"): vol.Datetime("%Y-%m-%dT%H:%M:%S%z"),
        vol.Optional("departureTimeEstimated"): vol.Datetime("%Y-%m-%dT%H:%M:%S%z"),
        vol.Required("transportation"): SCHEMA_TRANSPORTATION,
        vol.Optional("infos"): list,
        vol.Optional("hints"): list,
    },
    extra=vol.ALLOW_EXTRA,
)


@dataclass(frozen=True)
class _Base:
    raw_data: dict = field(repr=False)

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError

    def to_dict(self) -> dict:
        return self.raw_data


# Data classes
@dataclass(frozen=True)
class SystemInfo(_Base):
    version: str
    app_version: str
    data_format: str
    data_build: str
    valid_from: date
    valid_to: date

    _schema = SCHEMA_SYSTEM_INFO

    @classmethod
    def from_dict(cls, data: dict) -> Self | None:
        if not data:
            return None

        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary, provided {type(data)}")

        cls._schema(data)

        return SystemInfo(
            data,
            data.get("version"),
            data.get("ptKernel").get("appVersion"),
            data.get("ptKernel").get("dataFormat"),
            data.get("ptKernel").get("dataBuild"),
            parse_date(data.get("validity").get("from")),
            parse_date(data.get("validity").get("to")),
        )


@dataclass(frozen=True)
class Location(_Base):
    name: str
    loc_type: LocationType
    id: str = ""
    coord: list[int] = field(default_factory=[])
    transports: list[TransportType] = field(default_factory=[])
    parent: Self | None = None
    stops: list[Self] = field(default_factory=[])
    properties: dict = field(default_factory={})
    disassembled_name: str = field(repr=False, default="")
    match_quality: int = field(repr=False, default=0)

    _schema = SCHEMA_LOCATION

    @classmethod
    def from_dict(cls, data: dict) -> Self | None:
        if not data:
            return None

        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary, provided {type(data)}")

        # validate data dictionary
        cls._schema(data)

        name = data.get("name")
        id = data.get("id", "")
        loc_type = LocationType(data.get("type", "unknown"))
        disassembled_name = data.get("disassembledName", None)
        coord = data.get("coord", [])
        match_quality = data.get("matchQuality", 0)
        transports = [TransportType(x) for x in data.get("productClasses", [])]
        properties = data.get("properties", {})
        parent = Location.from_dict(data.get("parent"))
        stops = [Location.from_dict(x) for x in data.get("assignedStops", [])]

        return Location(
            data,
            name,
            loc_type,
            id,
            coord,
            transports,
            parent,
            stops,
            properties,
            disassembled_name,
            match_quality,
        )


@dataclass(frozen=True)
class Departure(_Base):
    location: Location = field(repr=False)
    line_name: str
    route: str
    origin: Location
    destination: Location
    transport: TransportType
    planned_time: datetime
    estimated_time: datetime | None = None
    infos: list[dict] = field(default_factory=[])
    hints: list[dict] = field(default_factory=[])

    _schema = SCHEMA_DEPARTURE

    @classmethod
    def from_dict(cls, data: dict) -> Self | None:
        if not data:
            return None

        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary, provided {type(data)}")

        # validate data dictionary
        cls._schema(data)

        location = Location.from_dict(data.get("location"))
        planned_time = parse_datetime(data.get("departureTimePlanned", None))
        estimated_time = parse_datetime(data.get("departureTimeEstimated", None))
        infos = data.get("infos")
        hints = data.get("hints")

        line = Line.from_dict(data.get("transportation"))
        line_name = line.name
        transport = line.product
        origin = line.origin
        destination = line.destination
        route = line.description

        return Departure(
            data,
            location,
            line_name,
            route,
            origin,
            destination,
            transport,
            planned_time,
            estimated_time,
            infos,
            hints,
        )


@dataclass(frozen=True)
class Line(_Base):
    id: str
    name: str
    description: str
    product: TransportType
    operator: str
    destination: Location
    origin: Location
    properties: dict = field(default_factory={})

    _schema = SCHEMA_TRANSPORTATION

    @classmethod
    def from_dict(cls, data: dict) -> Self | None:
        if not data:
            return None

        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary, provided {type(data)}")

        # validate data dictionary
        cls._schema(data)

        id = data.get("id")
        name = data.get("number")
        # disassembled_name = data.get("disassembledName")
        # number = data.get("number")
        description = data.get("description")
        product = TransportType(data.get("product").get("class"))
        # operator = data.get("operator", None).get("name", None)
        operator = "None"
        destination = Location.from_dict(data.get("destination"))
        origin = Location.from_dict(data.get("origin"))
        properties = data.get("properties", {})

        return Line(
            data,
            id,
            name,
            description,
            product,
            operator,
            destination,
            origin,
            properties,
        )
