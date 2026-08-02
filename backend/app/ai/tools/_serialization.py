from typing import Any

from fastapi.encoders import jsonable_encoder


def to_jsonable(data: Any) -> Any:
    """Convert service return values into JSON-serializable data.

    Args:
        data: A Pydantic model, SQLAlchemy model, list, or primitive value.

    Returns:
        JSON-serializable data suitable for tool responses.
    """

    return jsonable_encoder(data)
