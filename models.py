from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    password = db.Column(
        db.Text,
        nullable=False,
    )
    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )
    height=db.Column(
        db.Text,
        nullable = True
    )

class Food(db.Model):

    __tablename__ = 'food'

    spoon_id = db.Column(
        db.Integer,
        primary_key=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow().date(),
    )
    calories = db.Column(
        db.Integer,
        nullable=False
    )

class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    difficulty = db.Column(db.Text,nullable=False,
    )


class BMI(db.Model):
    __tablename__ = 'bmi'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    bmi = db.Column(
        db.Integer,
        nullable=False,
    )
    # in pounds
    weight = db.Column(
        db.Integer,
        nullable=False,
    )
    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow().date(),
    )

