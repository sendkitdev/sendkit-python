# SendKit Python SDK

Official Python SDK for the [SendKit](https://sendkit.com) email API.

## Installation

```bash
pip install sendkit
```

## Usage

### Create a Client

```python
from sendkit import SendKit

client = SendKit("sk_your_api_key")
```

### Send an Email

```python
result = client.emails.send(
    from_="you@example.com",
    to="recipient@example.com",
    subject="Hello from SendKit",
    html="<h1>Welcome!</h1>",
)

print(result["id"])
```

### Send a MIME Email

```python
result = client.emails.send_mime(
    envelope_from="you@example.com",
    envelope_to="recipient@example.com",
    raw_message=mime_string,
)
```

### Error Handling

API errors raise `SendKitError`:

```python
from sendkit import SendKit, SendKitError

client = SendKit("sk_your_api_key")

try:
    client.emails.send(...)
except SendKitError as e:
    print(e.name)        # e.g. "validation_error"
    print(e.message)     # e.g. "The to field is required."
    print(e.status_code) # e.g. 422
```

### Configuration

```python
# Read API key from SENDKIT_API_KEY environment variable
client = SendKit()

# Custom base URL
client = SendKit("sk_...", base_url="https://custom.api.com")
```
