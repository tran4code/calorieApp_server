from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    IntegerField,
)
from wtforms import DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from apps import App


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        app_object = App()
        mongo = app_object.mongo

        temp = mongo.db.user.find_one({"email": email.data}, {"email", "pwd"})
        if temp:
            raise ValidationError("Email already exists!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class FoodForm(FlaskForm):
    app = App()
    mongo = app.mongo

    # Read database for food options
    cursor = mongo.db.food.find()
    get_docs = []
    for record in cursor:
        get_docs.append(record)

    result = []
    temp = ""
    for i in get_docs:
        temp = i["food"] + " (" + str(i["calories"]) + " cal)"
        result.append((temp, temp))

    food = SelectField(
        "Select Food",
        choices=result,
    )

    amount = IntegerField("Portion (grams)")

    submit = SubmitField("Save")


class ActivityForm(FlaskForm):
    app = App()
    mongo = app.mongo

    activities = mongo.db.activities.find()
    choices = [
        (
            entry["activity"]
            + " ("
            + "{:.2f}".format(entry["burn_rate"])
            + ".../kg/hr"
            + ")"
        )
        for entry in activities
    ]

    activity = SelectField("Activity", choices=choices)
    duration = IntegerField("Duration (minutes)")
    submit = SubmitField("Burn")


class UserProfileForm(FlaskForm):
    weight = StringField("Weight", validators=[DataRequired(), Length(min=2, max=20)])
    height = StringField("Height", validators=[DataRequired(), Length(min=2, max=20)])
    goal = StringField("Goal", validators=[DataRequired(), Length(min=2, max=20)])
    target_weight = StringField(
        "Target Weight", validators=[DataRequired(), Length(min=2, max=20)]
    )
    submit = SubmitField("Save Profile")


class HistoryForm(FlaskForm):
    app = App()
    mongo = app.mongo
    date = DateField()
    submit = SubmitField("Fetch")


class EnrollForm(FlaskForm):
    app = App()
    mongo = app.mongo
    submit = SubmitField("Enroll")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset")
