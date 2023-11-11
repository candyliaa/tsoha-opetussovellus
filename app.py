from flask import Flask
from os import getenv

app = Flask(__name__, static_url_path="", static_folder="public", template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

import routes
