import logging

from voluptuous import Any, Required, Schema

from apyefa.data_classes import SystemInfo
from apyefa.requests.req import Request

_LOGGER = logging.getLogger(__name__)


class SystemInfoRequest(Request):
    def __init__(self) -> None:
        super().__init__("XML_SYSTEMINFO_REQUEST", "system")

    def parse(self, data: dict) -> SystemInfo:
        _LOGGER.info("Parsing system info response")

        data = self._get_parser().parse(data)

        return SystemInfo.from_dict(data)

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
            }
        )
