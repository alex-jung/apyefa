# apyefa
[![Python package](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml/badge.svg)](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Intro
**apyefa** is a python package used to asynchronously fetch public transit routing data via EFA  interfaces like [efa.vgn](https://efa.vgn.de/vgnExt_oeffi/"). It can request itineraries for Bus/Trams/Subways etc. connections and return data in a human and machine readable format.
# Installation
You only need to install the **apyefa** package, for example using pip:
``` bash
pip install apyefa
```

# Restrictions
Currently the package supports only endpoints using [RapidJSON](https://rapidjson.org/) format. To check whether the endpoint supports this format, please call:
``` bash
To describe(!)
```

# Development setup
Create and activate virtual environment. Then install dependencies required by `apefa` package.
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

# EfaClient functions
|Function name                                       |Implementation    |Documentation     |
|----------------------------------------------------|------------------|------------------|
|[info()](#info)                                     |:white_check_mark:|:white_check_mark:|
|[locations_by_name()](#locations_by_name)           |:white_check_mark:|:white_check_mark:|
|[location_by_coord()](#locations_by_coord)          |:white_check_mark:|:white_check_mark:|
|[trip()](#trip)                                     |:x:               |:x:               |
|[departures_by_location()](#departures_by_location) |:white_check_mark:|:white_check_mark:|
|[lines_by_name()](#lines_by_name)                   |:white_check_mark:|:white_check_mark:|
|[lines_by_location()](#lines_by_location)           |:white_check_mark:|:white_check_mark:|
|[locations_by_line()](#locations_by_line) |:x:               |:x:               |
|[coords()](#coords)                                 |:x:               |:x:               |
|[geo_object()](#geo_object)                         |:x:               |:x:               |
|[trip_stop_time()](#trip_stop_time)                 |:x:               |:x:               |
|[stop_seq_coord()](#stop_seq_coord)                 |:x:               |:x:               |
|[map_route()](#map_route)                           |:x:               |:x:               |
|[add_info()](#add_info)                             |:x:               |:x:               |
|[stop_list()](#stop_list)                           |:x:               |:x:               |
|[line_list()](#line_list)                           |:x:               |:x:               |

## info()
Provides end API system information.

### Arguments
None

### Return value
|Type|Description|
|----|-----------|
|[SystemInfo](#systeminfo)|System information object|

### Example request
``` python
from apyefa import EfaClient, SystemInfo
from pprint import pprint

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    info: SystemInfo = await client.info()

    pprint(info)

    # OUTPUT:
    # SystemInfo(version='10.6.14.22',
    #            app_version='10.4.30.6 build 16.09.2024 01:30:57',
    #            data_format='EFA10_04_00',
    #            data_build='2024-12-02T16:53:02Z',
    #            valid_from=datetime.date(2024, 11, 1),
    #            valid_to=datetime.date(2025, 12, 13))
```

## locations_by_name()
Find localities by name or unique id.

### Arguments
|Name     |Type                |Required|Description|
|---------|--------------------|--------|-----------|
|name     |str                 |required|Name or id ID of locality to search for|
|filters  |list[[LocationFilter](#locationfilter)]|optional|The localition search may be limited by certain types of objects using this parameter. Default value is `[]`|
|limit    |int                 |optional|Max size of returned list. Default value is `30`|

### Return value
|Type|Description|
|----|-----------|
|list[[Location](#location)]|List of locations found py provided name sorted by match quality|


### Examples
1. Search for all localities contain name `Plärrer`
``` python
from apyefa import EfaClient, Location, LocationFilter

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    locations: list[Location] = await client.locations_by_name("Plärrer")

    print(f"Found {len(locations)} location(s)")
    print(location[0].id)
    print(location[0].name)
    print(location[0].loc_type)
    # OUTPUT:
    # Found 20 location(s)
    # de:09574:7132
    # Hersbruck, Plärrer
    # <LocationType.STOP: 'stop'>
```
2. Search for POIs and Addresses with name `Plärrer`
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    locations: list[Location] = await client.locations_by_name("Plärrer", filters=[LocationFilter.ADDRESSES, LocationFilter.POIS])
    
    print(f"Found {len(locations)} location(s)")
    print(location[0].id)
    print(location[0].name)
    print(location[0].loc_type)

    # OUTPUT:
    # Found 4 location(s)
    # poiID:1000029001:9564000:-1:N-PLärrer:Nürnberg:N-PLärrer:ANY:POI:4431934:680416:NAV4:vgn
    # Nürnberg, N-PLärrer
    # <LocationType.POI: 'poi'>
```
3. Search by `stop id`
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    locations: list[Location] = await client.locations_by_name("de:09564:704")

    print(f"Found {len(locations)} location(s)")
    print(location[0].id)
    print(location[0].name)
    print(location[0].loc_type)
    # OUTPUT:
    # Found 1 location(s)
    # de:09564:704
    # Nürnberg, N-PLärrer
    # <LocationType.STOP: 'stop'>
```

## locations_by_coord()
Find localities by coordinates.

> :x: Currently test endpoint does not sent any answers for this request

### Arguments
|Arguments|Type                |Required|Description|
|---------|--------------------|--------|-----------|
|coord_x  |float               |required|X-coordinate|
|coord_y  |float               |required|Y-coordinate|
|format   |[CoordFormat](#coordformat)|optional|Coordinates format used for request|
|limit    |int                 |optional|Max size of returned list. Default value is `10`|

### Return value
|Type|Description|
|----|-----------|
|list[[Location](#location)]|List of locations found py provided name sorted by match quality|

## trip()

## departures_by_location()
Find all departures for a specific location

### Arguments
|Arguments|Type                |Required|Description|
|---------|--------------------|--------|-----------|
|stop     |[Location](#location) \| str |required|Location for which the departures are being sought|
|limit    |int                 |optional|Max size of returned list. Default value is `40`|
|date     |str                 |optional|Date/time for which the departures are sought in format "YYYYMMDD hh:mm", "YYYYMMDD" or "mm:hh". Default value is `empty`|

### Return value
|Type|Description|
|----|-----------|
|list[[Departure](#departure)]|List of departures sorted by departure time|

### Examples
``` python
from apyefa import EfaClient, Departure

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    departures: list[Departure] = await client.departures_by_location("de:09564:704", limit=3, date="22:13")

    print(f"Found {len(departures)} departure(s)")
    print(location[0].line_name)
    print(location[0].route)
    print(location[0].transport)
    print(location[0].planned_time)
    # OUTPUT:
    # Found 3 departure(s)
    # U3
    # Nordwestring - Hauptbahnhof - Plärrer - Großreuth bei Schweinau
    # <TransportType.SUBWAY: 2>
    # datetime.datetime(2024, 12, 7, 22, 16, tzinfo=zoneinfo.ZoneInfo(key='Europe/Berlin'))
```

## lines_by_name()
Find lines by name.

### Arguments
|Arguments|Type                |Required|Description|
|---------|--------------------|--------|-----------|
|name  |str               |required|Name of the line to search. e.g. `U1` or `67`|

### Return value
|Type|Description|
|----|-----------|
|list[[Line](#line)]|List of lines found for provided name|

> NOTE: The attribute `origin` of returned `line` objects is None

### Examples
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    lines: list[Line] = await client.lines_by_name("U1")

    print(f"Found {len(lines)} line(s)")
    print(f"id         : {lines[0].id}")
    print(f"name       : {lines[0].name}")
    print(f"description: {lines[0].description}")
    print(f"product    : {lines[0].product}")

    # OUTPUT:
    # Found 4 line(s)
    # id         : vgn:11001: :H:j24
    # name       : U1
    # description: Fürth Hardhöhe - Nürnberg Plärrer - Hauptbahnhof - Langwasser Süd
    # product    : <TransportType.SUBWAY: 2> 
```

## lines_by_location()
Find lines pass provided location.

### Arguments
|Arguments|Type                |Required|Description|
|---------|--------------------|--------|-----------|
|location |str \| [Location](#location) |required|The location passed by searched line(s)|

### Return value
|Type|Description|
|----|-----------|
|list[[Line](#line)]|List of lines found for provided location|

> The attribute `origin` of returned `line` objects is None

### Examples
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    lines: list[Line] = await client.lines_by_location("de:09564:704")

    print(f"Found {len(lines)} line(s)")
    print(f"id         : {lines[0].id}")
    print(f"name       : {lines[0].name}")
    print(f"description: {lines[0].description}")
    print(f"product    : {lines[0].product}")

    # OUTPUT:
    # Found 10 line(s)
    # id         : vgn:33283: :H:j24
    # name       : 283
    # description: Hugenottenplatz - St. Johann - Dechsendorfer Weiher
    # product    : <TransportType.BUS: 5> 
```

## coords()
## geo_object()
## trip_stop_time()
## stop_seq_coord()
## map_route()
## add_info()
## stop_list()
## line_list()

# Data Classes
## SystemInfo
|Attribute   |Type|Description  |
|------------|----|------------------------ |
|version     |str |API internal information|
|app_version |str |API internal information |
|data_format |str |API internal information |
|data_build  |str |API internal information |
|valid_from  |date|Start validity date      |
|valid_to    |date|End validity date        |

## Location
|Attribute        |Type               |Description  |
|-----------------|-------------------|-------------|
|name             |str                |Name of location e.g. `Nürnberg, Nordostbahnhof`|
|loc_type         |[LocationType](#locationtype)|Type of location e.g. `STOP` or `POI`|
|id               |str                |Location unique id|
|coord            |list[int]          |Location coordinates|
|transports       |list[[TransportType](#transporttype)]|Transport type(s) this location pass|
|parent           |[Location](#location) \| None|Parent location|
|stops            |list[[Location](#location)]|Location with type `STOP` assigned to this location|
|properties       |dict               |API internal information|

## Departure
|Attribute      |Type|Description              |
|---------------|----|------------------------|
|location       |[Location](#location) |Location of departure|
|line_name      |str |Line name e.g. `U3`|
|route          |str |The complete route name from origin to destination stops e.g. `Nordwestring - Hauptbahnhof - Plärrer - Großreuth bei Schweinau`|
|origin         |[Location](#location)|Origin location|
|destination    |[Location](#location)|Destination location|
|transport      |[TransportType](#transporttype)|Transport type e.g. `Bus` or `Subway`|
|planned_time   |datetime|Planned departure time|
|estimated_time |datetime \| None|Estimated departure time(will be provided by endpoits supporting real time mode)|
|infos          |list[dict] \| None|List of ICS messages|

## Line
|Attribute   |Type|Description              |
|------------|----|------------------------ |
|id          |str |Line id                  |
|name        |str |Line name                |
|description |str |Route name               |
|product     |[TransportType](#transporttype) |Type of transportation. Bus, Subway etc.|
|destination |[Location](#location)|Line destination location|
|origin      |[Location](#location) \| None|Line start location|
|properties  |dict|Additional properties    |

# Enums
## TransportType
```python
class TransportType(IntEnum):
    RAIL        = 0 
    SUBURBAN    = 1
    SUBWAY      = 2 
    CITY_RAIL   = 3 
    TRAM        = 4
    BUS         = 5 
    RBUS        = 6 
    EXPRESS_BUS = 7
    CABLE_TRAM  = 8
    FERRY       = 9 
    AST         = 10  # Anruf-Sammel-Taxi
```

## CoordFormat
```python
class CoordFormat(StrEnum):
    WGS84 = "WGS84 [dd.ddddd]"
```

## LocationFilter
```python
class LocationFilter(IntEnum):
    NO_FILTER     = 0
    LOCATIONS     = 1
    STOPS         = 2
    STREETS       = 4
    ADDRESSES     = 8
    INTERSACTIONS = 16
    POIS          = 32
    POST_CODES    = 64
```

## LocationType
```python
class LocationType(StrEnum):
    STOP     = "stop"
    POI      = "poi"
    ADDRESS  = "address"
    STREET   = "street"
    LOCALITY = "locality"
    SUBURB   = "suburb"
    PLATFORM = "platform"
    UNKNOWN  = "unknown"
```