import os
import requests

from service import UserFoodService, UserBMIService

from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import UserFood, db, connect_db, User, BMI
from constants import (
    PLANS,
    ACTIVITY_LEVELS,
    BASE_API_URL,
)

from forms import (
    FoodIntakeForm,
    UserAddForm,
    LoginForm,
    BMIForm,
    PlanForm,
)

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# API_SECRET_KEY = os.environ.get("API_SECRET_KEY")

# to use in local environment, comment out
from secrets import API_SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///capstone1"

# uri = os.environ.get('DATABASE_URL',"postgresql://capstone1")
# if uri.startswith("postgres://"):
#     uri=uri.replace('postgres://','postgresql://')
# app.config["SQLALCHEMY_DATABASE_URI"] = uri

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


def login_required(func):
    """Confirm user is logged in, else redirect to home page and flash unauthorized message"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return func(*args, **kwargs)

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


@app.route("/")
def homepage():

    if not g.user:
        return render_template("home.html")

    last_seven_user_food_data = UserFoodService.get_last_seven_user_food_information(
        g.user.id
    )

    user_food_dates_and_calories = UserFoodService.get_user_food_dates_and_calories(
        last_seven_user_food_data
    )
    user_food_dates = user_food_dates_and_calories["user_food_dates"]
    user_food_calories = user_food_dates_and_calories["user_food_calories"]

    date_bmi_weight_entries_ascending = UserBMIService.query_user_bmi_information(
        g.user
    )

    user_bmi_dict = UserBMIService.get_bmi_information(
        date_bmi_weight_entries_ascending, g.user
    )
    user_bmi_dates = user_bmi_dict["user_bmi_dates"]
    bmis = user_bmi_dict["bmis"]
    weights = user_bmi_dict["weights"]
    bmi_lows_normal = user_bmi_dict["bmi_lows_normal"]
    bmi_highs_normal = user_bmi_dict["bmi_highs_normal"]
    weight_lows_normal = user_bmi_dict["weight_lows_normal"]
    weight_highs_normal = user_bmi_dict["weight_highs_normal"]

    user_calories_out = UserFoodService.get_user_calories_out(
        last_seven_user_food_data, g.user
    )

    last_recorded_bmi_date = user_bmi_dates[-1]

    user_goal_calories_in = UserFoodService.get_user_goal_calories_in(
        user_calories_out, g.user
    )

    return render_template(
        "home-loggedin.html",
        user_food_dates=user_food_dates,
        user_food_calories=user_food_calories,
        user_bmi_dates=user_bmi_dates,
        bmis=bmis,
        weights=weights,
        bmi_lows_normal=bmi_lows_normal,
        bmi_highs_normal=bmi_highs_normal,
        weight_lows_normal=weight_lows_normal,
        weight_highs_normal=weight_highs_normal,
        user_calories_out=user_calories_out,
        user_goal_calories_in=user_goal_calories_in,
        last_recorded_bmi_date=last_recorded_bmi_date,
        high_weight_normal=BMI.calculate_normal_high_weight_by_height(
            int(g.user.height)
        ),
        low_weight_normal=BMI.calculate_normal_low_weight_by_height(int(g.user.height)),
    )


###### signup/login/logout


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    form.gender.choices = [("female", "female"), ("male", "male")]
    activity_level_choices = [(al, al) for al in ACTIVITY_LEVELS]
    form.activity_level.choices = activity_level_choices
    plan_choices = [(plan, plan) for plan in PLANS]
    form.diet_plan.choices = plan_choices

    if not form.validate_on_submit():
        return render_template("users/signup.html", form=form)
    try:
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            weight=form.weight.data,
            height=BMI.cal_height_inches(form.height.data),
            image_url=form.image_url.data or User.image_url.default.arg,
            gender=form.gender.data,
            age=form.age.data,
            activity_level=form.activity_level.data,
            diet_plan=form.diet_plan.data,
        )

    except IntegrityError as e:
        flash("Username already taken", "danger")
        return render_template("users/signup.html", form=form)

    keep_login(user)
    height = BMI.cal_height_inches(form.height.data)
    weight = form.weight.data
    bmi = BMI.calculate_BMI(height, weight)
    add_bmi = BMI(bmi=bmi, weight=form.weight.data, user_id=user.id)
    db.session.add_all([add_bmi])

    db.session.commit()

    return redirect("/")


@app.route("/logout")
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", "success")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            keep_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/users/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Update profile for current user."""

    user = g.user
    form = UserAddForm(obj=user)
    form.gender.choices = [("female", "female"), ("male", "male")]
    activity_level_choices = [(al, al) for al in ACTIVITY_LEVELS]
    form.activity_level.choices = activity_level_choices
    plan_choices = [(plan, plan) for plan in PLANS]
    form.diet_plan.choices = plan_choices

    if not form.validate_on_submit():
        return render_template("users/edit.html", form=form, user_id=user.id)

    if User.authenticate(user.username, form.password.data):
        user.username = (form.username.data,)
        user.weight = (form.weight.data,)
        user.height = (BMI.cal_height_inches(form.height.data),)
        user.image_url = (form.image_url.data or User.image_url.default.arg,)
        user.gender = (form.gender.data,)
        user.age = (form.age.data,)
        user.activity_level = (form.activity_level.data,)
        user.diet_plan = form.diet_plan.data

        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi = BMI.calculate_BMI(height, weight)
        b = (
            db.session.query(BMI)
            .filter(BMI.user_id == g.user.id, BMI.date == datetime.utcnow().date())
            .first()
        )
        if not b:
            add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
            db.session.add_all([user, add_bmi])
        else:
            b.bmi = bmi
            b.weight = weight
            db.session.add_all([user, b])

        db.session.commit()
        flash("User profile successfully updated", "success")
        return redirect("/")

    flash("Wrong password, please try again.", "danger")
    return redirect("/users/profile")


