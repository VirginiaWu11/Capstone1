"""User View tests."""

from unittest import TestCase

from models import db, User, BMI, UserFood
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

        height = BMI.cal_height_inches(self.u2.height)
        weight = self.u2.weight
        bmi = BMI.calculate_BMI(height, weight)
        add_bmi = BMI(bmi=bmi, weight=self.u2.weight, user_id=u2.id)

        user_food1 = UserFood(
            spoon_id=1096010,
            user_id=2,
            name="Egg Salad Wrap",
            calories=570,
            img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
        )
        db.session.add_all([add_bmi, user_food1])

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_home_view(self):
        """When you’re logged in, can you see the home page showing charts and Username?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser2", str(resp.data))
            self.assertIn("canvas", str(resp.data))
            self.assertIn(self.u2.diet_plan, str(resp.data))

    def test_users_logged_out_food_intake(self):
        """when logged out, /food-intake should show search bar to search recipes"""
        with self.client as c:
            resp = c.get("/food-intake")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search recipes here.", str(resp.data))

    def test_users_logged_out_food_journal(self):
        """when logged out, /food-journal should redirect to logged out home page."""
        with self.client as c:
            resp = c.get("/food-journal")
            self.assertEqual(resp.status_code, 302)

    def test_users_logged_in_food_journal(self):
        """when logged in, /food-journal should show the user their last logged foods"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.get("/food-journal")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Egg Salad Wrap", str(resp.data))
