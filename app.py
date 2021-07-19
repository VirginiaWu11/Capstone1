import os
import requests
import json

from datetime import datetime
from functools import wraps
from secrets import API_SECRET_KEY
from sqlalchemy.sql import func

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
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
    'Lose .5lb per week; 250 calories deficit': -250,
    'Lose 1lb per week; 500 calories deficit': -500,
    'Lose 1.5lbs per week; 750 calories deficit': -750,
    'Gain .5lb per week; 250 calories surplus': 250,
    'Gain 1lb per week; 500 calories surplus': 500,
    'Gain 1.5lbs per week; 750 calories surplus': 750,
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


        return render_template('home-loggedin.html',labels=labels, values=values, labels1=labels1, values1=values1,values2=values2, values3=values3,values4=values4, values5=values5,values6=values6)

    
    return render_template('home.html')


###### signup/login/logout

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                height= BMI.cal_height_inches(form.height.data),
                image_url=form.image_url.data or User.image_url.default.arg,
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
        return redirect('/plan')

    return render_template('users/bmi.html', form=form)


@app.route('/plan',methods=['GET','POST'])
@login_required
def handle_plan():

    form= PlanForm()
    plan_choices = [(plan,plan) for plan in plans]
    form.plan.choices=plan_choices
    if form.validate_on_submit():
        user = g.user
        user.diet_plan=form.plan.data
        db.session.add(user)
        db.session.commit()
        flash('plan successfully added/updated')
        return redirect('/')
    return render_template('users/plan.html', form=form)

@app.route('/food-intake',methods=['GET','POST'])
@login_required
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


        resp2 = requests.get('https://api.spoonacular.com/recipes/complexSearch',params={"query": search,"minCalories":0, "number":3,"apiKey":API_SECRET_KEY})
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
    url=data['url']
    return render_template("recipe-card.html",url=url)

@app.route('/food/eat/<int:food_id>',methods=['POST'])
@login_required
def add_food(food_id):
    for arr in session["data"]['results']:
        if arr["id"]==food_id:
            user_food=UserFood(spoon_id=arr["id"],user_id=g.user.id,name=arr["title"],calories=arr["nutrition"]["nutrients"][0]["amount"],img=arr["image"])
            db.session.add(user_food)
            db.session.commit()
    return redirect("/")

  