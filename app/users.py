"""In-memory user store. A real application would use a database."""

import hashlib

# Demo credentials. Passwords are stored as SHA-256 digests purely so the
# plaintext is not sitting in the source; this is NOT how you store passwords
# in a real application (use bcrypt/argon2 with a per-user salt).
USERS = {
    "alice": {
        "password_sha256": hashlib.sha256(b"alice-password").hexdigest(),
        "role": "user",
        "full_name": "Alice Jones",
    },
    "admin": {
        "password_sha256": hashlib.sha256(b"admin-password").hexdigest(),
        "role": "admin",
        "full_name": "Site Administrator",
    },
}


def authenticate(username: str, password: str):
    user = USERS.get(username)
    if not user:
        return None
    if hashlib.sha256(password.encode()).hexdigest() != user["password_sha256"]:
        return None
    return {"username": username, "role": user["role"], "full_name": user["full_name"]}
