from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

from .models import User, File
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
        remember = request.form.get("remember") == "on"  # ✅ remember me

        user = User.query.filter_by(email=email).first()
        if not user:
            return "Email not registered"

        if not check_password_hash(user.password, password):
            return "Invalid password"

        # ✅ Flask-Login
        login_user(user, remember=remember)

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

            # ✅ TEMP save (no user id yet)
            upload_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename
            )
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
@login_required
def dashboard():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", active="myfiles", user=current_user, files=files)


@main.route("/upload")
@login_required
def upload_page():
    return render_template("dashboard.html", active="upload", user=current_user)


@main.route("/aidetection", methods=["GET", "POST"])
@login_required
def ai_detection_page():
    result = None
    if request.method == "POST":
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            # Process the image
            result = detect_objects(image_file)
    return render_template("dashboard.html", active="aidetection", user=current_user, result=result)


# --------------------------
# FILE UPLOAD ROUTE
# --------------------------
@main.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
    file = request.files.get("file")

    if not file or file.filename == "":
        return "No file selected"

    filename = secure_filename(file.filename)

    # ✅ user folder
    user_folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        str(current_user.id)
    )
    os.makedirs(user_folder, exist_ok=True)

    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    new_file = File(
        filename=filename,
        filepath=filepath,
        user_id=current_user.id
    )

    db.session.add(new_file)
    db.session.commit()

    return {"message": "File uploaded successfully"}, 200

@main.route("/download/<int:file_id>")
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:
        return "Unauthorized"

    return send_file(file.filepath, as_attachment=True)

# --------------------------
# FILE PREVIEW ROUTE
# --------------------------
@main.route("/preview/<int:file_id>")
@login_required
def preview_file(file_id):
    file = File.query.get_or_404(file_id)

    # 🔐 Security check
    if file.user_id != current_user.id:
        return "Unauthorized"

    # ❌ File missing on disk
    if not os.path.exists(file.filepath):
        abort(404)

    # ✅ Get file extension safely
    ext = file.filename.rsplit(".", 1)[-1].lower()

    # 🖼️ Image preview
    if ext in ["png", "jpg", "jpeg", "gif", "webp"]:
        return send_file(file.filepath)

    # 📄 PDF preview
    if ext == "pdf":
        return send_file(file.filepath)

    # 📁 Other files → download
    return send_file(file.filepath, as_attachment=True)
@main.route("/delete/<int:file_id>")
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:
        return "Unauthorized"

    # delete from disk
    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    # delete from DB
    db.session.delete(file)
    db.session.commit()

    return redirect(url_for("main.dashboard"))
    # --------------------------
# RENAME FILE ROUTE
# --------------------------
@main.route("/rename/<int:file_id>", methods=["POST"])
@login_required
def rename_file(file_id):
    file = File.query.get_or_404(file_id)

    # 🔐 Security check
    if file.user_id != current_user.id:
        return "Unauthorized"

    new_name = request.form.get("new_name", "").strip()

    if not new_name:
        return redirect(url_for("main.dashboard"))

    # keep extension
    ext = file.filename.rsplit(".", 1)[-1]
    new_filename = f"{new_name}.{ext}"

    old_path = file.filepath
    new_path = os.path.join(os.path.dirname(old_path), new_filename)

    # rename file on disk
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    # update DB
    file.filename = new_filename
    file.filepath = new_path

    db.session.commit()

    return redirect(url_for("main.dashboard"))


# --------------------------
# PROFILE UPDATE ROUTE
# --------------------------
@main.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    user = current_user

    new_username = request.form.get("username", "").strip()
    new_profile_pic = request.files.get("profile_pic")

    if new_username:
        user.username = new_username

    if new_profile_pic and new_profile_pic.filename != "":
        filename = secure_filename(new_profile_pic.filename)

        user_folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            str(current_user.id)
        )
        os.makedirs(user_folder, exist_ok=True)

        upload_path = os.path.join(user_folder, filename)
        new_profile_pic.save(upload_path)

        user.profile_pic = filename

    db.session.commit()
    return redirect(url_for("main.dashboard"))


# --------------------------
# LOGOUT ROUTE
# --------------------------
@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


# --------------------------  
# AI DETECTION FUNCTION
# --------------------------
def detect_objects(image_file):
    # Read image
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load Haar cascades
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cat_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface.xml')
    
    # Detect faces (humans)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    has_human = len(faces) > 0
    
    # Detect cat faces (animals)
    cats = cat_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    has_animal = len(cats) > 0
    
    if has_human and has_animal:
        return "Image contains both humans and animals (cats)."
    elif has_human:
        return "Image contains humans."
    elif has_animal:
        return "Image contains animals (cats)."
    else:
        return "No humans or cats detected in the image."