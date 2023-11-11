from flask import Flask
from os import getenv

app = Flask(__name__, static_url_path="", static_folder="public", template_folder="templates")

import routes
