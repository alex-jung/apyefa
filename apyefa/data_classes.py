from dataclasses import dataclass, field
from datetime import date, datetime
from enum import IntEnum, StrEnum


class StopType(StrEnum):
    STOP = "stop"
    POI = "poi"
    ADDRESS = "address"
    STREET = "street"
    LOCALITY = "locality"
    SUBURB = "suburb"
    PLATFORM = "platform"


class TransportType(IntEnum):
    RAIL = 0  # RB
    SUBURBAN = 1  # S-Bahn
    SUBWAY = 2  # U-Bahn
    CITY_RAIL = 3  # Stadtbahn
    TRAM = 4  # Straßenbahn
    BUS = 5  # Bus
    RBUS = 6  # Regional Bus
    EXPRESS_BUS = 7  # Schnellbus
    CABLE_TRAM = 8  # Seilbahn
    FERRY = 9  # Schief
    AST = 10  # Anruf-Sammel-Taxi


class StopFilter(IntEnum):
    NO_FILTER = 0
    LOCATIONS = 1
    STOPS = 2
    STREETS = 4
    ADDRESSES = 8
    INTERSACTIONS = 16
    POIS = 32
    POST_CODES = 64


@dataclass
class SystemInfo:
    version: str
    data_format: str
    valid_from: date
    valid_to: date


@dataclass
class Stop:
    id: str
    name: str
    type: StopType
    disassembled_name: str = field(repr=False, default="")
    coord: list[int] = field(default_factory=list)
    transports: list[TransportType] = field(default_factory=list)


@dataclass
class Departure:
    line_name: str
    route: str
    origin: Stop
    destination: Stop
    transport: TransportType
    planned_time: datetime
    estimated_time: datetime | None
    infos: list[dict]
