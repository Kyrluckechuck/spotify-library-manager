from datetime import datetime
from typing import Any

import strawberry


@strawberry.scalar(
    description=(
        "The `DateTime` scalar type represents a date and time following the "
        "ISO 8601 standard."
    )
)
class DateTime:
    @staticmethod
    def serialize(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise ValueError(f"Cannot serialize {value} as DateTime")

    @staticmethod
    def parse_value(value: Any) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        raise ValueError(f"Cannot parse {value} as DateTime")

    @staticmethod
    def parse_literal(ast: Any) -> datetime:
        if hasattr(ast, "value"):
            return DateTime.parse_value(ast.value)
        raise ValueError(f"Cannot parse literal {ast} as DateTime")
