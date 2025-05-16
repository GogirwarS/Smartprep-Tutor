from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User
from datetime import datetime


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    branch = StringField('Branch', validators=[DataRequired(), Length(min=2, max=100)])
    year_of_passing = IntegerField('Year of Passing', 
                                 validators=[DataRequired(), 
                                             NumberRange(min=datetime.now().year, 
                                                         max=datetime.now().year + 10,
                                                         message='Year must be current or future year')])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=15, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
