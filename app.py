from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///tsoha"
db = SQLAlchemy(app)

db.session.execute("CREATE TABLE testi (id SERIAL PRIMARY KEY, content TEXT);")
db.session.execute("INSERT INTO testi (content) VALUES ('just testing!');")
db.session.execute("SELECT * FROM testi;")

@app.route("/")
def index():
    result = db.session.execute("SELECT content FROM test")
    return result
