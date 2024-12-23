import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command

from ..data_classes import CoordFormat

_LOGGER = logging.getLogger(__name__)


class CommandTrip(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_TRIP_REQUEST2", format)

    def parse(self, data: dict):
        raise NotImplementedError

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default="WGS84"): Any(
                    *[x.value for x in CoordFormat]
                ),
                Required("type_origin", default="any"): Any("any", "coord"),
                Required("name_origin"): str,
                Required("type_destination", default="any"): Any("any", "coord"),
                Required("name_destination"): str,
                Optional("type_via", default="any"): Any("any", "coord"),
                Optional("name_via"): str,
                Optional("useUT"): Any("0", "1", 0, 1),
                Optional("useRealtime"): Any("0", "1", 0, 1),
            }
        )
