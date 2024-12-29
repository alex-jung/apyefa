import logging

from voluptuous import Any, Optional, Range, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, Line, LineRequestType

_LOGGER = logging.getLogger(__name__)


class CommandLineList(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_LINELIST_REQUEST", format)

    def parse(self, data: dict):
        data = self._get_parser().parse(data)

        lines = data.get("transportations", [])

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
                Optional("lineListBranchCode"): str,
                Optional("lineListNetBranchCode"): str,
                Optional("lineListSubnetwork"): str,
                Optional("lineListOMC"): str,
                Optional("lineListMixedLines"): Any("0", "1", 0, 1),
                Optional("mergeDir"): Any("0", "1", 0, 1),
                Optional("lineReqType"): Range(
                    min=0, max=sum([x.value for x in LineRequestType])
                ),
            }
        )
