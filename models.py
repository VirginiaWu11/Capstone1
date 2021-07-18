from datetime import datetime
from bisect import bisect_right

from sqlalchemy.orm import backref

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
    diet_plan = db.Column(
        db.Text,
        nullable = True
    )

    bmi = db.relationship('BMI', backref='users')
    user_food = db.relationship('UserFood', backref='users')
    
    @classmethod
    def signup(cls, username, password, height, image_url):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            height=height,
            image_url=image_url,
        )

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class UserFood(db.Model):

    __tablename__ = 'user_food'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spoon_id = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow().date(),
    )
    name = db.Column(
        db.Text,
        nullable=False
    )
    calories = db.Column(
        db.Integer,
        nullable=False
    )
    img = db.Column(
        db.Text,
        default="/static/images/w-logo.png"
    )

class UserIngredients(db.Model):

    __tablename__ = 'user_ingredients'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spoon_id = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow().date(),
    )
    name = db.Column(
        db.Text,
        nullable=False
    )
    calories = db.Column(
        db.Integer,
        nullable=False
    )
    img = db.Column(
        db.Text,
        default="/static/images/w-logo.png"
    )

class Food(db.Model):

    __tablename__ = 'food'

    spoon_id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    name = db.Column(
        db.Text,
        nullable=False
    )
    calories = db.Column(
        db.Integer,
        nullable=False
    )
    img = db.Column(
        db.Text,
        default="/static/images/w-logo.png"
    )

class Ingredients(db.Model):

    __tablename__ = 'ingredients'

    spoon_id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False
    )
    calories = db.Column(
        db.Integer,
        nullable=False
    )
    img = db.Column(
        db.Text,
        default="/static/images/w-logo.png"
    )



class BMI(db.Model):
    __tablename__ = 'bmi'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    bmi = db.Column(
        db.Float,
        nullable=False,
    )
    # in pounds
    weight = db.Column(
        db.Integer,
        nullable=False,
    )
    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow().date(),
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"),
        nullable = False
    )

    @classmethod
    def cal_height_inches(cls,height): #height is a string 5'4
        """Convert height from String to Number in Inches"""
        return int(height[0:height.index("'")])*12+int(height[height.index("'")+1])

    @classmethod
    def calculate_BMI(cls, height, weight): #height is in inches now
        """Use BMI formula to calculate BMI"""
        return round(703*weight/((height)**2),2)

    @classmethod
    def BMI_range(cls, bmi): 
        categories = [
            (16,"Severe Thinness"),
            (17,"Moderate Thinness"),
            (18,"Mild Thinness"),
            (25,"Normal"),
            (30,"Overweight"),
            (35,"Obese Class I"),
            (40,"Obese Class II"),
            (100,"Obese Class III"),
        ]
        pos=bisect_right(categories,(bmi,))
        return categories[pos][1]
    @classmethod
    def lbs_away(cls, bmi, height, weight): 
        if(bmi <=18.01):
            goal_weight = int(18.01*((height)**2)/703)
            return goal_weight-weight
        if(bmi > 25):
            goal_weight = int(25*((height)**2)/703)
            return weight-goal_weight