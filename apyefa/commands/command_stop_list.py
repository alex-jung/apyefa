import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Location

_LOGGER = logging.getLogger(__name__)


class CommandStopList(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_STOPLIST_REQUEST", format)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        locations = data.get("locations", [])

        _LOGGER.info(f"{len(locations)} location(s) found")

        result = []

        for location in locations:
            result.append(Location.from_dict(location))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
                Optional("stopListOMC"): str,
                Optional("stopListPlaceId"): str,
                Optional("stopListOMCPlaceId"): str,
                Optional("rTN"): str,
                Optional("stopListSubnetwork"): str,
                Optional("fromstop"): str,
                Optional("tostop"): str,
                Optional("servingLines"): Any("0", "1", 0, 1),
                Optional("servingLinesMOTType"): Any("0", "1", 0, 1),
                Optional("servingLinesMOTTypes"): Any("0", "1", 0, 1),
                Optional("tariffZones"): Any("0", "1", 0, 1),
            }
        )
