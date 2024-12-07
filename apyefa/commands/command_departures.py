import logging

from voluptuous import Any, Date, Datetime, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import Departure

_LOGGER = logging.getLogger(__name__)


class CommandDepartures(Command):
    def __init__(self, stop: str) -> None:
        super().__init__("XML_DM_REQUEST", "dm")

        self.add_param("name_dm", stop)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        departures = data.get("stopEvents", [])

        _LOGGER.info(f"{len(departures)} departure(s) found")

        result = []

        for departure in departures:
            result.append(Departure.from_dict(departure))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default="WGS84"): Any("WGS84"),
                Required("name_dm"): str,
                Required("type_dm", default="stop"): Any("any", "stop"),
                Required("mode", default="direct"): Any("any", "direct"),
                Optional("itdTime"): Datetime("%M%S"),
                Optional("itdDate"): Date("%Y%m%d"),
                Optional("useAllStops"): Any("0", "1", 0, 1),
                Optional("useRealtime", default=1): Any("0", "1", 0, 1),
                Optional("lsShowTrainsExplicit"): Any("0", "1", 0, 1),
                Optional("useProxFootSearch"): Any("0", "1", 0, 1),
                Optional("deleteAssigendStops_dm"): Any("0", "1", 0, 1),
                Optional("doNotSearchForStops_dm"): Any("0", "1", 0, 1),
                Optional("limit"): int,
            }
        )
