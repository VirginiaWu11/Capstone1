"""User View tests."""

import os
from unittest import TestCase

from models import db, User
from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///capstone1test"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False



db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

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

        print(self.u2.username, "********************************")
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
            
    def test_users_logged_out_food_intake(self):
        """when logged out, /food-intake should show search bar to search recipes"""
        with self.client as c:
            resp = c.get("/food-intake")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search recipes here.",str(resp.data))

    def test_users_logged_out_food_journal(self):
        """when logged out, /food-journal should redirect to logged out home page with flash showing Access unauthorized."""
        with self.client as c:
            resp = c.get("/food-journal")
            self.assertEqual(resp.status_code, 302)


