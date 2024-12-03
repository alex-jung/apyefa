# apyefa
[![Python package](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml/badge.svg)](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## Intro
**apyefa** package used to asynchronously fetch data about public transport like departures, locations etc.
## Installation
You only need to install the **apyefa** package, for example using pip:
``` bash
pip install apyefa
```

## Restirctions
Currently the package supports only [RapidJSON](https://rapidjson.org/) format. To check whether your end api supports this format, please call:
``` bash
To describe(!)
```

## Development setup
Create and activate virtual environment
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## EfaClient functions
|Function                                                     |Implementation    |Documentation     |
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

### info()
Get end API system information
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    info: SystemInfo = await client.info()
```
**SystemInfo** attributes:
```python
version: str
app_version: str
data_format: str
data_build: str
valid_from: date
valid_to: date
```

### locations_by_name()
Find localities by name and id.
``` python
async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    locations: list[Location] = await client.locations_by_name("Plärrer")
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

