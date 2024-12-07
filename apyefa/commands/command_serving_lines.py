import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import Line

_LOGGER = logging.getLogger(__name__)


class CommandServingLines(Command):
    def __init__(self, mode: str, value: str) -> None:
        super().__init__("XML_SERVINGLINES_REQUEST", "servingLines")

        match mode:
            case "odv":
                self.add_param("type_sl", "stopID")
                self.add_param("name_sl", value)
            case "line":
                self.add_param("lineName", value)
            case _:
                raise ValueError(f"Mode {mode} not supported for serving lines")

        self.add_param("mode", mode)

    def parse(self, data: dict) -> list[Line]:
        data = self._get_parser().parse(data)

        transportations = data.get("lines", [])

        _LOGGER.info(f"{len(transportations)} transportation(s) found")

        result = []

        for t in transportations:
            result.append(Line.from_dict(t))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default="WGS84"): Any("WGS84"),
                Required("mode", default="line"): Any("odv", "line"),
                # mode 'odv'
                Optional("type_sl"): Any("stopID"),
                Optional("name_sl"): str,
                # mode 'line'
                Optional("lineName"): str,
                Optional("lineReqType"): int,
                Optional("mergeDir"): Any("0", "1", 0, 1),
                Optional("lsShowTrainsExplicit"): Any("0", "1", 0, 1),
                Optional("line"): str,
                # Optional("doNotSearchForStops_sf"): Any("0", "1", 0, 1),
                # Optional("anyObjFilter_origin"): Range(
                #    min=0, max=sum([x.value for x in StopFilter])
                # ),
            }
        )
