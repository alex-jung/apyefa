import logging

from voluptuous import Any, Match, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Location

_LOGGER = logging.getLogger(__name__)


class CommandCoord(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_COORD_REQUEST", format)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        locations = data.get("locations", [])

        _LOGGER.info(f"{len(locations)} location(s) found")

        result = []

        for loc in locations:
            result.append(Location.from_dict(loc))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
                Optional("boundingBox"): Any("0", "1", 0, 1),
                Optional("boundingBoxLU"): str,
                Optional("boundingBoxRL"): str,
                Optional("inclFilter"): Any("0", "1", 0, 1),
                Optional(Match(r"^type_\d{1,}$")): str,
                Optional(Match(r"^radius_\d{1,}$")): int,
                Optional("coord"): str,
                Optional("max"): int,
            },
        )
