from models import UserFood, db, BMI, User
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


class UserFoodService:
    @classmethod
    def get_last_seven_user_food_information(cls, user_id):
        user_food_query = db.session.query(
            UserFood.date.label("date"),
            func.sum(UserFood.calories).label("total_calories"),
        ).filter_by(user_id=user_id)
        # querying last 7 user food entries
        last_seven_user_food_query = (
            user_food_query.group_by(UserFood.date)
            .order_by(UserFood.date.desc())
            .limit(7)
            .all()
        )
        # django: query.values_list('date', 'amount') => [(date_1, amount_1), (date_2, amount_2)]
        # Example shape of the last_seven_user_food_query: [sqlalchemy.util._collections.result((datetime.date(2021, 8, 7), 1697)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 5), 1140)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 4), 570)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 3), 548)), sqlalchemy.util._collections.result((datetime.date(2021, 7, 10), 1118))]

        last_seven_user_food_data = [
            (t[0].strftime("%m/%d/%Y"), t[1]) for t in last_seven_user_food_query
        ]
        # Example shape of the last_seven_user_food_data: [('08/07/2021', 1697), ('08/05/2021', 1140), ('08/04/2021', 570), ('08/03/2021', 548), ('07/10/2021', 1118)]

        # sort by date ascending order
        last_seven_user_food_data.sort()
        # Example shape of the last_seven_user_food_data: [('07/10/2021', 1118), ('08/03/2021', 548), ('08/04/2021', 570), ('08/05/2021', 1140), ('08/07/2021', 1697)]

        return last_seven_user_food_data

    @classmethod
    def get_user_food_dates_and_calories(cls, last_seven_user_food_data):
        user_food_dates, user_food_calories = [], []
        for row in last_seven_user_food_data:
            user_food_dates.append(row[0])
            user_food_calories.append(row[1])
        return {
            "user_food_dates": user_food_dates,
            "user_food_calories": user_food_calories,
        }
        # dict(user_food_dates=user_food_dates,user_food_calories=user_food_calories)

    @classmethod
    def get_user_calories_out(cls, last_seven_user_food_data, user):
        #### calories out
        return [
            int(
                User.basal_metabolic_rate(
                    user.weight, int(user.height), user.age, user.gender
                )
                * ACTIVITY_LEVELS[user.activity_level]
            )
            for row in last_seven_user_food_data
        ]

    @classmethod
    def get_user_goal_calories_in(cls, user_calories_out, user):
        #### Goal Calories In
        user_goal_calories_in = [
            calories_out + PLANS[user.diet_plan] for calories_out in user_calories_out
        ]
        return user_goal_calories_in

    # food-intake Route
    @classmethod
    def query_ingredients_resp(cls, search):
        ingredients_resp = requests.get(
            BASE_API_URL + "food/ingredients/search",
            params={"query": search, "number": 1, "apiKey": API_SECRET_KEY},
        )
        ingredients_data = ingredients_resp.json()
        return ingredients_data

    @classmethod
    def format_ingredients_data(cls, food_id, ingredients_data):
        imge = ingredients_data["results"][0]["image"]
        img_url = BASE_INGREDIENTS_IMG_URL + imge

        ingredients_data["results"][0]["image"] = img_url
        ingredients_data["results"][0]["title"] = ingredients_data["results"][0]["name"]

        ingredients_calories_resp = requests.get(
            BASE_API_URL + f"food/ingredients/{food_id}/information",
            params={"amount": 1, "apiKey": API_SECRET_KEY},
        )
        ingredients_calories_content = ingredients_calories_resp.json()
        # Example shape of the ingredients_calories_content: {'id': 9040, 'original': 'ripe bananas', 'originalName': 'ripe bananas', 'name': 'ripe bananas', 'amount': 1.0, 'unit': '', 'unitShort': '', 'unitLong': '', 'possibleUnits': ['small', 'large', 'piece', 'slice', 'g', 'extra small', 'medium', 'oz',   ], 'estimatedCost': {'value': 15.73, 'unit': 'US Cents'}, 'consistency': 'solid', 'shoppingListUnits': ['pieces'], 'aisle': 'Produce', 'image': 'bananas.jpg', 'meta': [], 'nutrition': {'nutrients': [{'title': 'Iron', 'name': 'Iron', 'amount': 0.31, 'unit': 'mg'}, {'title': 'Phosphorus', 'name': 'Phosphorus', 'amount': 25.96, 'unit': 'mg'}, {'title': 'Vitamin B3', 'name': 'Vitamin B3', 'amount': 0.78, 'unit': 'mg'}, {'title': 'Mono Unsaturated Fat', 'name': 'Mono Unsaturated Fat', 'amount': 0.04, 'unit': 'g'}, {'title': 'Manganese', 'name': 'Manganese', 'amount': 0.32, 'unit': 'mg'}, {'title': 'Vitamin D', 'name': 'Vitamin D', 'amount': 0.0, 'unit': 'µg'}, {'title': 'Folic Acid', 'name': 'Folic Acid', 'amount': 0.0, 'unit': 'µg'}, {'title': 'Vitamin C', 'name': 'Vitamin C', 'amount': 10.27, 'unit': 'mg'},   ], 'properties': [{'name': 'Glycemic Index', 'title': 'Glycemic Index', 'amount': 54.78, 'unit': ''}, {'name': 'Glycemic Load', 'title': 'Glycemic Load', 'amount': 13.08, 'unit': ''}], 'flavonoids': [{'name': 'Cyanidin', 'title': 'Cyanidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Petunidin', 'title': 'Petunidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Delphinidin', 'title': 'Delphinidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Malvidin', 'title': 'Malvidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Pelargonidin', 'title': 'Pelargonidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Peonidin', 'title': 'Peonidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Catechin', 'title': 'Catechin', 'amount': 7.2, 'unit': 'mg'}, {'name': 'Epigallocatechin', 'title': 'Epigallocatechin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Epicatechin', 'title': 'Epicatechin', 'amount': 0.02, 'unit': 'mg'}, {'name': 'Epicatechin 3-gallate', 'title': 'Epicatechin 3-gallate', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Epigallocatechin 3-gallate', 'title': 'Epigallocatechin 3-gallate', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Theaflavin', 'title': 'Theaflavin', 'amount': 0.0, 'unit': ''}, {'name': 'Thearubigins', 'title': 'Thearubigins', 'amount': 0.0, 'unit': ''}, {'name': 'Eriodictyol', 'title': 'Eriodictyol', 'amount': 0.0, 'unit': ''}, {'name': 'Hesperetin', 'title': 'Hesperetin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Naringenin', 'title': 'Naringenin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Apigenin', 'title': 'Apigenin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Luteolin', 'title': 'Luteolin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Isorhamnetin', 'title': 'Isorhamnetin', 'amount': 0.0, 'unit': ''}, {'name': 'Kaempferol', 'title': 'Kaempferol', 'amount': 0.13, 'unit': 'mg'}, {'name': 'Myricetin', 'title': 'Myricetin', 'amount': 0.01, 'unit': 'mg'}, {'name': 'Quercetin', 'title': 'Quercetin', 'amount': 0.07, 'unit': 'mg'}, {'name': "Theaflavin-3,3'-digallate", 'title': "Theaflavin-3,3'-digallate", 'amount': 0.0, 'unit': ''}, {'name': "Theaflavin-3'-gallate", 'title': "Theaflavin-3'-gallate", 'amount': 0.0, 'unit': ''}, {'name': 'Theaflavin-3-gallate', 'title': 'Theaflavin-3-gallate', 'amount': 0.0, 'unit': ''}, {'name': 'Gallocatechin', 'title': 'Gallocatechin', 'amount': 0.0, 'unit': 'mg'}  ], 'caloricBreakdown': {'percentProtein': 4.42, 'percentFat': 3.01, 'percentCarbs': 92.57}, 'weightPerServing': {'amount': 118, 'unit': 'g'}  }, 'categoryPath': ['banana', 'tropical fruit', 'fruit']  }

        for obj in ingredients_calories_content["nutrition"]["nutrients"]:
            if obj["title"] == "Calories":
                ingredients_calories_content["nutrition"]["nutrients"][0] = obj

        ingredients_data["results"][0]["nutrition"] = ingredients_calories_content[
            "nutrition"
        ]
        return ingredients_data

    @classmethod
    def query_recipes_response(cls, search):
        return requests.get(
            BASE_API_URL + "recipes/complexSearch",
            params={
                "query": search,
                "minCalories": 0,
                "number": 11,
                "apiKey": API_SECRET_KEY,
            },
        ).json()


