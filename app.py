import os

from functools import wraps

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, BMI

from forms import UserAddForm, UserEditForm, LoginForm, BMIForm

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

    if form.validate_on_submit():
        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi =  BMI.calculate_BMI(height,weight)
        # print('***************************',height,form.weight.data,bmi)
        # import pdb
        # pdb.set_trace()
        if g.user:
            user = g.user
            user.bmi.bmi = bmi
            user.height = height
            add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
            db.session.add_all([user,add_bmi])
            db.session.commit()
            return render_template('users/bmi.html', form=form,bmi=bmi)
        return render_template('users/bmi.html', form=form,bmi=bmi)


    return render_template('users/bmi.html', form=form)