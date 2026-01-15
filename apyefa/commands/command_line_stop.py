import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Location

_LOGGER = logging.getLogger(__name__)


class CommandLineStop(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_LINESTOP_REQUEST", format)

    def parse(self, data: str):
        data_parsed = self._get_parser().parse(data)

        stops = data_parsed.get("locationSequence", [])

        _LOGGER.info(f"{len(stops)} stop(s) found")

        result = []

        for stop in stops:
            result.append(Location.from_dict(stop))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
                Optional("line"): str,
                Optional("allStopInfo"): Any("0", "1", 0, 1),
            }
        )
