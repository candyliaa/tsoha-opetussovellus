from app import app
from flask import render_template, request, redirect

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    pass

@app.route("/accountcreated", methods=["POST"])
def accountcreated():
    return render_template("accountcreated.html", name=request.form["name"])
