import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # ✅ Use environment variables
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_fallback_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    # ✅ Upload folder
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # ✅ Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please login first"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes import main
    app.register_blueprint(main)

    # ✅ Wait for PostgreSQL (important for Docker)
    with app.app_context():
        time.sleep(3)
        db.create_all()

    return app