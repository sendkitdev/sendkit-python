from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import SendKit


class Emails:
    """Handles communication with the email related methods of the SendKit API."""

    def __init__(self, client: SendKit) -> None:
        self._client = client

    def send(
        self,
        *,
        from_: str,
        to: str | list[str],
        subject: str,
        html: str | None = None,
        text: str | None = None,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        reply_to: str | None = None,
        headers: dict[str, str] | None = None,
        tags: list[str] | None = None,
        scheduled_at: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> dict[str, str]:
        """Send a structured email.

        Returns a dict with the email ``id``.
        """
        payload: dict[str, Any] = {
            "from": from_,
            "to": to,
            "subject": subject,
        }

        if html is not None:
            payload["html"] = html
        if text is not None:
            payload["text"] = text
        if cc is not None:
            payload["cc"] = cc
        if bcc is not None:
            payload["bcc"] = bcc
        if reply_to is not None:
            payload["reply_to"] = reply_to
        if headers is not None:
            payload["headers"] = headers
        if tags is not None:
            payload["tags"] = tags
        if scheduled_at is not None:
            payload["scheduled_at"] = scheduled_at
        if attachments is not None:
            payload["attachments"] = attachments

        return self._client._post("/v1/emails", payload)

    def send_mime(
        self,
        *,
        envelope_from: str,
        envelope_to: str,
        raw_message: str,
    ) -> dict[str, str]:
        """Send a raw MIME email.

        Returns a dict with the email ``id``.
        """
        return self._client._post("/v1/emails/mime", {
            "envelope_from": envelope_from,
            "envelope_to": envelope_to,
            "raw_message": raw_message,
        })
