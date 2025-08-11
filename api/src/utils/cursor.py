from __future__ import annotations

import base64
from typing import Union


def encode_cursor(value: Union[int, str]) -> str:
    """Return a URL-safe base64 encoded cursor from an int or string value."""
    raw = str(value).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor: str) -> Union[int, str]:
    """Decode a cursor previously produced by encode_cursor.

    Returns an int when the decoded content is purely numeric, otherwise the raw string.
    """
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
    except Exception:
        # Fallback to legacy/plain cursor styles
        raw = cursor
    return int(raw) if raw.isdigit() else raw
