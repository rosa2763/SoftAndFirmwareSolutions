from flask import Blueprint, redirect, render_template, request, session, url_for

from . import db
from .models import User

main = Blueprint("main", __name__)

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["username"] = username
        return redirect(url_for("main.dashboard"))
    return render_template("index.html", error="Invalid username or password")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("index.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        return render_template("index.html", error="Username and password are required")

    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="User already registered")

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    session["username"] = username
    return redirect(url_for("main.dashboard"))


@main.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect(url_for("main.home"))


@main.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("main.home"))


@main.route("/")
def home():
    if "username" in session:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")
