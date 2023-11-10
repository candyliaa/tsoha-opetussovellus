from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__, static_url_path="", static_folder="public", template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost/tsoha"
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")
