import os
from flask import Flask, render_template, request, flash, redirect, url_for
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
    product_category = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=False)
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


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        usrname = request.form.get("usrname")
        usremail = request.form.get("usremail")
        usrsubject = request.form.get("usrsubject")
        usrmsg = request.form.get("usrmsg")
        entry = Contact(name=usrname, email=usremail,
                        subject=usrsubject, message=usrmsg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("new message from " + usrname +
                          " ." + usrsubject, sender=usremail, body=usrmsg, recipients=[params['gmail-user']])
    return render_template("contact.html")


@app.route("/stories")
def stories():
    return render_template("blog.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/categories")
def categories():

    categories = Category.query.filter_by().all()
    return render_template("categories.html", categories=categories)

@app.route("/add-category", methods=['GET', 'POST'])
def addCategory():

    if(request.method == 'POST'):

        category_name = request.form.get("category_name")

        entry = Category(category_name=category_name)

        db.session.add(entry)
        db.session.commit()

    return render_template("add_category.html")

@app.route("/categories/edit/<category_id>", methods=['GET', 'POST'])
def categoriesEdit(category_id):
    if(request.method == 'POST'):
        category_name = request.form.get("category_name")

        selected_category = Category.query.get_or_404(category_id)

        selected_category.category_name = category_name

        db.session.commit()

    category = Category.query.filter_by(id=category_id).first()
    return render_template("edit_category.html", category=category)


@app.route("/categories/delete/<category_id>")
def categoryDelete(category_id):
    category = Category.query.get_or_404(category_id)

    products_to_be_deleted = Product.query.filter_by(product_category=category_id).all()

    for product in products_to_be_deleted :
        db.session.delete(product)
        db.session.commit()

    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("categories"))


@app.route("/products")
def products():
    products = Product.query.filter_by().all()
    return render_template("products.html", products=products)


@app.route("/add-product", methods=['GET', 'POST'])
def addProduct():

    if(request.method == 'POST'):

        product_name = request.form.get("product_name")
        product_category = request.form.get("product_category")
        product_price = request.form.get("product_price")
        product_description = request.form.get("product_description")
        product_image = request.form.get("product_image")

        entry = Product(product_name=product_name, product_category=product_category,
                        product_price=product_price, product_description=product_description, product_image=product_image)

        db.session.add(entry)
        db.session.commit()
    categories = Category.query.filter_by().all()
    return render_template("add_product.html",categories=categories)


@app.route("/products/edit/<product_id>", methods=['GET', 'POST'])
def productdit(product_id):
    if(request.method == 'POST'):

        product_name = request.form.get("product_name")
        product_category = request.form.get("product_category")
        product_price = request.form.get("product_price")
        product_description = request.form.get("product_description")
        product_image = request.form.get("product_image")

        selected_product = Product.query.get_or_404(product_id)

        selected_product.product_name = product_name
        selected_product.product_category = product_category
        selected_product.product_price = product_price
        selected_product.product_description = product_description
        selected_product.product_image = product_image

        db.session.commit()

    product = Product.query.filter_by(id=product_id).first()
    categories = Category.query.filter_by().all()
    return render_template("edit_product.html", product=product , categories=categories)


@app.route("/products/delete/<product_id>")
def productDelete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("products"))


if __name__ == "__main__":
    app.run(debug=True)
