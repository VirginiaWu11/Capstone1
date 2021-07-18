from os import name
from app import db
from models import User, Food,BMI, UserFood, UserIngredients


db.drop_all()
db.create_all()

user = User(
    username="123abc",
    password="$2b$12$fSlKmZ/ord1cMM3cTl18zuZw7yNtGuMlJukeyrX8N95WSsbKo/cdy",
    image_url='/static/images/default-pic.png',
)
bmi1 = BMI(
    weight = 155,
    bmi=round(703*155/((64)**2),2),
    date= '2021-07-01',
    user_id = 1
)
bmi2 = BMI(
    weight = 153,
    bmi=round(703*153/((64)**2),2),
    date= '2021-07-02',
    user_id = 1
)
bmi3 = BMI(
    weight = 145,
    bmi=round(703*145/((64)**2),2),
    date= '2021-07-03',
    user_id = 1
)

user_ing1= UserIngredients(
    spoon_id = 9040,
    user_id = 1,
    date = "2021-07-10",
    name = "banana",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/bananas.jpg"
)
user_ing2= UserIngredients(
    spoon_id = 9040,
    user_id = 1,
    date = "2021-07-10",
    name = "banana",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/bananas.jpg"
)
user_ing3= UserIngredients(
    spoon_id = 1123,
    user_id = 1,
    date = "2021-07-11",
    name = "egg",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/egg.png"
)
user_ing4= UserIngredients(
    spoon_id = 1123,
    user_id = 1,
    date = "2021-07-11",
    name = "egg",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/egg.png"
)
user_ing5= UserIngredients(
    spoon_id = 1123,
    user_id = 1,
    date = "2021-07-12",
    name = "egg",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/egg.png"
)
user_ing6= UserIngredients(
    spoon_id = 1123,
    user_id = 1,
    date = "2021-07-12",
    name = "egg",
    calories = 105,
    img = "https://spoonacular.com/cdn/ingredients_100x100/egg.png"
)

user_food1 = UserFood(
    spoon_id = 1096010,
    user_id = 1,
    date = "2021-07-10",
    name = "Egg Salad Wrap",
    calories = 570,
    img = "https://spoonacular.com/recipeImages/1096010-312x231.jpg"
)
user_food2 = UserFood(
    spoon_id = 642240,
    user_id = 1,
    date = "2021-07-10",
    name = "Egg Salad Sandwiches With Tarragon",
    calories = 274,
    img = "https://spoonacular.com/recipeImages/642240-312x231.jpg"
)
user_food3 = UserFood(
    spoon_id = 642240,
    user_id = 1,
    date = "2021-07-10",
    name = "Egg Salad Sandwiches With Tarragon",
    calories = 274,
    img = "https://spoonacular.com/recipeImages/642240-312x231.jpg"
)
user_food4 = UserFood(
    spoon_id = 642240,
    user_id = 1,
    date = "2021-07-11",
    name = "Egg Salad Sandwiches With Tarragon",
    calories = 274,
    img = "https://spoonacular.com/recipeImages/642240-312x231.jpg"
)
user_food5 = UserFood(
    spoon_id = 642240,
    user_id = 1,
    date = "2021-07-12",
    name = "Egg Salad Sandwiches With Tarragon",
    calories = 274,
    img = "https://spoonacular.com/recipeImages/642240-312x231.jpg"
)
user_food6 = UserFood(
    spoon_id = 1096010,
    user_id = 1,
    date = "2021-07-13",
    name = "Egg Salad Wrap",
    calories = 570,
    img = "https://spoonacular.com/recipeImages/1096010-312x231.jpg"
)
user_food7 = UserFood(
    spoon_id = 1096010,
    user_id = 1,
    date = "2021-07-14",
    name = "Egg Salad Wrap",
    calories = 570,
    img = "https://spoonacular.com/recipeImages/1096010-312x231.jpg"
)
user_food8 = UserFood(
    spoon_id = 1096010,
    user_id = 1,
    date = "2021-07-14",
    name = "Egg Salad Wrap",
    calories = 570,
    img = "https://spoonacular.com/recipeImages/1096010-312x231.jpg"
)



db.session.add_all([user,bmi1,bmi2,bmi3])
# user_ing2,user_ing3,user_ing4,user_ing5,user_ing6,user_food1,user_food2,user_food3,user_food4,user_food5,user_food6,user_food7,user_food8])
db.session.commit()
db.session.add_all([user_ing1,user_ing2,user_ing3,user_ing4,user_ing5,user_ing6,user_food1,user_food2,user_food3,user_food4,user_food5,user_food6,user_food7,user_food8])
db.session.commit()