###### bmi


@app.route("/bmi", methods=["GET", "POST"])
def bmi_form():
    form = BMIForm()
    plan_form = PlanForm()
    plan_choices = [(plan, plan) for plan in PLANS]
    plan_form.plan.choices = plan_choices
    if form.validate_on_submit():
        height = BMI.cal_height_inches(form.height.data)
        weight = form.weight.data
        bmi = BMI.calculate_BMI(height, weight)

        bmi_cat = BMI.BMI_range(bmi)
        lbs_away = BMI.lbs_away(bmi, height, weight)

        if g.user:
            user = g.user
            user.height = height
            user.weight = weight
            b = (
                db.session.query(BMI)
                .filter(BMI.user_id == g.user.id, BMI.date == datetime.utcnow().date())
                .first()
            )
            if not b:
                add_bmi = BMI(bmi=bmi, weight=weight, user_id=user.id)
                db.session.add_all([user, add_bmi])
            else:
                b.bmi = bmi
                b.weight = weight
                db.session.add_all([user, b])

            db.session.commit()
            return render_template(
                "users/bmi.html",
                form=form,
                bmi=bmi,
                bmi_cat=bmi_cat,
                lbs_away=lbs_away,
                plan_form=plan_form,
            )

        return render_template(
            "users/bmi.html", form=form, bmi=bmi, bmi_cat=bmi_cat, lbs_away=lbs_away
        )

    if plan_form.validate_on_submit():
        user = g.user
        user.diet_plan = plan_form.plan.data
        db.session.add(user)
        db.session.commit()
        flash("Plan successfully added/updated", "success")
        return redirect("/")

    return render_template("users/bmi.html", form=form)


@app.route("/food-intake", methods=["GET", "POST"])
def search_food():
    form = FoodIntakeForm()
    no_result = "Search recipes here."
    if not form.validate_on_submit():
        return render_template("users/food-intake.html", form=form, no_result=no_result)

    search = form.search.data

    ingredients_data = UserFoodService.query_ingredients_resp(search)

    try:
        food_id = ingredients_data["results"][0]["id"]
    except IndexError:
        flash(f'API: "{search}" not found.', "danger")
        return redirect("/food-intake")

    ingredients_data = UserFoodService.format_ingredients_data(
        food_id, ingredients_data
    )

    recipes_data = UserFoodService.query_recipes_response(search)

    # combine first ingredient and 9 recipes
    ingredients_data["results"].extend(recipes_data["results"])
    session["data"] = ingredients_data
    return render_template(
        "users/food-intake.html", form=form, ingredients_data=ingredients_data
    )


@app.route("/recipes", methods=["GET", "POST"])
def search_recipes():
    form = FoodIntakeForm()
    if form.validate_on_submit():
        search = form.search.data

        resp2 = requests.get(
            BASE_API_URL + "recipes/complexSearch",
            params={
                "query": search,
                "minCalories": 0,
                "number": 10,
                "apiKey": API_SECRET_KEY,
            },
        )
        data = resp2.json()

        return render_template("recipes.html", form=form, data=data)
    return render_template("recipes.html", form=form)


@app.route("/recipes/<int:food_id>", methods=["GET"])
def show_recipe(food_id):
    for r in session["data"]["results"]:
        if r["id"] == food_id:
            no_result = f"API error: {r['title']} recipe card not found"

    resp = requests.get(
        BASE_API_URL + f"recipes/{food_id}/card", params={"apiKey": API_SECRET_KEY}
    )
    data = resp.json()
    try:
        url = data["url"]
    except KeyError:
        flash(f"{no_result}", "danger")
        return redirect("/food-intake")
    else:
        return render_template("recipe-card.html", url=url)


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template("404.html"), 404


@app.route("/food/eat/<int:food_id>", methods=["POST"])
@login_required
def add_food(food_id):

    for arr in session["data"]["results"]:
        if arr["id"] == food_id:
            food = arr["title"]
            user_food = UserFood(
                spoon_id=arr["id"],
                user_id=g.user.id,
                name=arr["title"],
                calories=arr["nutrition"]["nutrients"][0]["amount"],
                img=arr["image"],
            )
            db.session.add(user_food)
            db.session.commit()
    flash(f"{food} successfully added", "success")
    return redirect("/food-journal")


@app.route("/food-journal")
@login_required
def show_food():
    data = UserFood.query.filter_by(user_id=g.user.id, date=datetime.utcnow().date())
    current_date = datetime.utcnow().date()
    one_week_ago = current_date - timedelta(weeks=1)
    food_within_the_last_week = UserFood.query.filter(
        UserFood.user_id == g.user.id, UserFood.date > one_week_ago
    ).all()

    return render_template(
        "users/meals.html", data=data, wfood=food_within_the_last_week
    )


@app.route("/user-food/<int:user_food_id>/delete", methods=["POST"])
@login_required
def delete_food(user_food_id):
    food = UserFood.query.get_or_404(user_food_id)
    if food.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    db.session.delete(food)
    db.session.commit()
    flash(f"{food.name} successfully deleted.", "success")
    return redirect("/food-journal")
