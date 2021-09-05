import os
import requests
import json

from service import UserFoodService

from datetime import datetime, timedelta
from functools import wraps

from sqlalchemy.sql import func

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user

from models import UserFood, db, connect_db, User, BMI
from constants import PLANS, ACTIVITY_LEVELS, BMI_LOW_NORMAL, BMI_HIGH_NORMAL, BASE_API_URL

from forms import FoodIntakeForm, UserAddForm, UserEditForm, LoginForm, BMIForm, PlanForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

API_SECRET_KEY = os.environ.get("API_SECRET_KEY")

# to use in local environment, comment out
# from secrets import API_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres:///capstone1'

# uri = os.environ.get('DATABASE_URL',"postgresql://capstone1") 
# if uri.startswith("postgres://"):
#     uri=uri.replace('postgres://','postgresql://')
# app.config["SQLALCHEMY_DATABASE_URI"] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
def login_required(func):
    """Confirm user is logged in, else redirect to home page and flash unauthorized message"""
    @wraps(func)
    def wrapper(*args,**kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return func(*args,**kwargs)
    return wrapper

def keep_login(user):
    """Add user to session."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Remove user from Session."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.route('/')
def homepage():
    
    if not g.user:
        return render_template('home.html')
        
    last_seven_user_food_data = UserFoodService.get_last_seven_user_food_information(g.user.id)

    user_food_dates_and_calories = UserFoodService.get_user_food_dates_and_calories(last_seven_user_food_data)
    user_food_dates = user_food_dates_and_calories["user_food_dates"]
    user_food_calories = user_food_dates_and_calories["user_food_calories"]

    date_bmi_weight_entries_ascending = UserFoodService.query_user_bmi_information(g.user)

    user_bmi_dict = UserFoodService.get_bmi_information(date_bmi_weight_entries_ascending, g.user)
    user_bmi_dates = user_bmi_dict["user_bmi_dates"]
    bmis = user_bmi_dict["bmis"]
    weights = user_bmi_dict["weights"]
    bmi_lows_normal = user_bmi_dict["bmi_lows_normal"]
    bmi_highs_normal = user_bmi_dict["bmi_highs_normal"]
    weight_lows_normal = user_bmi_dict["weight_lows_normal"]
    weight_highs_normal = user_bmi_dict["weight_highs_normal"]

    user_calories_out = UserFoodService.get_user_calories_out(last_seven_user_food_data, g.user)

    last_recorded_bmi_date = user_bmi_dates[-1]

    user_goal_calories_in = UserFoodService.get_user_goal_calories_in(user_calories_out, g.user)
    
    return render_template('home-loggedin.html',user_food_dates=user_food_dates, user_food_calories=user_food_calories, user_bmi_dates=user_bmi_dates, bmis=bmis,weights=weights, bmi_lows_normal=bmi_lows_normal,bmi_highs_normal=bmi_highs_normal, weight_lows_normal=weight_lows_normal,weight_highs_normal=weight_highs_normal,
    user_calories_out=user_calories_out,user_goal_calories_in=user_goal_calories_in, last_recorded_bmi_date=last_recorded_bmi_date,high_weight_normal=BMI.calculate_normal_high_weight_by_height(int(g.user.height)),low_weight_normal=BMI.calculate_normal_low_weight_by_height(int(g.user.height)))


###### signup/login/logout

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    form.gender.choices=[("female","female"),("male","male")]
    activity_level_choices= [(al,al) for al in ACTIVITY_LEVELS]
    form.activity_level.choices=activity_level_choices
    plan_choices = [(plan,plan) for plan in PLANS]
    form.diet_plan.choices=plan_choices

    if not form.validate_on_submit():
        return render_template('users/signup.html', form=form)
    try:
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            weight=form.weight.data,
            height= BMI.cal_height_inches(form.height.data),
            image_url=form.image_url.data or User.image_url.default.arg,
            gender=form.gender.data,
            age=form.age.data,
            activity_level=form.activity_level.data,
            diet_plan=form.diet_plan.data
        )

    except IntegrityError as e:
        flash("Username already taken", 'danger')
        return render_template('users/signup.html', form=form)

    keep_login(user)
    height = BMI.cal_height_inches(form.height.data)
    weight = form.weight.data
    bmi =  BMI.calculate_BMI(height,weight)
    add_bmi = BMI(bmi=bmi, weight=form.weight.data, user_id=user.id)
    db.session.add_all([add_bmi])
    
    db.session.commit()

    return redirect("/")

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/")

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            keep_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    """Update profile for current user."""
    
    user = g.user
    form = UserAddForm(obj=user)
    form.gender.choices=[("female","female"),("male","male")]
    activity_level_choices= [(al,al) for al in ACTIVITY_LEVELS]
    form.activity_level.choices=activity_level_choices
    plan_choices = [(plan,plan) for plan in PLANS]
    form.diet_plan.choices=plan_choices

    if not form.validate_on_submit():
        return render_template('users/edit.html', form=form, user_id=user.id)

    if User.authenticate(user.username, form.password.data):
        user.username = form.username.data,
        user.weight = form.weight.data,
        user.height = BMI.cal_height_inches(form.height.data),
        user.image_url = form.image_url.data or User.image_url.default.arg,
        user.gender = form.gender.data,
        user.age = form.age.data,
        user.activity_level = form.activity_level.data,
        user.diet_plan = form.diet_plan.data

        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi =  BMI.calculate_BMI(height,weight)
        b = db.session.query(BMI).filter(BMI.user_id==g.user.id,BMI.date==datetime.utcnow().date()).first()
        if not b:
            add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
            db.session.add_all([user,add_bmi])
        else:
            b.bmi=bmi
            b.weight=weight
            db.session.add_all([user,b])

        db.session.commit()
        flash("User profile successfully updated","success")
        return redirect("/")

    flash("Wrong password, please try again.", 'danger')
    return redirect('/users/profile')
    

###### bmi

@app.route('/bmi',methods=['GET','POST'])
def bmi_form():
    form = BMIForm()
    plan_form= PlanForm()
    plan_choices = [(plan,plan) for plan in PLANS]
    plan_form.plan.choices=plan_choices
    if form.validate_on_submit():
        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi =  BMI.calculate_BMI(height,weight)
        
        bmi_cat = BMI.BMI_range(bmi)
        lbs_away = BMI.lbs_away(bmi,height,weight)

        if g.user:            
            user = g.user
            user.height = height
            user.weight = weight
            b = db.session.query(BMI).filter(BMI.user_id==g.user.id,BMI.date==datetime.utcnow().date()).first()
            if not b:
                add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
                db.session.add_all([user,add_bmi])
            else:
                b.bmi=bmi
                b.weight=weight
                db.session.add_all([user,b])

            db.session.commit()
            return render_template('users/bmi.html', form=form,bmi=bmi,bmi_cat=bmi_cat,lbs_away=lbs_away,plan_form=plan_form)

        return render_template('users/bmi.html', form=form,bmi=bmi,bmi_cat=bmi_cat,lbs_away=lbs_away)

    if plan_form.validate_on_submit():
        user = g.user
        user.diet_plan=plan_form.plan.data
        db.session.add(user)
        db.session.commit()
        flash('Plan successfully added/updated','success')
        return redirect('/')

    return render_template('users/bmi.html', form=form)

@app.route('/food-intake',methods=['GET','POST'])
def search_food():
    form = FoodIntakeForm()
    no_result="Search recipes here."
    if not form.validate_on_submit():
        return render_template('users/food-intake.html', form=form,no_result=no_result)

    search = form.search.data
    # Base URL constant added
    ingredients_resp = requests.get(BASE_API_URL+'food/ingredients/search',params={"query": search, "number":1,"apiKey":API_SECRET_KEY})
    
    ingredients_data=ingredients_resp.json()
    try:
        food_id= ingredients_data['results'][0]['id']
    except IndexError:
        flash(f'API: "{search}" not found.', 'danger')
        return redirect("/food-intake")
    imge = ingredients_data['results'][0]['image']
    img_url= "https://spoonacular.com/cdn/ingredients_100x100/"+imge
    
    ingredients_data['results'][0]['image'] = img_url
    ingredients_data['results'][0]['title']=ingredients_data['results'][0]['name']

    ingredients_calories_resp = requests.get(BASE_API_URL+f'food/ingredients/{food_id}/information',params={"amount": 1,"apiKey":API_SECRET_KEY})
    ingredients_calories_content = ingredients_calories_resp.json()
    # Example shape of the ingredients_calories_content: {'id': 9040, 'original': 'ripe bananas', 'originalName': 'ripe bananas', 'name': 'ripe bananas', 'amount': 1.0, 'unit': '', 'unitShort': '', 'unitLong': '', 'possibleUnits': ['small', 'large', 'piece', 'slice', 'g', 'extra small', 'medium', 'oz',   ], 'estimatedCost': {'value': 15.73, 'unit': 'US Cents'}, 'consistency': 'solid', 'shoppingListUnits': ['pieces'], 'aisle': 'Produce', 'image': 'bananas.jpg', 'meta': [], 'nutrition': {'nutrients': [{'title': 'Iron', 'name': 'Iron', 'amount': 0.31, 'unit': 'mg'}, {'title': 'Phosphorus', 'name': 'Phosphorus', 'amount': 25.96, 'unit': 'mg'}, {'title': 'Vitamin B3', 'name': 'Vitamin B3', 'amount': 0.78, 'unit': 'mg'}, {'title': 'Mono Unsaturated Fat', 'name': 'Mono Unsaturated Fat', 'amount': 0.04, 'unit': 'g'}, {'title': 'Manganese', 'name': 'Manganese', 'amount': 0.32, 'unit': 'mg'}, {'title': 'Vitamin D', 'name': 'Vitamin D', 'amount': 0.0, 'unit': 'µg'}, {'title': 'Folic Acid', 'name': 'Folic Acid', 'amount': 0.0, 'unit': 'µg'}, {'title': 'Vitamin C', 'name': 'Vitamin C', 'amount': 10.27, 'unit': 'mg'},   ], 'properties': [{'name': 'Glycemic Index', 'title': 'Glycemic Index', 'amount': 54.78, 'unit': ''}, {'name': 'Glycemic Load', 'title': 'Glycemic Load', 'amount': 13.08, 'unit': ''}], 'flavonoids': [{'name': 'Cyanidin', 'title': 'Cyanidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Petunidin', 'title': 'Petunidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Delphinidin', 'title': 'Delphinidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Malvidin', 'title': 'Malvidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Pelargonidin', 'title': 'Pelargonidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Peonidin', 'title': 'Peonidin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Catechin', 'title': 'Catechin', 'amount': 7.2, 'unit': 'mg'}, {'name': 'Epigallocatechin', 'title': 'Epigallocatechin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Epicatechin', 'title': 'Epicatechin', 'amount': 0.02, 'unit': 'mg'}, {'name': 'Epicatechin 3-gallate', 'title': 'Epicatechin 3-gallate', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Epigallocatechin 3-gallate', 'title': 'Epigallocatechin 3-gallate', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Theaflavin', 'title': 'Theaflavin', 'amount': 0.0, 'unit': ''}, {'name': 'Thearubigins', 'title': 'Thearubigins', 'amount': 0.0, 'unit': ''}, {'name': 'Eriodictyol', 'title': 'Eriodictyol', 'amount': 0.0, 'unit': ''}, {'name': 'Hesperetin', 'title': 'Hesperetin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Naringenin', 'title': 'Naringenin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Apigenin', 'title': 'Apigenin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Luteolin', 'title': 'Luteolin', 'amount': 0.0, 'unit': 'mg'}, {'name': 'Isorhamnetin', 'title': 'Isorhamnetin', 'amount': 0.0, 'unit': ''}, {'name': 'Kaempferol', 'title': 'Kaempferol', 'amount': 0.13, 'unit': 'mg'}, {'name': 'Myricetin', 'title': 'Myricetin', 'amount': 0.01, 'unit': 'mg'}, {'name': 'Quercetin', 'title': 'Quercetin', 'amount': 0.07, 'unit': 'mg'}, {'name': "Theaflavin-3,3'-digallate", 'title': "Theaflavin-3,3'-digallate", 'amount': 0.0, 'unit': ''}, {'name': "Theaflavin-3'-gallate", 'title': "Theaflavin-3'-gallate", 'amount': 0.0, 'unit': ''}, {'name': 'Theaflavin-3-gallate', 'title': 'Theaflavin-3-gallate', 'amount': 0.0, 'unit': ''}, {'name': 'Gallocatechin', 'title': 'Gallocatechin', 'amount': 0.0, 'unit': 'mg'}  ], 'caloricBreakdown': {'percentProtein': 4.42, 'percentFat': 3.01, 'percentCarbs': 92.57}, 'weightPerServing': {'amount': 118, 'unit': 'g'}  }, 'categoryPath': ['banana', 'tropical fruit', 'fruit']  }
    
    for obj in ingredients_calories_content["nutrition"]["nutrients"]:
        if obj["title"]=="Calories":
            ingredients_calories_content["nutrition"]["nutrients"][0]=obj

    ingredients_data['results'][0]["nutrition"]=ingredients_calories_content["nutrition"]

    recipes_resp = requests.get(BASE_API_URL+'recipes/complexSearch',params={"query": search,"minCalories":0, "number":11,"apiKey":API_SECRET_KEY})
    recipes_data = recipes_resp.json() 

    ingredients_data['results'].extend(recipes_data['results'])
    session["data"] = ingredients_data
    return render_template('users/food-intake.html', form=form, ingredients_data=ingredients_data)
    

@app.route('/recipes',methods=['GET','POST'])
def search_recipes():
    form = FoodIntakeForm()
    if form.validate_on_submit():
        search = form.search.data
        
        resp2 = requests.get(BASE_API_URL+'recipes/complexSearch',params={"query": search,"minCalories":0, "number":10,"apiKey":API_SECRET_KEY})
        data = resp2.json() 

        return render_template('recipes.html', form=form, data=data)
    return render_template('recipes.html', form=form)

@app.route('/recipes/<int:food_id>',methods=['GET'])
def show_recipe(food_id):
    for r in session['data']['results']:  
        if r['id'] == food_id:
            no_result = f"API error: {r['title']} recipe card not found"
    
    resp = requests.get(BASE_API_URL+f'recipes/{food_id}/card',params={"apiKey":API_SECRET_KEY})
    data = resp.json()
    try:
        url=data['url']
    except KeyError:
        flash(f"{no_result}","danger")
        return redirect('/food-intake')
    else:
        return render_template("recipe-card.html",url=url)  

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

@app.route('/food/eat/<int:food_id>',methods=['POST'])
@login_required
def add_food(food_id):
    
    for arr in session["data"]['results']:
        if arr["id"]==food_id:
            food=arr['title']
            user_food=UserFood(spoon_id=arr["id"],user_id=g.user.id,name=arr["title"],calories=arr["nutrition"]["nutrients"][0]["amount"],img=arr["image"])
            db.session.add(user_food)
            db.session.commit()
    flash(f"{food} successfully added","success")
    return redirect("/food-journal")

@app.route("/food-journal")
@login_required
def show_food():
    data = UserFood.query.filter_by(user_id=g.user.id, date= datetime.utcnow().date())
    current_date = datetime.utcnow().date()
    one_week_ago= current_date - timedelta(weeks=1)
    food_within_the_last_week = UserFood.query.filter(UserFood.user_id==g.user.id,UserFood.date>one_week_ago).all()

    return render_template('users/meals.html', data=data, wfood=food_within_the_last_week)

@app.route("/user-food/<int:user_food_id>/delete", methods=["POST"])
@login_required
def delete_food(user_food_id):
    food = UserFood.query.get_or_404(user_food_id)
    if food.user_id!= g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    db.session.delete(food)
    db.session.commit()
    flash(f"{food.name} successfully deleted.", "success")
    return redirect("/food-journal")

