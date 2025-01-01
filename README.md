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
curl <EFA API URL>/XML_SYSTEMINFO_REQUEST?outputFormat=rapidJSON
e.g. curl https://bahnland-bayern.de/efa/XML_SYSTEMINFO_REQUEST?outputFormat=rapidJSON
```
If API's answer looks like this, endpoint supports rapidJSON:
```
{"version":"10.6.21.17","ptKernel":{"appVersion":"10.6.22.28 build 16.12.2024 11:14:57","dataFormat":"EFA10_06_01","dataBuild":"2024-12-31T00:54:55Z"},"validity":{"from":"2024-12-15","to":"2025-06-14"}}
```

# Development setup
Create and activate virtual environment. Then install dependencies required by `apefa` package.
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

# apyefa functions
|Function Name                                                |Description|
|----------------------------------------------------|-----------|
|[info()](https://github.com/alex-jung/apyefa/wiki/info)|Provides EFA endpoint system information|
|[locations_by_name()](https://github.com/alex-jung/apyefa/wiki/locations_by_name)|Search for locations by name with optional filters and limits|
|[location_by_coord()](https://github.com/alex-jung/apyefa/wiki/location_by_coord)|Search for location by it's coordinates|
|[list_lines()](https://github.com/alex-jung/apyefa/wiki/list_lines)|Retrieves a list of lines|
|[list_stops()](https://github.com/alex-jung/apyefa/wiki/list_stops)|Retrieves a list of stops|
|[trip()](https://github.com/alex-jung/apyefa/wiki/trip)|Calculates a trip between an origin and a destination locations|
|[departures_by_location()](https://github.com/alex-jung/apyefa/wiki/departures_by_location)|Fetches departures for a given location|
|[lines_by_name()](https://github.com/alex-jung/apyefa/wiki/lines_by_name)|Fetches lines by name|
|[lines_by_location()](https://github.com/alex-jung/apyefa/wiki/lines_by_location)|Fetches lines for a specific location|
|[line_stops()](https://github.com/alex-jung/apyefa/wiki/line_stops)|Retrieves the stops for a given line|
|[coord_bounding_box()](https://github.com/alex-jung/apyefa/wiki/coord_bounding_box)|Requests locations within a bounding box|
|[coord_radial()](https://github.com/alex-jung/apyefa/wiki/coord_radial)|Requests locations within a radius|
|[geo_object()](https://github.com/alex-jung/apyefa/wiki/geo_object)|Generates a sequence of coordinates and all passed stops of a provided line|


# Example
``` python
import asyncio
from apyefa import EfaClient
from apyefa.data_classes import (
    Location,
    LocationFilter,
)

async def async_info(client: EfaClient):
    info = await client.info()
    print(info)

async def async_location_by_name(client: EfaClient):
    stops: list[Location] = await client.locations_by_name(
        "Plärrer", filters=[LocationFilter.STOPS], limit=20
    )
    for s in stops:
        print(s)    

async def main():
    async with EfaClient("https://bahnland-bayern.de/efa/") as client:
        await asyncio.gather(
            async_info(client),
            async_location_by_name(client),
        )

if __name__ == "__main__":
    asyncio.run(main())
```
