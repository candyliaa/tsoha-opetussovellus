from flask import Flask
from os import getenv

app = Flask(__name__, static_url_path="", static_folder="public", template_folder="templates")
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

import routes
