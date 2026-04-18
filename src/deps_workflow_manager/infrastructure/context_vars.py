import contextvars
from typing import Any

__all__ = ["user"]

user: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar("user")
