from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length



class UserAddForm(FlaskForm):
    """Sign up form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    height = StringField('Height',validators=[DataRequired()])


class UserEditForm(FlaskForm):
    """Edit user form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    height = StringField('(Optional) Height')
    plan = SelectField('Diet Plan')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class BMIForm(FlaskForm):
    """BMI form."""

    height = StringField("Height (feet'inches e.g. 5'4)", validators=[DataRequired()])
    weight = IntegerField('Weight (lbs)', validators=[DataRequired()])

class PlanForm(FlaskForm):
    """Diet Plan form."""

    plan = SelectField('Diet Plan')

class FoodIntakeForm(FlaskForm):
    """Food Intake form."""

    search = StringField('Search',validators=[DataRequired()])
    