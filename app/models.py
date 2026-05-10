from . import db
from flask_login import UserMixin


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    profile_pic = db.Column(db.String(200))

    # ✅ relationship to files
    files = db.relationship("File", backref="user", lazy=True)


class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(200), nullable=False)

    filepath = db.Column(db.String(300), nullable=False)

    classification = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)