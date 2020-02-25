import os
from flask import Flask,render_template,request
import json
import sqlite3
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = "any_random_string"
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
) 

mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)



class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)



class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(80), nullable=False)
    product_category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_description = db.Column(db.String(1000), nullable=False)
    product_image = db.Column(db.String(1000), nullable=False)

class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(1000), nullable=False)
    message = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/",methods=['GET', 'POST'])
def home(): 
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/contact",methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        usrname = request.form.get("usrname")
        usremail = request.form.get("usremail")
        usrsubject = request.form.get("usrsubject")
        usrmsg = request.form.get("usrmsg")
        entry = Contact(name=usrname , email = usremail , subject = usrsubject, message = usrmsg, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("new message from " + usrname +
                          " ." + usrsubject,sender=usremail, body=usrmsg, recipients=[params['gmail-user']])
    return render_template("contact.html")
   

@app.route("/stories")
def stories():
    return render_template("blog.html")



if __name__ == "__main__":
    app.run( debug = True )