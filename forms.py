from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms import StringField, PasswordField, HiddenField, SubmitField, FileField, SelectField


class SignUp(FlaskForm):
    Name = StringField('Name', validators=[InputRequired(), Length(min=3)])
    Username = StringField(
        "Username", validators=[InputRequired(), Length(min=5, max=16)]
    )
    Phone = StringField("Phone", validators=[
                        InputRequired(), Length(min=10, max=10)])
    Password = PasswordField(
        "Password", validators=[InputRequired(), EqualTo("Confirm_Password", message="Passwords Must Match"), Length(min=8, max=30)]
    )
    Confirm_Password = PasswordField(
        "Confirm Password", validators=[InputRequired(), Length(min=8, max=30)]
    )
    Email = StringField("Email", validators=[InputRequired(), Email(
        message="Must be a Valid Email Address"), Length(max=100)])
    Submit = SubmitField(label=('SignUp'))


class Login(FlaskForm):
    UsernameorEmail = StringField("UsernameorEmail", validators=[
                                  InputRequired(), Length(max=100)])
    Password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8, max=30)])
    Submit = SubmitField(label=('Login'))

class Files(FlaskForm):
    Index = HiddenField("Index")
    File_Name = StringField("File Name", validators=[InputRequired()])
    File_Type = StringField("File Type", validators=[InputRequired()])
    Rename = SubmitField(name="button", label="Rename", id="Rename")
    Rename_new = HiddenField("Rename_new")
    Delete = SubmitField(name="button", label="Delete", id="Delete")
    Download = SubmitField(name="button", label="Download", id = "Download")
    Share = SubmitField(name="button", label="Share", id="Share")
    
class Upload(FlaskForm):
    File = FileField("report", validators=[InputRequired()])
    File_Type = SelectField("File Type", choices=[("public", "Public"), ("private", "Private")] )
    Upload = SubmitField(name="button", label="Upload")
    
