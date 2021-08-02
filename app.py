import os
import requests
import json

from datetime import datetime, timedelta
from functools import wraps
from secrets import API_SECRET_KEY
from sqlalchemy.sql import func

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user
from wtforms.fields.simple import PasswordField

from models import UserFood, db, connect_db, User, BMI

from forms import FoodIntakeForm, UserAddForm, UserEditForm, LoginForm, BMIForm, PlanForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///capstone1'))

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

plans = {
    'Maintain current weight; 0 calories deficit':0,
    'Lose .5lb per week; 250 calories deficit': -250,
    'Lose 1lb per week; 500 calories deficit': -500,
    'Lose 1.5lbs per week; 750 calories deficit': -750,
    'Gain .5lb per week; 250 calories surplus': 250,
    'Gain 1lb per week; 500 calories surplus': 500,
    'Gain 1.5lbs per week; 750 calories surplus': 750,
}

activity_levels={
    "Sedentary (little to no exercise)":1.2,
    "Lightly active (light exercise 1–3 days per week)":1.375,
    "Moderately active (moderate exercise 3–5 days per week)":1.55,
    "Very active (hard exercise 6–7 days per week)":1.725,
    "Extra active (very hard exercise, training, or a physical job)":1.9
}


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
    
    if g.user:
         
        qry = db.session.query(      
                    UserFood.date.label('date'),
                    func.sum(UserFood.calories).label("total_calories"),
                    ).filter_by(user_id=g.user.id)
        qry = qry.group_by(UserFood.date)

        data = [res for res in qry.all()]
        # print("*****************",dat)
        data=[(t[0].strftime('%m/%d/%Y'),t[1]) for t in data]
        data.sort()
        

        # import pdb;pdb.set_trace()
        labels = [row[0] for row in data]
        values = [row[1] for row in data]
        

        # qry1 = db.session.query(
                    
        #             # BMI.date.label('date'),
        #             func.max(BMI.date).label("date"),
        #             BMI.bmi.label("BMI"),
        #             # BMI.weight.label("weight")
                   
        #             ).filter_by(user_id=g.user.id)
        # qry1 = qry1.group_by(BMI.bmi, 
        # # BMI.weight
        # )

        qry1 = BMI.query.filter_by(user_id=g.user.id)


        data1 = [(res.date,res.bmi, res.weight) for res in qry1.all()]
        print("*****************",data1)
        height = int(g.user.height)

        

        data1=[(t[0].strftime('%m/%d/%Y'),t[1],t[2],18.5,24.9,int(18.01*((height)**2)/703),int(25*((height)**2)/703)) for t in data1]
        data1.sort()
            
        # import pdb;pdb.set_trace()
        labels1 = [row[0] for row in data1]
        values1 = [row[1] for row in data1]
        values2 = [row[2] for row in data1]
        values3 = [row[3] for row in data1]
        values4 = [row[4] for row in data1]
        values5 = [row[5] for row in data1]
        values6 = [row[6] for row in data1]
        #### calories out
        values7 = [int(User.basal_metabolic_rate(g.user.weight,height,g.user.age,g.user.gender)*activity_levels[g.user.activity_level]) for row in data]

        #### Goal Calories In
        values8 = [c_out+plans[g.user.diet_plan] for c_out in values7]
        # import pdb;pdb.set_trace()
        return render_template('home-loggedin.html',labels=labels, values=values, labels1=labels1, values1=values1,values2=values2, values3=values3,values4=values4, values5=values5,values6=values6,
        values7=values7,values8=values8)
        

    
    return render_template('home.html')


