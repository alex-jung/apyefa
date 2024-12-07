import logging

from voluptuous import Any, Optional, Range, Required, Schema

from apyefa.commands.command import Command
from apyefa.data_classes import Location, LocationFilter

_LOGGER = logging.getLogger(__name__)


class CommandStopFinder(Command):
    def __init__(self, req_type: str, name: str) -> None:
        super().__init__("XML_STOPFINDER_REQUEST", "stopfinder")

        self.add_param("type_sf", req_type)
        self.add_param("name_sf", name)

    def parse(self, data: dict) -> list[Location]:
        data = self._get_parser().parse(data)

        locations = data.get("locations", [])

        _LOGGER.info(f"{len(locations)} location(s) found")

        result = []

        for location in locations:
            result.append(Location.from_dict(location))

        return sorted(result, key=lambda x: x.match_quality, reverse=True)

    def _get_params_schema(self) -> Schema:
        return Schema(
            {
                Required("outputFormat", default="rapidJSON"): Any("rapidJSON"),
                Required("coordOutputFormat", default="WGS84"): Any("WGS84"),
                Required("type_sf", default="any"): Any("any", "coord"),
                Required("name_sf"): str,
                Optional("anyMaxSizeHitList"): int,
                Optional("anySigWhenPerfectNoOtherMatches"): Any("0", "1", 0, 1),
                Optional("anyResSort_sf"): str,
                Optional("anyObjFilter_sf"): int,
                Optional("doNotSearchForStops_sf"): Any("0", "1", 0, 1),
                Optional("anyObjFilter_origin"): Range(
                    min=0, max=sum([x.value for x in LocationFilter])
                ),
            }
        )
