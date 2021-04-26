from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class BuyForm(FlaskForm):
    submit = SubmitField('Оплатить')