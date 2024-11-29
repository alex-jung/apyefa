# apyefa
[![Python package](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml/badge.svg)](https://github.com/alex-jung/apyefa/actions/workflows/python-package.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Installation

# Known EFA endpoints
* [Verkehrsverbund Großraum Nürnberg](https://efa.vgn.de/vgnExt_oeffi/) (VGN)
* [Verkehrsverbund Rhein-Ruhr](https://efa.vrr.de/vrr/) (VRR)

# Features
## System info
Get API system information
``` python
info: SystemInfo = None

async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
    info = await client.info()

print(info.version)
print(info.data_format)
print(info.valid_from)
print(info.valid_to)
```
Output:
```python

```
## Find stop

## Get departures

# Usage
``` python
import asyncio
from apyefa import EfaClient
from pprint import pprint

async def main():
    async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
        result = await asyncio.gather(
            client.info(),
            client.stops("Nürnberg Plärrer"),
            client.departures("de:09564:704", limit=10, date="20241126 16:30"),
        )

    print("System Info".center(60, "-"))
    pprint(result[0])

    print("Plärrer stops".center(60, "-"))
    pprint(result[1])

    print("Plärrer departures - 26 Nov. 16:30".center(60, "-"))
    pprint(result[2])

if __name__ == "__main__":
    asyncio.run(main())
```

# Open points
* Implement find stop by coordinates
* Implementd xml parsing for APIs not supporting rapid JSON

# Documentation
> s. pydoc in code