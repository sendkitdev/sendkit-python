# SendKit Python SDK

## Project Overview

Python SDK for the SendKit email API. Uses `urllib` (stdlib), zero external dependencies.

## Architecture

```
src/sendkit/
├── __init__.py    # Public exports (SendKit, SendKitError)
├── client.py      # SendKit client: holds API key, _post() method
├── emails.py      # Emails service (send, send_mime)
└── errors.py      # SendKitError exception class
```

- `SendKit` class is the entry point, accepts api_key + optional base_url
- `client.emails` exposes email operations
- Uses keyword-only arguments for send() params
- `from_` parameter (trailing underscore) avoids Python reserved word conflict
- API errors raise `SendKitError` with name, message, status_code
- `POST /v1/emails` for structured emails, `POST /v1/emails/mime` for raw MIME

## Testing

- Tests use `unittest` + `http.server` for mock HTTP servers
- Run tests: `python -m pytest`
- No external test dependencies beyond pytest

## Releasing

- Tags use numeric format: `1.0.0` (no `v` prefix)
- CI runs tests on Python 3.10, 3.11, 3.12, 3.13
- Pushing a tag creates GitHub Release + publishes to PyPI via trusted publishing

## Git

- NEVER add `Co-Authored-By` lines to commit messages
