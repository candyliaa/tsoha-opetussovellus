from app import app
from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from db import db
from sqlalchemy.sql import text

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    name = request.form["name"]
    password = request.form["password"]
    account_type = request.form["role"]
    sql = f"SELECT id, password FROM {account_type}_accounts WHERE name=:name"
    result = db.session.execute(text(sql), {"name":name})
    user = result.fetchone()
    if not user:
        # code for when user doesn't exist
        pass
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            # logged in
            pass
        else:
            # invalid login
            pass
    session["name"] = name
    return redirect("/")

@app.route("/accountcreated", methods=["POST"])
def accountcreated():
    name = request.form["name"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    account_type = request.form["role"]
    sql = f"INSERT INTO {account_type}_accounts (name, password) VALUES (:name, :password)"
    db.session.execute(text(sql), {"name":name, "password":hash_value})
    db.session.commit()
    return render_template("accountcreated.html", name=request.form["name"])

@app.route("/logout")
def logout():
    del session["name"]
    return redirect("/")
