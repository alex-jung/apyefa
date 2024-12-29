import logging

from voluptuous import Any, Optional, Range, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Line, LineRequestType

_LOGGER = logging.getLogger(__name__)


class CommandServingLines(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_SERVINGLINES_REQUEST", format)

    def parse(self, data: dict) -> list[Line]:
        data = self._get_parser().parse(data)

        lines = data.get("lines", [])

        _LOGGER.info(f"{len(lines)} line(s) found")

        result = []

        for line in lines:
            result.append(Line.from_dict(line))

        return result

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
                Required("locationServerActive", default="1"): Any("0", "1", 0, 1),
                Required("mode", default="line"): Any("odv", "line"),
                # mode 'odv'
                Optional("type_sl"): Any("stopID"),
                Optional("name_sl"): str,
                # mode 'line'
                Optional("lineName"): str,
                Optional("lineReqType"): Range(
                    min=0, max=sum([x.value for x in LineRequestType])
                ),
                Optional("mergeDir"): Any("0", "1", 0, 1),
                Optional("lsShowTrainsExplicit"): Any("0", "1", 0, 1),
                Optional("line"): str,
                # Optional("doNotSearchForStops_sf"): Any("0", "1", 0, 1),
                # Optional("anyObjFilter_origin"): Range(
                #    min=0, max=sum([x.value for x in StopFilter])
                # ),
            }
        )
