from app import db
from models import User, Food, Plan,BMI


db.drop_all()
db.create_all()