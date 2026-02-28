from __future__ import annotations


class SendKitError(Exception):
    """Represents an error response from the SendKit API."""

    def __init__(self, message: str, status_code: int | None = None, name: str = "application_error") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.name = name

    def __repr__(self) -> str:
        return f"SendKitError(name={self.name!r}, status_code={self.status_code}, message={self.message!r})"
