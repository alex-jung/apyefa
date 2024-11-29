import logging

from voluptuous import Any, Exclusive, Optional, Range, Required, Schema

from apyefa.data_classes import Stop, StopFilter, StopType, TransportType
from apyefa.requests.req import Request
from apyefa.requests.schemas import SCHEMA_LOCATION

_LOGGER = logging.getLogger(__name__)


class ServingLinesRequest(Request):
    def __init__(self, mode: str) -> None:
        super().__init__("XML_SERVINGLINES_REQUEST", "servingLines")

        self.add_param("mode", mode)

    def parse(self, data: dict) -> list[Stop]:
        self._validate_response(data)

        locations = data.get("locations", [])

        _LOGGER.info(f"{len(locations)} stop(s) found")

        stops = []

        for location in locations:
            id = location.get("id", "")

            if not location.get("isGlobalId", False):
                if location.get("properties"):
                    id = location.get("properties").get("stopId")

            stop = {
                "id": id,
                "name": location.get("name", ""),
                "disassembled_name": location.get("disassembledName", ""),
                "coord": location.get("coord", []),
                "stop_type": StopType(location.get("type", "")),
                "transports": [
                    TransportType(x) for x in location.get("productClasses", [])
                ],
                "match_quality": location.get("matchQuality", 0),
            }

            stops.append(stop)

        stops = sorted(stops, key=lambda x: x["match_quality"], reverse=True)

        return [
            Stop(
                x["id"],
                x["name"],
                x["disassembled_name"],
                x["coord"],
                x["stop_type"],
                x["transports"],
            )
            for x in stops
        ]

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
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

    def _get_response_schema(self) -> Schema:
        return Schema(
            {
                Required("version"): str,
                Optional("systemMessages"): list,
                Required("locations"): [SCHEMA_LOCATION],
            }
        )
