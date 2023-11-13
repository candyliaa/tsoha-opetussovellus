from app import app
from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from sqlalchemy.sql import text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not "username" in request.form or "password" not in request.form or "role" not in request.form:
            return redirect("/login?failed=1")
        username = request.form["username"]
        password = request.form["password"]
        account_type = request.form["role"]
        if account_type == "teacher":
            sql = "SELECT id, password FROM teacher_accounts WHERE username = :username"
        else:
            sql = "SELECT id, password FROM student_accounts WHERE username = :username"
        result = db.session.execute(text(sql), {"username": username})
        user = result.fetchone()
        if not user:
            return redirect("/login?failed=1")
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                    session["username"] = username
                    session["role"] = account_type
                    session["user_id"] = user[0]
                    return redirect("/")
            else:
                return redirect("/login?failed=2")
    else:
        return render_template("login.html")

@app.route("/accountcreated", methods=["POST"])
def accountcreated():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    account_type = request.form["role"]
    if account_type == "teacher":
        sql = "INSERT INTO teacher_accounts (username, password) VALUES (:username, :password)"
    else:
        sql = "INSERT INTO student_accounts (username, password) VALUES (:username, :password)"
    return_value = db.session.execute(text(sql), {"username": username, "password": hash_value})
    db.session.commit()
    session["username"] = username
    session["role"] = account_type
    session["user_id"] = return_value.fetchone()[0]
    return render_template("accountcreated.html", username=request.form["username"])

@app.route("/logout")
def logout():
    del session["username"]
    del session["role"]
    del session["user_id"]
    return redirect("/")

@app.route("/coursetools", methods=["POST", "GET"])
def coursetools():
    if not "role" in session.keys():
        return render_template("error.html", error="Ei oikeutta nähdä sivua")
    if session["role"] != "teacher":
        return render_template("error.html", error="Ei oikeutta nähdä sivua")
    if request.method == "POST":
        course_name = request.form["course_name"]
        credits = int(request.form["credits"])
        if len(course_name) < 1 or credits < 1:
            return redirect("/coursetools?status=fail")
        check_sql = "SELECT name FROM courses WHERE name = :course_name"
        if db.session.execute(text(check_sql), {"course_name": course_name}).fetchone() is not None:
            return redirect(f"/coursetools?status=already_exists&name={course_name}")
        sql = "INSERT INTO courses (name, credits) VALUES (:course_name, :credits)"
        db.session.execute(text(sql), {"course_name": course_name, "credits": credits})
        db.session.commit()
        return redirect(f"/coursetools?status=success&name={course_name}")
    courses = db.session.execute(text("""
                                      SELECT courses.id, name, credits, COUNT(course_participants.student_id) AS student_count, STRING_AGG(teacher_accounts.username, ', ') AS teacher_names
                                      FROM courses
                                      LEFT JOIN course_participants ON courses.id = course_participants.course_id
                                      LEFT JOIN course_teachers ON courses.id = course_teachers.course_id
                                      LEFT JOIN teacher_accounts ON course_teachers.teacher_id = teacher_accounts.id
                                      GROUP BY courses.id
                                      ORDER BY name ASC
                                      """)).fetchall()
    return render_template("coursetools.html", courses=courses)

@app.route("/deletecourse")
def deletecourse():
    course_id = request.args.get("id")
    if session["role"] != "teacher":
        return render_template("error.html", error="Ei oikeutta tähän toimintoon")
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(course_name_sql), {"course_id":course_id}).fetchone()[0]
    sql = "DELETE FROM courses WHERE id =:course_id"
    db.session.execute(text(sql), {"course_id": course_id})
    db.session.commit()
    return redirect(f"/coursetools?status=deleted&name={course_name}")

@app.route("/coursesview", methods=["POST", "GET"])
def coursesview():
    if "role" not in session.keys():
        return render_template("error.html", error="Ei oikeutta nähddä tätä sivua")
    if session["role"] != "student":
        return render_template("error.html", error="Et ole opiskelija")
    username = session["username"]
    user_id = session["user_id"]
    own_courses_sql = """
          SELECT courses.id, name, credits, teacher_accounts.username AS teacher_names FROM courses
          LEFT JOIN course_participants ON
          courses.id = course_participants.course_id
          LEFT JOIN course_teachers ON
          courses.id = course_teachers.course_id
          LEFT JOIN teacher_accounts ON
          course_teachers.teacher_id = teacher_accounts.id
          WHERE course_participants.student_id = :student_id
          """
    own_courses = db.session.execute(text(own_courses_sql), {"student_id": user_id}).fetchall()
    courses_sql = """
                  SELECT courses.id, name, credits, teacher_accounts.username AS teacher_names FROM courses
                  LEFT JOIN course_participants ON
                  courses.id = course_participants.course_id
                  LEFT JOIN course_teachers ON
                  courses.id = course_teachers.course_id
                  LEFT JOIN teacher_accounts ON
                  course_teachers.teacher_id = teacher_accounts.id
                  WHERE course_participants.student_id = :student_id
                  """
    return render_template("/coursesview.html", own_courses=own_courses)

