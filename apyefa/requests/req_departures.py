import logging

from voluptuous import Any, Date, Datetime, Optional, Required, Schema

from apyefa.data_classes import Departure, Stop, StopType, TransportType
from apyefa.helpers import parse_datetime
from apyefa.requests.req import Request
from apyefa.requests.schemas import SCHEMA_LOCATION, SCHEMA_TRANSPORTATION

_LOGGER = logging.getLogger(__name__)


class DeparturesRequest(Request):
    def __init__(self, stop: str) -> None:
        super().__init__("XML_DM_REQUEST", "dm")

        self.add_param("name_dm", stop)

    def parse(self, data: dict):
        self._validate_response(data)

        stops = data.get("stopEvents", [])

        _LOGGER.debug(f"{len(stops)} departure(s) found")

        departures = []

        for stop in stops:
            planned_time = stop.get("departureTimePlanned", None)
            estimated_time = stop.get("departureTimeEstimated", None)

            if planned_time:
                planned_time = parse_datetime(planned_time)

            if estimated_time:
                estimated_time = parse_datetime(estimated_time)

            infos = stop.get("infos", [])
            transportation = stop.get("transportation", {})

            if transportation:
                line_name = transportation.get("number")
                route = transportation.get("description")

                origin_dict = {
                    "id": transportation.get("origin").get("id"),
                    "name": transportation.get("origin").get("name"),
                    "type": StopType(transportation.get("origin").get("type")),
                }
                destination_dict = {
                    "id": transportation.get("destination").get("id"),
                    "name": transportation.get("destination").get("name"),
                    "type": StopType(transportation.get("destination").get("type")),
                }

                origin = Stop(
                    origin_dict["id"], origin_dict["name"], origin_dict["type"]
                )
                destination = Stop(
                    destination_dict["id"],
                    destination_dict["name"],
                    destination_dict["type"],
                )

                product = TransportType(transportation.get("product").get("class"))

                departures.append(
                    Departure(
                        line_name,
                        route,
                        origin,
                        destination,
                        product,
                        planned_time,
                        estimated_time,
                        infos,
                    )
                )
        return departures

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
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

    def _get_response_schema(self) -> Schema:
        return Schema(
            {
                Required("version"): str,
                Optional("systemMessages"): list,
                Required("locations"): [SCHEMA_LOCATION],
                Required("stopEvents"): [
                    Schema(
                        {
                            Required("location"): SCHEMA_LOCATION,
                            Required("departureTimePlanned"): Datetime(
                                "%Y-%m-%dT%H:%M:%S%z"
                            ),
                            Optional("departureTimeEstimated"): Datetime(
                                "%Y-%m-%dT%H:%M:%S%z"
                            ),
                            Required("transportation"): SCHEMA_TRANSPORTATION,
                        }
                    )
                ],
            }
        )
