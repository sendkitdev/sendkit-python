from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
from unittest import TestCase

from sendkit import SendKit, SendKitError


def _make_server(handler_class: type[BaseHTTPRequestHandler]) -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), handler_class)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


class TestNewClient(TestCase):
    def test_with_api_key(self) -> None:
        client = SendKit("sk_test_123")
        self.assertEqual(client.api_key, "sk_test_123")

    def test_missing_api_key(self) -> None:
        os.environ.pop("SENDKIT_API_KEY", None)
        with self.assertRaises(ValueError):
            SendKit()

    def test_from_env_variable(self) -> None:
        os.environ["SENDKIT_API_KEY"] = "sk_from_env"
        try:
            client = SendKit()
            self.assertEqual(client.api_key, "sk_from_env")
        finally:
            del os.environ["SENDKIT_API_KEY"]

    def test_custom_base_url(self) -> None:
        client = SendKit("sk_test_123", base_url="https://custom.api.com")
        self.assertEqual(client.base_url, "https://custom.api.com")


class TestEmailsSend(TestCase):
    def test_send_email(self) -> None:
        captured: dict[str, Any] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                captured["path"] = self.path
                captured["method"] = self.command
                captured["auth"] = self.headers.get("Authorization")
                length = int(self.headers.get("Content-Length", 0))
                captured["body"] = json.loads(self.rfile.read(length))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"id": "email-uuid-123"}).encode())

            def log_message(self, *args: Any) -> None:
                pass

        server, url = _make_server(Handler)
        try:
            client = SendKit("sk_test_123", base_url=url)
            result = client.emails.send(
                from_="sender@example.com",
                to="recipient@example.com",
                subject="Test Email",
                html="<p>Hello</p>",
            )

            self.assertEqual(result["id"], "email-uuid-123")
            self.assertEqual(captured["path"], "/v1/emails")
            self.assertEqual(captured["method"], "POST")
            self.assertEqual(captured["auth"], "Bearer sk_test_123")
            self.assertEqual(captured["body"]["from"], "sender@example.com")
            self.assertEqual(captured["body"]["to"], "recipient@example.com")
            self.assertEqual(captured["body"]["subject"], "Test Email")
        finally:
            server.shutdown()

    def test_send_with_optional_fields(self) -> None:
        captured: dict[str, Any] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", 0))
                captured["body"] = json.loads(self.rfile.read(length))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"id": "email-uuid-456"}).encode())

            def log_message(self, *args: Any) -> None:
                pass

        server, url = _make_server(Handler)
        try:
            client = SendKit("sk_test_123", base_url=url)
            client.emails.send(
                from_="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                html="<p>Hi</p>",
                reply_to="reply@example.com",
                scheduled_at="2026-03-01T10:00:00Z",
            )

            self.assertEqual(captured["body"]["reply_to"], "reply@example.com")
            self.assertEqual(captured["body"]["scheduled_at"], "2026-03-01T10:00:00Z")
        finally:
            server.shutdown()

    def test_send_mime_email(self) -> None:
        captured: dict[str, Any] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                captured["path"] = self.path
                length = int(self.headers.get("Content-Length", 0))
                captured["body"] = json.loads(self.rfile.read(length))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"id": "mime-uuid-789"}).encode())

            def log_message(self, *args: Any) -> None:
                pass

        server, url = _make_server(Handler)
        try:
            client = SendKit("sk_test_123", base_url=url)
            result = client.emails.send_mime(
                envelope_from="sender@example.com",
                envelope_to="recipient@example.com",
                raw_message="From: sender@example.com\r\nTo: recipient@example.com\r\n\r\nHello",
            )

            self.assertEqual(result["id"], "mime-uuid-789")
            self.assertEqual(captured["path"], "/v1/emails/mime")
            self.assertEqual(captured["body"]["envelope_from"], "sender@example.com")
            self.assertEqual(captured["body"]["envelope_to"], "recipient@example.com")
        finally:
            server.shutdown()

    def test_api_error(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                self.send_response(422)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "name": "validation_error",
                    "message": "The to field is required.",
                    "statusCode": 422,
                }).encode())

            def log_message(self, *args: Any) -> None:
                pass

        server, url = _make_server(Handler)
        try:
            client = SendKit("sk_test_123", base_url=url)
            with self.assertRaises(SendKitError) as ctx:
                client.emails.send(
                    from_="sender@example.com",
                    to="",
                    subject="Test",
                    html="<p>Hi</p>",
                )

            err = ctx.exception
            self.assertEqual(err.name, "validation_error")
            self.assertEqual(err.status_code, 422)
            self.assertEqual(err.message, "The to field is required.")
        finally:
            server.shutdown()
