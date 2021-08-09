from datetime import datetime
from bisect import bisect_right
from requests.sessions import default_headers

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
    weight = db.Column(
        db.Integer,
        nullable=False
    )
    height=db.Column(
        db.Text,
        nullable = True
    )
    diet_plan = db.Column(
        db.Text,
        nullable = False,
        default="Maintain current weight; 0 calories deficit"
    )
    gender = db.Column(
        db.Text,
        nullable = False
    )
    age = db.Column(
        db.Integer,
        nullable = False
    )
    activity_level = db.Column(
        db.Text,
        nullable = False
    )
# https://www.healthline.com/health/fitness-exercise/how-many-calories-do-i-burn-a-day#calories-burned
    # 1.2, or sedentary (little to no exercise)
    # 1.375, or lightly active (light exercise 1–3 days per week)
    # 1.55, or moderately active (moderate exercise 3–5 days per week)
    # 1.725, or very active (hard exercise 6–7 days per week)
    # 1.9, or extra active (very hard exercise, training, or a physical job)

    bmi = db.relationship('BMI', backref='users')
    user_food = db.relationship('UserFood', backref='users')
    
    @classmethod
    def signup(cls, username, password, weight, height, image_url, gender, age, activity_level, diet_plan):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            weight=weight,
            height=height,
            image_url=image_url,
            gender=gender,
            age=age,
            activity_level=activity_level,
            diet_plan=diet_plan
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

    @classmethod
    def basal_metabolic_rate(cls,weight, height, age, gender):
        if gender=="female":
            return 655.1 + (4.35 * weight) + (4.7 * height) - (4.7 * age)
        return 66 + (6.2 * weight) + (12.7 * height) - (6.76 * age)

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
        if "'" not in height:
            return int(height)
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