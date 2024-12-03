# apyefa
[![Python package](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml/badge.svg)](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Intro
**apyefa** is a python package used to asynchronously fetch data about public transit routing interfaces like [efa.vgn](https://efa.vgn.de/vgnExt_oeffi/"). It can request itineraries for Bus/Tram/Subway etc. connections and return data in a human and machine readable format.
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
Create and activate virtual environment
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

# EfaClient functions
|Function name                                                |Implementation    |Documentation     |
|-------------------------------------------------------------|------------------|------------------|
|[info()](#info)                                              |:white_check_mark:|:white_check_mark:|
|[locations_by_name()](#locations_by_name)                    |:white_check_mark:|:x:               |
|[location_by_coord()](#locations_by_coord)                   |:x:               |:x:               |
|[trip()](#trip)                                              |:x:               |:x:               |
|[departures_by_location()](#departures_by_location)          |:white_check_mark:|:x:               |
|[transportations_by_name()](#transportations_by_name)        |:white_check_mark:|:x:               |
|[transportations_by_location()](#transportations_by_location)|:white_check_mark:|:x:               |
|[locations_by_transportation()](#locations_by_transportation)|:x:               |:x:               |
|[coords()](#coords)                                          |:x:               |:x:               |
|[geo_object()](#geo_object)                                  |:x:               |:x:               |
|[trip_stop_time()](#trip_stop_time)                          |:x:               |:x:               |
|[stop_seq_coord()](#stop_seq_coord)                          |:x:               |:x:               |
|[map_route()](#map_route)                                    |:x:               |:x:               |
|[add_info()](#add_info)                                      |:x:               |:x:               |
|[stop_list()](#stop_list)                                    |:x:               |:x:               |
|[line_list()](#line_list)                                    |:x:               |:x:               |

## info()
Provides end API system information.
### Arguments
None
### Return value
[SystemInfo](#systeminfo)

#### Example request
``` python
from apyefa import EfaClient, SystemInfo

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    info: SystemInfo = await client.info()

    print(info.version)
    print(info.app_version)
    print(info.valid_from)

    # OUTPUT:
    # 10.5.17.3
    # 10.4.30.6 build 16.09.2024 01:30:57
    # datetime.date(2024, 11, 1)
```

### locations_by_name()
Find localities by name or unique id.
### Arguments
|Arguments|Type|Required|Description|
|---------|----|--------|-----------|
|name     |str |required|Name or id ID of locality to search for|
|filters  |list|optional|The localition search may be limited by certain types of objects using this parameter|
### Return value
List of [Locations](#location) sorted by match quility. 

#### Example request
``` python
from apyefa import EfaClient, Location, LocationFilter

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    # Search by stop name
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

    # Search by stop name and limit the list by using filters
    locations: list[Location] = await client.locations_by_name("Plärrer", filters=[LocationFilter.ADDRESSES, LocationFilter.POIS])

    print(len(locations))
    print(location[0].id)
    print(location[0].name)
    print(location[0].loc_type)
    # OUTPUT:
    # Found 4 location(s)
    # poiID:1000029001:9564000:-1:N-PLärrer:Nürnberg:N-PLärrer:ANY:POI:4431934:680416:NAV4:vgn
    # Nürnberg, N-PLärrer
    # <LocationType.POI: 'poi'>

    # Search by stop ID
    locations: list[Location] = await client.locations_by_name("de:09564:704", filters=[LocationFilter.ADDRESSES, LocationFilter.POIS])

    print(len(locations))
    print(location[0].id)
    print(location[0].name)
    print(location[0].loc_type)
    # OUTPUT:
    # Found 1 location(s)
    # de:09564:704
    # Nürnberg, N-PLärrer
    # <LocationType.STOP: 'stop'>
```

### locations_by_coord()
Find location(s) by name.
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    locations: list[Location] = await client.locations_by_coord("9.23:48.80:WGS84[dd.ddddd]")
```

### trip()
### departures_by_location()
### transportations_by_name()
### transportations_by_location()
### coords()
### geo_object()
### trip_stop_time()
### stop_seq_coord()
### map_route()
### add_info()
### stop_list()
### line_list()

## Data Classes
### SystemInfo
|Attribute   |Type|Description  |
|------------|----|------------------------ |
|version     |str |API internal information|
|app_version |str |API internal information |
|data_format |str |API internal information |
|data_build  |str |API internal information |
|valid_from  |date|Start validity date      |
|valid_to    |date|End validity date        |
### Location
|Attribute        |Type               |Description  |
|-----------------|-------------------|-------------|
|name             |str                ||
|loc_type         |LocationType       ||
|id               |str                ||           |
|coord            |list[int]          ||
|transports       |list[TransportType]||
|parent           |Location           ||
|stops            |list[Location]     ||
|properties       |dict               ||
|disassembled_name|date               ||
|match_quality    |int                ||      

## Enums
### TransportType