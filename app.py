from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost/tsoha"
db = SQLAlchemy(app)

with app.app_context():
    db.session.execute(text("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, content TEXT);"))
    db.session.commit()
    db.session.execute(text("INSERT INTO test (content) VALUES ('just testing!');"))
    db.session.commit()

@app.route("/")
def index():
    result = db.session.execute(text("SELECT * FROM test;"))
    return result.fetchone()[1]
