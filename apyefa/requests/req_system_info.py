import logging

from voluptuous import Any, Date, Required, Schema

from apyefa.data_classes import SystemInfo
from apyefa.helpers import parse_date
from apyefa.requests.req import Request

_LOGGER = logging.getLogger(__name__)


class SystemInfoRequest(Request):
    def __init__(self) -> None:
        super().__init__("XML_SYSTEMINFO_REQUEST", "system")

    def parse(self, data: dict) -> SystemInfo:
        _LOGGER.info("Parsing system info response")

        self._validate_response(data)

        version = data.get("version", None)
        data_format = data.get("ptKernel").get("dataFormat")
        valid_from = data.get("validity").get("from")
        valid_to = data.get("validity").get("to")

        valid_from = parse_date(valid_from)
        valid_to = parse_date(valid_to)

        return SystemInfo(version, data_format, valid_from, valid_to)

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
            }
        )

    def _get_response_schema(self) -> Schema:
        return Schema(
            {
                Required("version"): str,
                Required("ptKernel"): Schema(
                    {
                        Required("appVersion"): str,
                        Required("dataFormat"): str,
                        Required("dataBuild"): str,
                    }
                ),
                Required("validity"): Schema(
                    {
                        Required("from"): Date("%Y-%m-%d"),
                        Required("to"): Date("%Y-%m-%d"),
                    }
                ),
            }
        )
