from voluptuous import (
    ALLOW_EXTRA,
    Boolean,
    In,
    Optional,
    Range,
    Required,
    Schema,
)

from apyefa.data_classes import StopType


def IsStopType(type: str):
    if type not in [x.value for x in StopType]:
        raise ValueError


SCHEMA_PROPERTIES = Schema(
    {
        Required("stopId"): str,
        Optional("downloads"): list,
        Optional("area"): str,
        Optional("platform"): str,
        Optional("platformName"): str,
    }
)

SCHEMA_PARENT = Schema(
    {
        Required("id"): str,
        Required("name"): str,
        Required("type"): str,
        Optional("isGlobalId"): Boolean,
        Optional("disassembledName"): str,
        Optional("parent"): Schema(
            {
                Required("name"): str,
                Required("type"): IsStopType,
            }
        ),
        Optional("properties"): SCHEMA_PROPERTIES,
    }
)
SCHEMA_PRODUCT = Schema(
    {
        Required("id"): int,
        Required("class"): int,
        Required("name"): str,
        Optional("iconId"): int,
    }
)

SCHEMA_SRC_DEST = Schema(
    {
        Required("id"): str,
        Required("name"): str,
        Required("type"): IsStopType,
    }
)

SCHEMA_TRANSPORTATION = Schema(
    {
        Required("id"): str,
        Required("name"): str,
        Required("disassembledName"): str,
        Required("number"): str,
        Required("description"): str,
        Required("product"): SCHEMA_PRODUCT,
        Optional("operator"): dict,
        Optional("destination"): SCHEMA_SRC_DEST,
        Optional("origin"): SCHEMA_SRC_DEST,
        Optional("properties"): dict,
    }
)

SCHEMA_LOCATION = Schema(
    {
        Required("id"): str,
        Optional("isGlobalId"): Boolean,
        Required("name"): str,
        Optional("disassembledName"): str,
        Optional("coord"): list,
        Required("type"): In([x.value for x in StopType]),
        Optional("isBest"): Boolean,
        Optional("productClasses"): list[Range(min=0, max=10)],
        Optional("parent"): SCHEMA_PARENT,
        Optional("assignedStops"): list,
        Optional("properties"): SCHEMA_PROPERTIES,
        Optional("matchQuality"): int,
    },
    extra=ALLOW_EXTRA,
)
