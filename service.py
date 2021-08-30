from models import UserFood, db
from sqlalchemy.sql import func



class UserFoodService:
    @classmethod
    def get_latest_user_food_information(cls, user_id):
        user_food_query = db.session.query(      
                    UserFood.date.label('date'),
                    func.sum(UserFood.calories).label("total_calories"),
                    ).filter_by(user_id=user_id)
        # querying last 7 user food entries
        last_7_user_food_query = user_food_query.group_by(UserFood.date).order_by(UserFood.date.desc()).limit(7).all()
        # django: query.values_list('date', 'amount') => [(date_1, amount_1), (date_2, amount_2)]
        # Example shape of the last_7_user_food_query: [sqlalchemy.util._collections.result((datetime.date(2021, 8, 7), 1697)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 5), 1140)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 4), 570)), sqlalchemy.util._collections.result((datetime.date(2021, 8, 3), 548)), sqlalchemy.util._collections.result((datetime.date(2021, 7, 10), 1118))]

        last_7_user_food_data = [(t[0].strftime('%m/%d/%Y'),t[1]) for t in last_7_user_food_query]
        # Example shape of the last_7_user_food_data: [('08/07/2021', 1697), ('08/05/2021', 1140), ('08/04/2021', 570), ('08/03/2021', 548), ('07/10/2021', 1118)]
        
        # sort by date ascending order
        last_7_user_food_data.sort()
        # Example shape of the last_7_user_food_data: [('07/10/2021', 1118), ('08/03/2021', 548), ('08/04/2021', 570), ('08/05/2021', 1140), ('08/07/2021', 1697)]
        user_food_dates, user_food_calories = [], []
        for row in last_7_user_food_data:
            user_food_dates.append(row[0])
            user_food_calories.append(row[1]) 
        return {
            "user_food_dates": user_food_dates, 
            "user_food_calories": user_food_calories
        }

        # dict(user_food_dates=user_food_dates,user_food_calories=user_food_calories)
        last_7_user_food_data
        app home - othermethod(last_7_user_food_data)

        another method