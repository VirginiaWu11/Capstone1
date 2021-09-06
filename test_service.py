"""service function tests."""

from models import UserFood, db, BMI, User
from service import UserBMIService, UserFoodService
from sqlalchemy.sql import func
from constants import (
    BMI_LOW_NORMAL,
    BMI_HIGH_NORMAL,
    ACTIVITY_LEVELS,
    PLANS,
    BASE_API_URL,
    BASE_INGREDIENTS_IMG_URL,
)

from secrets import API_SECRET_KEY
import requests
from unittest import TestCase
from models import db, User, BMI, UserFood
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///capstone1test"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class UserServiceTestCase(TestCase):
    """Test service for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        User.query.delete()

        u1 = User.signup(
            username="testuser1",
            password="HASHED_PASSWORD",
            weight=150,
            height=64,
            image_url=None,
            gender="female",
            age=50,
            activity_level="Sedentary (little to no exercise)",
            diet_plan="Lose 1lb per week; 500 calories deficit",
        )

        u2 = User.signup(
            username="testuser2",
            password="HASHED_PASSWORD2",
            weight=200,
            height=65,
            image_url=None,
            gender="female",
            age=40,
            activity_level="Sedentary (little to no exercise)",
            diet_plan="Lose 1lb per week; 500 calories deficit",
        )

        db.session.add_all([u1, u2])
        db.session.commit()
        self.u1 = User.query.get(1)
        self.u2 = User.query.get(2)

        height = BMI.cal_height_inches(self.u2.height)
        weight = self.u2.weight
        bmi = BMI.calculate_BMI(height, weight)
        add_bmi = BMI(bmi=bmi, weight=self.u2.weight, user_id=u2.id)

        user_food1 = UserFood(
            spoon_id=1096010,
            user_id=2,
            date="2021-07-10",
            name="Egg Salad Wrap",
            calories=570,
            img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
        )
        db.session.add_all([add_bmi,user_food1])

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_get_last_seven_user_food_information(self):

        self.assertEqual(UserFoodService.get_last_seven_user_food_information(self.u2.id), [("07/10/2021", 570)])

    def test_get_user_food_dates_and_calories(self):

        self.assertEqual(UserFoodService.get_user_food_dates_and_calories([("07/10/2021", 570)]), {"user_food_dates": ["07/10/2021"], "user_food_calories": [570],})
