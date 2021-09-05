from os import name
from app import db
from models import User, BMI, UserFood


db.drop_all()
db.create_all()

user = User(
    username="User1",
    password="$2b$12$fSlKmZ/ord1cMM3cTl18zuZw7yNtGuMlJukeyrX8N95WSsbKo/cdy",
    weight=150,
    height=64,
    image_url="/static/images/default-pic.png",
    gender="female",
    age=30,
    activity_level="Sedentary (little to no exercise)",
)
bmi1 = BMI(
    weight=155, bmi=round(703 * 155 / ((64) ** 2), 2), date="2021-08-01", user_id=1
)
bmi2 = BMI(
    weight=153, bmi=round(703 * 153 / ((64) ** 2), 2), date="2021-08-02", user_id=1
)
bmi3 = BMI(
    weight=145, bmi=round(703 * 145 / ((64) ** 2), 2), date="2021-08-04", user_id=1
)
bmi4 = BMI(
    weight=142, bmi=round(703 * 142 / ((64) ** 2), 2), date="2021-08-07", user_id=1
)


user_food1 = UserFood(
    spoon_id=1096010,
    user_id=1,
    date="2021-07-10",
    name="Egg Salad Wrap",
    calories=570,
    img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
)
user_food2 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-07-10",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food3 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-07-10",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food4 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-08-03",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food5 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-08-03",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food6 = UserFood(
    spoon_id=1096010,
    user_id=1,
    date="2021-08-04",
    name="Egg Salad Wrap",
    calories=570,
    img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
)
user_food7 = UserFood(
    spoon_id=1096010,
    user_id=1,
    date="2021-08-05",
    name="Egg Salad Wrap",
    calories=570,
    img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
)
user_food8 = UserFood(
    spoon_id=1096010,
    user_id=1,
    date="2021-08-05",
    name="Egg Salad Wrap",
    calories=570,
    img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
)
user_food9 = UserFood(
    spoon_id=1096010,
    user_id=1,
    date="2021-08-07",
    name="Egg Salad Wrap",
    calories=570,
    img="https://spoonacular.com/recipeImages/1096010-312x231.jpg",
)
user_food10 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-08-07",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food11 = UserFood(
    spoon_id=642240,
    user_id=1,
    date="2021-08-07",
    name="Egg Salad Sandwiches With Tarragon",
    calories=274,
    img="https://spoonacular.com/recipeImages/642240-312x231.jpg",
)
user_food12 = UserFood(
    spoon_id=634006,
    user_id=1,
    date="2021-08-07",
    name="Banana Bread",
    calories=579,
    img="https://spoonacular.com/recipeImages/634006-312x231.jpg",
)


db.session.add_all([user, bmi1, bmi2, bmi3, bmi4])
db.session.commit()
db.session.add_all(
    [
        user_food1,
        user_food2,
        user_food3,
        user_food4,
        user_food5,
        user_food6,
        user_food7,
        user_food8,
        user_food9,
        user_food10,
        user_food11,
        user_food12,
    ]
)
db.session.commit()
