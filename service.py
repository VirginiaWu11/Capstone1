from models import UserFood, db, BMI
from sqlalchemy.sql import func
from flask import g
from constants import BMI_LOW_NORMAL, BMI_HIGH_NORMAL


class UserFoodService:
    @classmethod
    def get_last_seven_user_food_information(cls, user_id):
        user_food_query = db.session.query(      
                    UserFood.date.label('date'),
                    func.sum(UserFood.calories).label("total_calories"),
                    ).filter_by(user_id=user_id)
        # querying last 7 user food entries
        last_seven_user_food_query = user_food_query.group_by(UserFood.date).order_by(UserFood.date.desc()).limit(7).all()
        # django: query.values_list('date', 'amount') => [(date_1, amount_1), (date_2, amount_2)]
        # Example shape of the last_seven_user_food_query: [sqlalchemy.util._collections.result((datetime.date(2021, 8, 7), 1697)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 5), 1140)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 4), 570)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 3), 548)), sqlalchemy.util._collections.result((datetime.date(2021, 7, 10), 1118))]

        last_seven_user_food_data = [(t[0].strftime('%m/%d/%Y'),t[1]) for t in last_seven_user_food_query]
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
            "user_food_calories": user_food_calories
        }
        # dict(user_food_dates=user_food_dates,user_food_calories=user_food_calories)

    @classmethod
    def query_user_bmi_information(cls, user_id):
        #order by date descending first to get last 7 entries, then sort by date ascending.
        user_bmi_query = BMI.query.order_by(BMI.date.desc()).filter_by(user_id=g.user.id).limit(7).all()

        date_bmi_weight_entries_ascending = [(res.date, res.bmi, res.weight) for res in user_bmi_query]
        #sorting by date - ascending
        date_bmi_weight_entries_ascending.sort()
        return date_bmi_weight_entries_ascending

    @classmethod
    def get_bmi_information(cls, date_bmi_weight_entries_ascending):
        user_bmi_dates, bmis, weights, bmi_lows_normal, bmi_highs_normal, weight_lows_normal, weight_highs_normal= [], [], [], [], [], [], []
        for t in date_bmi_weight_entries_ascending:
            user_bmi_dates.append(t[0].strftime('%m/%d/%Y'))
            bmis.append(t[1])
            weights.append(t[2])
            bmi_lows_normal.append(BMI_LOW_NORMAL)
            bmi_highs_normal.append(BMI_HIGH_NORMAL)
            weight_lows_normal.append(BMI.calculate_normal_low_weight_by_height(int(g.user.height)))
            weight_highs_normal.append(BMI.calculate_normal_high_weight_by_height(int(g.user.height)))
        return {
            "user_bmi_dates" : user_bmi_dates, 
            "bmis" : bmis, 
            "weights" : weights, 
            "bmi_lows_normal" : bmi_lows_normal,
            "bmi_highs_normal" : bmi_highs_normal,
            "weight_lows_normal" : weight_lows_normal, 
            "weight_highs_normal" : weight_highs_normal
        }