###### signup/login/logout

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    form.gender.choices=[("female","female"),("male","male")]
    activity_level_choices= [(al,al) for al in activity_levels]
    form.activity_level.choices=activity_level_choices
    plan_choices = [(plan,plan) for plan in plans]
    form.diet_plan.choices=plan_choices

    if form.validate_on_submit():
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

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

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
        user = User.authenticate(form.username.data,
                                 form.password.data)

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
    activity_level_choices= [(al,al) for al in activity_levels]
    form.activity_level.choices=activity_level_choices
    plan_choices = [(plan,plan) for plan in plans]
    form.diet_plan.choices=plan_choices

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data,
            user.weight=form.weight.data,
            user.height= BMI.cal_height_inches(form.height.data),
            user.image_url=form.image_url.data or User.image_url.default.arg,
            user.gender=form.gender.data,
            user.age=form.age.data,
            user.activity_level=form.activity_level.data,
            user.diet_plan=form.diet_plan.data
            db.session.commit()
            flash("User profile successfully updated","success")
            return redirect("/")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)


###### bmi

@app.route('/bmi',methods=['GET','POST'])
def bmiForm():
    form = BMIForm()
    plan_form= PlanForm()
    plan_choices = [(plan,plan) for plan in plans]
    plan_form.plan.choices=plan_choices
    if form.validate_on_submit():
        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi =  BMI.calculate_BMI(height,weight)
        bmi_cat = BMI.BMI_range(bmi)
        lbs_away = BMI.lbs_away(bmi,height,weight)

        if g.user:            
            user = g.user
            # user.bmi.bmi = bmi
            # raise
            # import pdb;pdb.set_trace()
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


# @app.route('/plan',methods=['GET','POST'])
# @login_required
# def handle_plan():

#     form= PlanForm()
#     plan_choices = [(plan,plan) for plan in plans]
#     form.plan.choices=plan_choices
#     if form.validate_on_submit():
#         user = g.user
#         user.diet_plan=form.plan.data
#         db.session.add(user)
#         db.session.commit()
#         flash('plan successfully added/updated')
#         return redirect('/')
#     return render_template('users/plan.html', form=form)

@app.route('/food-intake',methods=['GET','POST'])
def search_food():
    form = FoodIntakeForm()
    if form.validate_on_submit():
        search = form.search.data
        resp = requests.get('https://api.spoonacular.com/food/ingredients/search',params={"query": search, "number":1,"apiKey":API_SECRET_KEY})
       
        data=resp.json()
        food_id= data['results'][0]['id']
        name=data['results'][0]['name']
        

        imge = data['results'][0]['image']
        img_url= "https://spoonacular.com/cdn/ingredients_100x100/"+imge
        

        
        
        data['results'][0]['image'] = img_url
        data['results'][0]['title']=data['results'][0]['name']

        cal_resp = requests.get(f'https://api.spoonacular.com/food/ingredients/{food_id}/information',params={"amount": 1,"apiKey":API_SECRET_KEY})
        content = cal_resp.json()
        for obj in content["nutrition"]["nutrients"]:
            if obj["title"]=="Calories":
                content["nutrition"]["nutrients"][0]=obj

        data['results'][0]["nutrition"]=content["nutrition"]


        resp2 = requests.get('https://api.spoonacular.com/recipes/complexSearch',params={"query": search,"minCalories":0, "number":11,"apiKey":API_SECRET_KEY})
        data2 = resp2.json() 

        data['results'].extend(data2['results'])
        session["data"] = data

        return render_template('users/food-intake.html', form=form, data=data)
    return render_template('users/food-intake.html', form=form)


@app.route('/recipes',methods=['GET','POST'])
def search_recipes():
    form = FoodIntakeForm()
    if form.validate_on_submit():
        search = form.search.data
        
        resp2 = requests.get('https://api.spoonacular.com/recipes/complexSearch',params={"query": search,"minCalories":0, "number":10,"apiKey":API_SECRET_KEY})
        data = resp2.json() 

        return render_template('recipes.html', form=form, data=data)
    return render_template('recipes.html', form=form)


@app.route('/recipes/<int:food_id>',methods=['GET'])
def show_recipe(food_id):
    
    resp = requests.get(f'https://api.spoonacular.com/recipes/{food_id}/card',params={"apiKey":API_SECRET_KEY})
    data = resp.json()
    # import pdb;pdb.set_trace()
    print("*************************", data)
    try:
        url=data['url']
        return render_template("recipe-card.html",url=url)  
    except KeyError:
        return render_template('404.html'), 404



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
    # import pdb;pdb.set_trace()

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

