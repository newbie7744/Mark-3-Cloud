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

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "tif", "tiff"}
PASSWORD_POLICY_MESSAGE = "Password must be at least 9 characters and include lowercase, uppercase, a number, and a symbol."


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

        password_error = validate_password_policy(password)
        if password_error:
            return password_error

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
    updated = False
    for file in files:
        if not file.classification and os.path.exists(file.filepath) and is_image_file(file.filename):
            file.classification = classify_image_file(file.filepath)
            updated = True

    if updated:
        db.session.commit()

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
    return render_template("dashboard.html", active="myfiles", user=current_user, result=result)


# --------------------------
# FILE UPLOAD ROUTE
# --------------------------
@main.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
    files = request.files.getlist("files")
    if not files:
        single_file = request.files.get("file")
        if single_file:
            files = [single_file]

    files = [uploaded_file for uploaded_file in files if uploaded_file and uploaded_file.filename != ""]
    if not files:
        return "No file selected"

    # ✅ user folder
    user_folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        str(current_user.id)
    )
    os.makedirs(user_folder, exist_ok=True)

    uploaded_records = []

    for uploaded_file in files:
        original_name = uploaded_file.filename.replace("\\", "/")
        safe_parts = []
        for part in original_name.split("/"):
            safe_part = secure_filename(part)
            if safe_part:
                safe_parts.append(safe_part)

        if not safe_parts:
            continue

        stored_relative_path = os.path.join(*safe_parts)
        file_directory = os.path.join(user_folder, *safe_parts[:-1]) if len(safe_parts) > 1 else user_folder
        os.makedirs(file_directory, exist_ok=True)

        filepath = os.path.join(user_folder, stored_relative_path)
        uploaded_file.save(filepath)

        classification = None
        if is_image_file(safe_parts[-1]):
            classification = classify_image_file(filepath)

        new_file = File(
            filename=stored_relative_path,
            filepath=filepath,
            classification=classification,
            user_id=current_user.id
        )

        db.session.add(new_file)
        uploaded_records.append({
            "filename": stored_relative_path,
            "classification": classification
        })

    db.session.commit()

    return {
        "message": f"{len(uploaded_records)} file(s) uploaded successfully",
        "uploaded": uploaded_records,
    }, 200

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


def validate_password_policy(password):
    if len(password) < 9:
        return PASSWORD_POLICY_MESSAGE

    has_lowercase = any(character.islower() for character in password)
    has_uppercase = any(character.isupper() for character in password)
    has_number = any(character.isdigit() for character in password)
    has_symbol = any(not character.isalnum() for character in password)

    if not (has_lowercase and has_uppercase and has_number and has_symbol):
        return PASSWORD_POLICY_MESSAGE

    return None


# --------------------------
# IMAGE CLASSIFICATION HELPERS
# --------------------------
def is_image_file(filename):
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[-1].lower()
    return extension in IMAGE_EXTENSIONS


def classify_image_file(image_path):
    with open(image_path, "rb") as image_handle:
        image_bytes = image_handle.read()

    return classify_image_bytes(image_bytes)


def classify_image_bytes(image_bytes):
    return classify_with_cascades(image_bytes)


def classify_with_cascades(image_bytes):
    try:
        import cv2
    except Exception:
        return "Unknown"

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return "Unknown"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(40, 40),
    )

    if len(faces) > 0:
        return "Human"

    upper_body_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_upperbody.xml"
    )
    bodies = upper_body_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=7,
        minSize=(60, 60),
    )

    if len(bodies) > 0:
        return "Human"

    return "Non-human"


# --------------------------  
# AI DETECTION FUNCTION
# --------------------------
def detect_objects(image_file):
    return classify_image_bytes(image_file.read())