from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class RegisterForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(),
                                             Length(min=1, max=254)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=1, max=254)])
    confirm = PasswordField('Repeat Password',
                            validators=[DataRequired(),
                                        EqualTo('password')])


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
