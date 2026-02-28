from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .emails import Emails
from .errors import SendKitError

_DEFAULT_BASE_URL = "https://api.sendkit.dev"


class SendKit:
    """SendKit API client.

    Args:
        api_key: Your SendKit API key. If not provided, reads from
            the ``SENDKIT_API_KEY`` environment variable.
        base_url: Override the API base URL.
    """

    def __init__(self, api_key: str | None = None, *, base_url: str = _DEFAULT_BASE_URL) -> None:
        self.api_key = api_key or os.environ.get("SENDKIT_API_KEY", "")

        if not self.api_key:
            raise ValueError(
                'Missing API key. Pass it to the constructor `SendKit("sk_...")` '
                "or set the SENDKIT_API_KEY environment variable."
            )

        self.base_url = base_url
        self.emails = Emails(self)

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        data = json.dumps(body).encode()
        req = Request(
            f"{self.base_url}{path}",
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(req) as resp:
                return json.loads(resp.read())
        except HTTPError as exc:
            try:
                error_body = json.loads(exc.read())
                raise SendKitError(
                    message=error_body.get("message", exc.reason),
                    status_code=exc.code,
                    name=error_body.get("name", "application_error"),
                ) from None
            except (json.JSONDecodeError, AttributeError):
                raise SendKitError(
                    message=str(exc.reason),
                    status_code=exc.code,
                ) from None
