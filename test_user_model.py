"""User model tests."""

# run these tests like:
#
#   FLASK_ENV=production python -m unittest test_user_model.py
# (we set FLASK_ENV for this command, so it doesn’t use debug mode, and therefore won’t use the Debug Toolbar during our tests).

import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"

from app import app

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
      
        u1 = User(
            
            username="testuser1",
            password="HASHED_PASSWORD",
            weight=150,
            height=60,
            diet_plan="Maintain current weight; 0 calories deficit",
            gender = "female",
            age = 50,
            activity_level="Sedentary (little to no exercise)"
        )
        
        db.session.add(u1)
        db.session.commit()

        
        self.u1 = User.query.get(1)
        self.u1_id=self.u1.id

        self.client = app.test_client()

        u3= User.signup(
            username="testuser3",
            password="HASHED_PASSWORD3",
            weight=200,
            height=70,
            diet_plan="Maintain current weight; 0 calories deficit",
            gender = "male",
            age = 60,
            image_url="",
            activity_level="Sedentary (little to no exercise)")

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        
        u2 = User(
            username="testuser2",
            password="HASHED_PASSWORD2",
            weight=200,
            height=70,
            diet_plan="Maintain current weight; 0 calories deficit",
            gender = "male",
            age = 60,
            activity_level="Sedentary (little to no exercise)"
        )

        db.session.add(u2)
        db.session.commit()

        # User should have no BMI record & no meals
        self.assertEqual(len(u2.bmi), 0)
        self.assertEqual(len(u2.user_food), 0)


# SignUp Tests
    def test_valid_user_signup(self):
        """Test user method signup"""

        u2= User.signup(
            username="testuser2",
            password="HASHED_PASSWORD2",
            weight=200,
            height=70,
            diet_plan="Maintain current weight; 0 calories deficit",
            gender = "male",
            age = 60,
            image_url="",
            activity_level="Sedentary (little to no exercise)")

        self.assertNotEqual(u2.password, "HASHED_PASSWORD2")
        self.assertEqual(len(User.query.all()),3)


    def test_invalid_username_signup(self):
        
        with self.assertRaises(exc.IntegrityError) as context:
            invalid_user=User.signup(
            username="testuser1",
            password="HASHED_PASSWORD2",
            weight=200,
            height=70,
            diet_plan="Maintain current weight; 0 calories deficit",
            gender = "male",
            age = 60,
            image_url="",
            activity_level="Sedentary (little to no exercise)")

# Authentication tests

    def test_valid_authentication(self):
        u = User.authenticate('testuser3', "HASHED_PASSWORD3")
        self.assertIsNotNone(u) 

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("testuser2", "HASHED_PASSWORD"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("testuser3", "incorrect"))
