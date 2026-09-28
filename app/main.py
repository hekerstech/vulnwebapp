"""Acme Internal Portal — routes and access control."""

import functools
import os

from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import COOKIE_NAME, issue_token, verify_token
from app.users import authenticate

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET", "dev-only-insecure-secret")


def current_user():
    return verify_token(request.cookies.get(COOKIE_NAME, ""))


def login_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login"))
        return view(user, *args, **kwargs)

    return wrapper


def admin_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login"))
        if user.get("role") != "admin":
            return render_template("error.html", message="Administrators only."), 403
        return view(user, *args, **kwargs)

    return wrapper


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user = authenticate(username, password)

    if not user:
        return render_template("login.html", error="Invalid username or password."), 401

    response = make_response(redirect(url_for("dashboard")))
    response.set_cookie(
        COOKIE_NAME,
        issue_token(user["username"], user["role"]),
        httponly=True,
        samesite="Lax",
    )
    return response


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie(COOKIE_NAME)
    return response


@app.route("/dashboard")
@login_required
def dashboard(user):
    return render_template("dashboard.html", user=user)


@app.route("/admin")
@admin_required
def admin(user):
    return render_template("admin.html", user=user)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
