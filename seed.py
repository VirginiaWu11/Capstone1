from app import db
from models import User, Food, Plan,BMI


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


db.session.add_all([user,bmi1,bmi2,bmi3])
db.session.commit()