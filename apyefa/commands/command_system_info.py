import logging

from voluptuous import Any, Optional, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import CoordFormat, SystemInfo

_LOGGER = logging.getLogger(__name__)


class CommandSystemInfo(Command):
    def __init__(self, format: str) -> None:
        super().__init__("XML_SYSTEMINFO_REQUEST", format)

    def parse(self, data: dict) -> SystemInfo:
        _LOGGER.info("Parsing system info response")

        data = self._get_parser().parse(data)

        return SystemInfo.from_dict(data)

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Optional("coordOutputFormat", default=CoordFormat.WGS84.value): Any(
                    *[x.value for x in CoordFormat]
                ),
            }
        )