class UserBMIService:
    @classmethod
    def query_user_bmi_information(cls, user):
        # order by date descending first to get last 7 entries, then sort by date ascending.
        user_bmi_query = (
            BMI.query.order_by(BMI.date.desc())
            .filter_by(user_id=user.id)
            .limit(7)
            .all()
        )

        date_bmi_weight_entries_ascending = [
            (res.date, res.bmi, res.weight) for res in user_bmi_query
        ]
        # sorting by date - ascending
        date_bmi_weight_entries_ascending.sort()
        return date_bmi_weight_entries_ascending

    @classmethod
    def get_bmi_information(cls, date_bmi_weight_entries_ascending, user):
        (
            user_bmi_dates,
            bmis,
            weights,
            bmi_lows_normal,
            bmi_highs_normal,
            weight_lows_normal,
            weight_highs_normal,
        ) = ([], [], [], [], [], [], [])
        for t in date_bmi_weight_entries_ascending:
            user_bmi_dates.append(t[0].strftime("%m/%d/%Y"))
            bmis.append(t[1])
            weights.append(t[2])
            bmi_lows_normal.append(BMI_LOW_NORMAL)
            bmi_highs_normal.append(BMI_HIGH_NORMAL)
            weight_lows_normal.append(
                BMI.calculate_normal_low_weight_by_height(int(user.height))
            )
            weight_highs_normal.append(
                BMI.calculate_normal_high_weight_by_height(int(user.height))
            )
        return {
            "user_bmi_dates": user_bmi_dates,
            "bmis": bmis,
            "weights": weights,
            "bmi_lows_normal": bmi_lows_normal,
            "bmi_highs_normal": bmi_highs_normal,
            "weight_lows_normal": weight_lows_normal,
            "weight_highs_normal": weight_highs_normal,
        }
