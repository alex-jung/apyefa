import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Line

_LOGGER = logging.getLogger(__name__)


class CommandGeoObject(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_GEOOBJECT_REQUEST", format)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        locations = data.get("transportations", [])

        _LOGGER.info(f"{len(locations)} location(s) found")

        result = []

        for loc in locations:
            result.append(Line.from_dict(loc))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
                Required("line"): str,
                Optional("boundingBox"): Any("0", "1", 0, 1),
                Optional("boundingBoxLU"): str,
                Optional("boundingBoxRL"): str,
                Optional("filterDate"): Any("0", "1", 0, 1),
            },
        )
