import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "secretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cloud.db"

    # ✅ Upload folder (absolute path)
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
        return db.session.get(User, int(user_id))  # ✅ modern way

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app