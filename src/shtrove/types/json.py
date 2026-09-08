###
# types for json-serializable stuff

JsonPrimitive = str | int | float | bool | None

type JsonValue = JsonPrimitive | list[JsonValue] | JsonObject

type JsonNonArrayValue = JsonPrimitive | JsonObject

type JsonObject = dict[str, JsonValue]
