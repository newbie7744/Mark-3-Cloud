from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "secretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cloud.db"
    app.config["UPLOAD_FOLDER"] = "app/static/uploads"

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app