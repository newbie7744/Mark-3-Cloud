from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from .models import User
from . import db

main = Blueprint("main", __name__)


# --------------------------
# LOGIN ROUTE
# --------------------------
@main.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()
        if not user:
            return "Email not registered"

        if not check_password_hash(user.password, password):
            return "Invalid password"

        # Successful login
        session["user_id"] = user.id
        session["username"] = user.username
        session["profile_pic"] = user.profile_pic or "profile.png"

        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


# --------------------------
# SIGNUP ROUTE
# --------------------------
@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        retyped = request.form.get("retype-password", "").strip()
        profile_pic = request.files.get("profile_pic")

        if password != retyped:
            return "Passwords do not match"

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        hashed_password = generate_password_hash(password)

        filename = None
        if profile_pic and profile_pic.filename != "":
            filename = secure_filename(profile_pic.filename)
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            profile_pic.save(upload_path)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            profile_pic=filename
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("main.login"))

    return render_template("signup.html")


# --------------------------
# DASHBOARD ROUTES
# --------------------------
@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html", active="myfiles")


@main.route("/upload")
def upload_page():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html", active="upload")


@main.route("/aidetection")
def ai_detection_page():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html", active="aidetection")


# --------------------------
# PROFILE UPDATE ROUTE
# --------------------------
@main.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("main.login"))

    new_username = request.form.get("username", "").strip()
    new_profile_pic = request.files.get("profile_pic")

    if new_username:
        user.username = new_username
        session["username"] = new_username

    if new_profile_pic and new_profile_pic.filename != "":
        filename = secure_filename(new_profile_pic.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        new_profile_pic.save(upload_path)
        user.profile_pic = filename
        session["profile_pic"] = filename

    db.session.commit()
    return redirect(url_for("main.dashboard"))


# --------------------------
# LOGOUT ROUTE
# --------------------------
@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))