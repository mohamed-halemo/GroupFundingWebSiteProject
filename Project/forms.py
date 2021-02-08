
from flask_wtf import FlaskForm
from flask_wtf import Form
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField,SubmitField,BooleanField, TextField, TextAreaField, SubmitField
import phonenumbers

from wtforms.validators import DataRequired, Length, Email,EqualTo # , ValidationError
import email_validator

#from wtforms import TextField, TextAreaField, SubmitField

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    phonenumber = StringField('Phone')

    submit=SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')


class ContactForm(Form):

    name = StringField("Name")
    email = StringField("Email")
    subject = TextField("Private or Public?")
    message = TextAreaField("Amount of Money,No.of Members")
    submit = SubmitField("Send")

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')    