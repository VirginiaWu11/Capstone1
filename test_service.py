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
from datetime import datetime
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
        db.session.add_all([add_bmi, user_food1])

        db.session.commit()

        self.client = app.test_client()
        # import pdb;pdb.set_trace()

    def tearDown(self):
        db.session.rollback()

    # test UserBMIService
    def test_query_user_bmi_information_and_get_bmi_information(self):
        self.assertEqual(
            UserBMIService.get_bmi_information(
                UserBMIService.query_user_bmi_information(self.u2), self.u2
            ),
            {
                "user_bmi_dates": ["09/06/2021"],
                "bmis": [33.28],
                "weights": [200],
                "bmi_lows_normal": [18.5],
                "bmi_highs_normal": [24.9],
                "weight_lows_normal": [111],
                "weight_highs_normal": [149],
            },
        )

    # test UserFoodService
    def test_get_last_seven_user_food_information(self):

        self.assertEqual(
            UserFoodService.get_last_seven_user_food_information(self.u2.id),
            [("07/10/2021", 570)],
        )

    def test_get_user_food_dates_and_calories(self):

        self.assertEqual(
            UserFoodService.get_user_food_dates_and_calories([("07/10/2021", 570)]),
            {
                "user_food_dates": ["07/10/2021"],
                "user_food_calories": [570],
            },
        )

    def test_get_user_calories_out(self):
        self.assertEqual(
            UserFoodService.get_user_calories_out([("07/10/2021", 570)], self.u2),
            [1971],
        )

    def test_get_user_goal_calories_in(self):
        self.assertEqual(
            UserFoodService.get_user_goal_calories_in([1971], self.u2), [1471]
        )

    def test_query_ingredients_resp(self):
        self.assertEqual(
            UserFoodService.query_ingredients_resp("banana"),
            {
                "results": [{"id": 9040, "name": "banana", "image": "bananas.jpg"}],
                "offset": 0,
                "number": 1,
                "totalResults": 14,
            },
        )

    def test_format_ingredients_data(self):
        self.assertEqual(
            UserFoodService.format_ingredients_data(
                9040,
                {
                    "results": [{"id": 9040, "name": "banana", "image": "bananas.jpg"}],
                    "offset": 0,
                    "number": 1,
                    "totalResults": 14,
                },
            ),
            {
                "results": [
                    {
                        "id": 9040,
                        "name": "banana",
                        "image": "https://spoonacular.com/cdn/ingredients_100x100/bananas.jpg",
                        "title": "banana",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 105.02,
                                    "unit": "kcal",
                                },
                                {
                                    "title": "Copper",
                                    "name": "Copper",
                                    "amount": 0.09,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Folate",
                                    "name": "Folate",
                                    "amount": 23.6,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Cholesterol",
                                    "name": "Cholesterol",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin E",
                                    "name": "Vitamin E",
                                    "amount": 0.12,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Fluoride",
                                    "name": "Fluoride",
                                    "amount": 2.6,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 105.02,
                                    "unit": "kcal",
                                },
                                {
                                    "title": "Vitamin B5",
                                    "name": "Vitamin B5",
                                    "amount": 0.39,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Iron",
                                    "name": "Iron",
                                    "amount": 0.31,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Zinc",
                                    "name": "Zinc",
                                    "amount": 0.18,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin B3",
                                    "name": "Vitamin B3",
                                    "amount": 0.78,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Potassium",
                                    "name": "Potassium",
                                    "amount": 422.44,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin B6",
                                    "name": "Vitamin B6",
                                    "amount": 0.43,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Fiber",
                                    "name": "Fiber",
                                    "amount": 3.07,
                                    "unit": "g",
                                },
                                {
                                    "title": "Sugar",
                                    "name": "Sugar",
                                    "amount": 14.43,
                                    "unit": "g",
                                },
                                {
                                    "title": "Vitamin B2",
                                    "name": "Vitamin B2",
                                    "amount": 0.09,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin B12",
                                    "name": "Vitamin B12",
                                    "amount": 0.0,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Sodium",
                                    "name": "Sodium",
                                    "amount": 1.18,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Carbohydrates",
                                    "name": "Carbohydrates",
                                    "amount": 26.95,
                                    "unit": "g",
                                },
                                {
                                    "title": "Manganese",
                                    "name": "Manganese",
                                    "amount": 0.32,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Mono Unsaturated Fat",
                                    "name": "Mono Unsaturated Fat",
                                    "amount": 0.04,
                                    "unit": "g",
                                },
                                {
                                    "title": "Fat",
                                    "name": "Fat",
                                    "amount": 0.39,
                                    "unit": "g",
                                },
                                {
                                    "title": "Phosphorus",
                                    "name": "Phosphorus",
                                    "amount": 25.96,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Alcohol",
                                    "name": "Alcohol",
                                    "amount": 0.0,
                                    "unit": "g",
                                },
                                {
                                    "title": "Vitamin C",
                                    "name": "Vitamin C",
                                    "amount": 10.27,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Folic Acid",
                                    "name": "Folic Acid",
                                    "amount": 0.0,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Protein",
                                    "name": "Protein",
                                    "amount": 1.29,
                                    "unit": "g",
                                },
                                {
                                    "title": "Vitamin D",
                                    "name": "Vitamin D",
                                    "amount": 0.0,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Magnesium",
                                    "name": "Magnesium",
                                    "amount": 31.86,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin A",
                                    "name": "Vitamin A",
                                    "amount": 75.52,
                                    "unit": "IU",
                                },
                                {
                                    "title": "Choline",
                                    "name": "Choline",
                                    "amount": 11.56,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Caffeine",
                                    "name": "Caffeine",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin K",
                                    "name": "Vitamin K",
                                    "amount": 0.59,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Selenium",
                                    "name": "Selenium",
                                    "amount": 1.18,
                                    "unit": "µg",
                                },
                                {
                                    "title": "Net Carbohydrates",
                                    "name": "Net Carbohydrates",
                                    "amount": 23.88,
                                    "unit": "g",
                                },
                                {
                                    "title": "Calcium",
                                    "name": "Calcium",
                                    "amount": 5.9,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Vitamin B1",
                                    "name": "Vitamin B1",
                                    "amount": 0.04,
                                    "unit": "mg",
                                },
                                {
                                    "title": "Saturated Fat",
                                    "name": "Saturated Fat",
                                    "amount": 0.13,
                                    "unit": "g",
                                },
                            ],
                            "properties": [
                                {
                                    "name": "Glycemic Index",
                                    "title": "Glycemic Index",
                                    "amount": 54.78,
                                    "unit": "",
                                },
                                {
                                    "name": "Glycemic Load",
                                    "title": "Glycemic Load",
                                    "amount": 13.08,
                                    "unit": "",
                                },
                            ],
                            "flavonoids": [
                                {
                                    "name": "Cyanidin",
                                    "title": "Cyanidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Petunidin",
                                    "title": "Petunidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Delphinidin",
                                    "title": "Delphinidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Malvidin",
                                    "title": "Malvidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Pelargonidin",
                                    "title": "Pelargonidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Peonidin",
                                    "title": "Peonidin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Catechin",
                                    "title": "Catechin",
                                    "amount": 7.2,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Epigallocatechin",
                                    "title": "Epigallocatechin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Epicatechin",
                                    "title": "Epicatechin",
                                    "amount": 0.02,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Epicatechin 3-gallate",
                                    "title": "Epicatechin 3-gallate",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Epigallocatechin 3-gallate",
                                    "title": "Epigallocatechin 3-gallate",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Theaflavin",
                                    "title": "Theaflavin",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Thearubigins",
                                    "title": "Thearubigins",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Eriodictyol",
                                    "title": "Eriodictyol",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Hesperetin",
                                    "title": "Hesperetin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Naringenin",
                                    "title": "Naringenin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Apigenin",
                                    "title": "Apigenin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Luteolin",
                                    "title": "Luteolin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Isorhamnetin",
                                    "title": "Isorhamnetin",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Kaempferol",
                                    "title": "Kaempferol",
                                    "amount": 0.13,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Myricetin",
                                    "title": "Myricetin",
                                    "amount": 0.01,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Quercetin",
                                    "title": "Quercetin",
                                    "amount": 0.07,
                                    "unit": "mg",
                                },
                                {
                                    "name": "Theaflavin-3,3'-digallate",
                                    "title": "Theaflavin-3,3'-digallate",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Theaflavin-3'-gallate",
                                    "title": "Theaflavin-3'-gallate",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Theaflavin-3-gallate",
                                    "title": "Theaflavin-3-gallate",
                                    "amount": 0.0,
                                    "unit": "",
                                },
                                {
                                    "name": "Gallocatechin",
                                    "title": "Gallocatechin",
                                    "amount": 0.0,
                                    "unit": "mg",
                                },
                            ],
                            "caloricBreakdown": {
                                "percentProtein": 4.42,
                                "percentFat": 3.01,
                                "percentCarbs": 92.57,
                            },
                            "weightPerServing": {"amount": 118, "unit": "g"},
                        },
                    }
                ],
                "offset": 0,
                "number": 1,
                "totalResults": 14,
            },
        )

    def test_query_recipes_response(self):
        self.assertEqual(
            UserFoodService.query_recipes_response("banana"),
            {
                "results": [
                    {
                        "id": 634006,
                        "title": "Banana Bread",
                        "image": "https://spoonacular.com/recipeImages/634006-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 578.932,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634183,
                        "title": "Banana Spheres",
                        "image": "https://spoonacular.com/recipeImages/634183-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 204.234,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634021,
                        "title": "Banana Butter Pie",
                        "image": "https://spoonacular.com/recipeImages/634021-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 837.301,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634165,
                        "title": "Banana Prawn Rolls",
                        "image": "https://spoonacular.com/recipeImages/634165-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 301.34,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 633975,
                        "title": "Banana Almond Cake",
                        "image": "https://spoonacular.com/recipeImages/633975-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 247.237,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634202,
                        "title": "Banana Walnut Cake",
                        "image": "https://spoonacular.com/recipeImages/634202-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 155.192,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634171,
                        "title": "Banana Pudding Cake",
                        "image": "https://spoonacular.com/recipeImages/634171-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 522.033,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634070,
                        "title": "Banana Creme Brulee",
                        "image": "https://spoonacular.com/recipeImages/634070-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 292.395,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634188,
                        "title": "Banana Split Parfait",
                        "image": "https://spoonacular.com/recipeImages/634188-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 940.99,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 634189,
                        "title": "Banana Split Pudding",
                        "image": "https://spoonacular.com/recipeImages/634189-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 700.29,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                    {
                        "id": 633970,
                        "title": "Banana & Oreo Muffin",
                        "image": "https://spoonacular.com/recipeImages/633970-312x231.jpg",
                        "imageType": "jpg",
                        "nutrition": {
                            "nutrients": [
                                {
                                    "title": "Calories",
                                    "name": "Calories",
                                    "amount": 535.324,
                                    "unit": "kcal",
                                }
                            ]
                        },
                    },
                ],
                "offset": 0,
                "number": 11,
                "totalResults": 146,
            },
        )
