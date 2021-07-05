import os

from functools import wraps
from secrets import API_SECRET_KEY

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, BMI

from forms import UserAddForm, UserEditForm, LoginForm, BMIForm, planForm

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
        return render_template('home-loggedin.html')
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
    plan_form= planForm()
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
            user.bmi.bmi = bmi
            user.height = height
            add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
            db.session.add_all([user,add_bmi])
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

    form= planForm()
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