import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Jorney

_LOGGER = logging.getLogger(__name__)


class CommandTrip(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_TRIP_REQUEST2", format)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        journeys = data.get("journeys", [])

        _LOGGER.info(f"{len(journeys)} journey(s) found")

        result = []

        for jorney in journeys:
            result.append(Jorney.from_dict(jorney))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default="WGS84"): Any(
                    *[x.value for x in CoordFormat]
                ),
                Required("locationServerActive", default="1"): Any("0", "1", 0, 1),
                Required("itdTripDateTimeDepArr", default="dep"): Any("dep", "arr"),
                Required("type_origin", default="any"): Any("any", "coord"),
                Required("name_origin"): str,
                Required("type_destination", default="any"): Any("any", "coord"),
                Required("name_destination"): str,
                Optional("type_via", default="any"): Any("any", "coord"),
                Optional("name_via"): str,
                Optional("useUT"): Any("0", "1", 0, 1),
                Optional("useRealtime"): Any("0", "1", 0, 1),
                Optional("deleteAssignedStops_origin"): Any("0", "1", 0, 1),
                Optional("deleteAssignedStops_destination"): Any("0", "1", 0, 1),
                Optional("genC"): Any("0", "1", 0, 1),
                Optional("genP"): Any("0", "1", 0, 1),
                Optional("genMaps"): Any("0", "1", 0, 1),
                Optional("allInterchangesAsLegs"): Any("0", "1", 0, 1),
                Optional("calcOneDirection"): Any("0", "1", 0, 1),
                Optional("changeSpeed"): str,
                Optional("coordOutputDistance"): Any("0", "1", 0, 1),
            }
        )
