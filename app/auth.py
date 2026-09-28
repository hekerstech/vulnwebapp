"""Session token issuing and verification.

Tokens are carried in a cookie and shaped as:

    base64url(json_payload) "." base64url(hmac_sha256(payload))
"""

import base64
import hashlib
import hmac
import json
import os
import time

SECRET = os.environ.get("APP_SECRET", "dev-only-insecure-secret").encode()
TOKEN_TTL_SECONDS = 3600
COOKIE_NAME = "session_token"


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64url_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _sign(body: str) -> str:
    digest = hmac.new(SECRET, body.encode(), hashlib.sha256).digest()
    return _b64url_encode(digest)


def issue_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    body = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    return f"{body}.{_sign(body)}"


def verify_token(token: str):
    """Return the payload carried by a session token, or None if unusable.

    The signature is recomputed over the payload and compared in constant time
    before any field is read, and expired tokens are refused.
    """
    if not token:
        return None

    body, separator, signature = token.partition(".")
    if not separator or not signature:
        return None

    if not hmac.compare_digest(signature, _sign(body)):
        return None

    try:
        payload = json.loads(_b64url_decode(body))
    except (ValueError, TypeError):
        return None

    if not isinstance(payload, dict) or "sub" not in payload:
        return None

    expires_at = payload.get("exp")
    if not isinstance(expires_at, (int, float)) or time.time() >= expires_at:
        return None

    return payload
