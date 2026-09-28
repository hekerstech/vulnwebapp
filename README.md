# vulnwebapp

Acme Internal Portal — a small Flask demo application with cookie-based
sessions and a role-gated administration area.

It is a demo, not a hardened production service.

## Running it

With Docker Compose:

```bash
cp .env.example .env     # optional; .env is git-ignored
docker compose up --build
```

Or with Docker directly:

```bash
docker build -t vulnwebapp .
docker run --rm -p 5000:5000 -e APP_SECRET=some-random-value vulnwebapp
```

Then open <http://localhost:5000>.

## Routes

| Route        | Access                      |
| ------------ | --------------------------- |
| `/login`     | public                      |
| `/dashboard` | any authenticated user      |
| `/admin`     | users with the `admin` role |
| `/healthz`   | public liveness probe       |

## Demo accounts

| Username | Password         | Role    |
| -------- | ---------------- | ------- |
| `alice`  | `alice-password` | `user`  |
| `admin`  | `admin-password` | `admin` |

The user store is in-memory, so accounts reset when the container restarts.

## Configuration

| Variable     | Default                     | Purpose                                  |
| ------------ | --------------------------- | ---------------------------------------- |
| `APP_SECRET` | `dev-only-insecure-secret`  | Signs session tokens — set a long random value per deployment |
| `PORT`       | `5000`                      | Port gunicorn binds inside the container |

Copy `.env.example` to `.env` for local overrides; `.env` is git-ignored and
must never be committed.

## Layout

```
app/auth.py        session token issuing and verification
app/main.py        routes and access-control decorators
app/users.py       in-memory demo user store
app/templates/     Jinja templates
Dockerfile         container image (gunicorn, unprivileged user, healthcheck)
docker-compose.yml one-command local deployment
```
