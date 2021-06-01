from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, Form
from wtforms.validators import InputRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm): # class RegisterForm extends FlaskForm
    email = StringField('',validators=[InputRequired(),Length(max=50),Email(message='Invalid email')],render_kw={"placeholder": "Email"})
    username = StringField('',validators=[InputRequired(),Length(min=4,max=15)],render_kw={"placeholder": "Username"})
    password = PasswordField('',validators=[InputRequired(),Length(min=6,max=80)],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('',validators=[EqualTo('password',message='Passwords must match')],render_kw={"placeholder": "Repeat Password"})
    show = BooleanField('')

class LoginForm(FlaskForm): # class RegisterForm extends FlaskForm
    emailORusername = StringField('',validators=[InputRequired()],render_kw={"placeholder": "Username or Email"})
    password = PasswordField('',validators=[InputRequired()],render_kw={"placeholder": "Password"})
    show = BooleanField('')


class ProfileForm(FlaskForm): # class RegisterForm extends FlaskForm
    email = StringField('Email')
    username = StringField('User Name')
    profile = StringField('Profile')

class SearchForm(Form): #create form
    company = StringField('Company', validators=[InputRequired(),Length(max=15)],render_kw={"placeholder": "company symbol (min 3 letters)"})
