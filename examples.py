import asyncio
from pprint import pprint

from apyefa import EfaClient, LocationFilter


async def main():
    async with EfaClient("https://efa.vgn.de/vgnExt_oeffi/") as client:
        result = await asyncio.gather(
            client.info(),
            client.locations_by_name("Nürnberg Plärrer"),
            client.locations_by_name("Nordostbahnhof", filters=[LocationFilter.STOPS]),
            client.departures_by_location(
                "de:09564:704", limit=10, date="20241126 16:30"
            ),
        )

    print("System Info".center(60, "-"))
    pprint(result[0])

    print("Plärrer stops".center(60, "-"))
    pprint(result[1])

    print("Nordostbahnhof stops".center(60, "-"))
    pprint(result[2])

    print("Plärrer departures - 26 Nov. 16:30".center(60, "-"))
    pprint(result[3])


if __name__ == "__main__":
    asyncio.run(main())
