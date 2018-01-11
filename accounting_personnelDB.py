#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask, render_template, request, redirect, url_for, session, json

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.login

class Subdivision(db.Model):
    __tablename__ = 'subdivision'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45), unique=True)
    cypher = db.Column(db.String(45), unique=True)
    departments = db.relationship('Department', backref='department', lazy='dynamic')

    def __init__(self,name,cypher):
        self.name = name
        self.cypher = cypher


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45), unique=True)
    subdivision_id = db.Column(db.INTEGER, db.ForeignKey('subdivision.id'))
    worksheets = db.relationship('Worksheet', backref='worksheet1', lazy='dynamic')

    def __init__(self,name,subdivision_id):
        self.name = name
        self.subdivision_id = subdivision_id

    def __repr__(self):
        return self.name


class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45), unique=True)
    salary = db.Column(db.INTEGER)
    worksheets = db.relationship('Worksheet', backref='worksheet2', lazy='dynamic')

    def __init__(self,name,salary):
        self.name = name
        self.salary = salary

class Worksheet(db.Model):
    __tablename__= 'worksheet'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    department_id = db.Column(db.INTEGER, db.ForeignKey('department.id'))
    receipt_date = db.Column(db.Date)
    position_id = db.Column(db.INTEGER, db.ForeignKey('position.id'))
    academic_title = db.Column(db.String(45))
    year_of_birth = db.Column(db.Date)
    date_of_dismissal = db.Column(db.Date)
    address = db.Column(db.String(45))
    telephone = db.Column(db.String(45))
    previous_employment = db.Column(db.String(45))
    diploma_number = db.Column(db.String(45))


    def __init__(self,name,department_id,receipt_date,position_id,academic_title,year_of_birth,date_of_dismissal,address,telephone,previous_employment,diploma_number):
        self.name = name
        self.department_id = department_id
        self.receipt_date = receipt_date
        self.position_id = position_id
        self.academic_title = academic_title
        self.year_of_birth = year_of_birth
        self.date_of_dismissal = date_of_dismissal
        self.address = address
        self.telephone = telephone
        self.previous_employment = previous_employment
        self.diploma_number = diploma_number



if __name__ == '__main__':
    manager.run()






