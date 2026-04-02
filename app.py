from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "altiora_nexus_secret_key_2026"

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


@app.route("/")
def auth():
    return render_template("auth.html", mode="register", error=None)


@app.route("/login")
def login_page():
    return render_template("auth.html", mode="login", error=None)


@app.route("/register", methods=["POST"])
def register():
    full_name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not full_name or not email or not password:
        return render_template(
            "auth.html",
            mode="register",
            error="Please fill in all fields."
        )

    users = load_users()

    for user in users:
        if user["email"] == email:
            return render_template(
                "auth.html",
                mode="register",
                error="This email is already registered."
            )

    users.append({
        "name": full_name,
        "email": email,
        "password": password
    })
    save_users(users)

    session["user_name"] = full_name
    session["user_email"] = email

    return redirect(url_for("site_home"))


@app.route("/do-login", methods=["POST"])
def do_login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    users = load_users()

    for user in users:
        if user["email"] == email and user["password"] == password:
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            return redirect(url_for("site_home"))

    return render_template(
        "auth.html",
        mode="login",
        error="Wrong email or password."
    )


def require_login():
    return "user_name" in session


@app.route("/site")
def site_home():
    if not require_login():
        return redirect(url_for("auth"))
    return render_template("index.html", user_name=session.get("user_name"))


@app.route("/about")
def about():
    if not require_login():
        return redirect(url_for("auth"))
    return render_template("about.html", user_name=session.get("user_name"))


@app.route("/info")
def info():
    if not require_login():
        return redirect(url_for("auth"))
    return render_template("info.html", user_name=session.get("user_name"))


@app.route("/contacts")
def contacts():
    if not require_login():
        return redirect(url_for("auth"))
    return render_template("contacts.html", user_name=session.get("user_name"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)