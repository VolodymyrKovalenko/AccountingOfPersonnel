from wtforms import Form,StringField,TextAreaField,PasswordField,validators,\
    BooleanField, IntegerField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


class LoginForm(Form):
    login = StringField('Login', [validators.Length(min=5, max=50)])
    password = PasswordField('Password', [validators.DataRequired()])



class ReceiptForm(Form):
    name = StringField('Name')
    receipt_date = db.Column(db.Date)
    academic_title = db.Column(db.String(45))
    year_of_birth = db.Column(db.Date)
    date_of_dismissal = db.Column(db.Date)
    address = db.Column(db.String(45))
    telephone = db.Column(db.String(45))
    previous_employment = db.Column(db.String(45))
    diploma_number = db.Column(db.String(45))

class NewSubdivisionForm(Form):
    subdivision = StringField('Subdivision',[validators.Length(min=2,max=50)])
    cypher = StringField('Cypher',[validators.Length(min=2,max=50)])

class NewDepartmentForm(Form):
    id_subdivision = IntegerField('Subdivision ID')
    department = StringField('Department',[validators.Length(min=2,max=50)])

class NewPositionForm(Form):
    name = StringField('Position')
    salary = IntegerField('Salary')