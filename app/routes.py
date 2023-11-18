from app import app
from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from sqlalchemy.sql import text
import json

def permission_check(role = None):
    if "role" not in session.keys() or session["role"] != role:
        return False
    return True

def student_in_course():
    student_id = session["user_id"]
    student_in_course_check_sql = """
                                    SELECT student_id
                                    FROM course_participants
                                    WHERE student_id = :student_id
                                    """
    if db.session.execute(text(student_in_course_check_sql), {"student_id": student_id}).fetchone() is None:
        return False
    return True

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
    if not permission_check():
        return render_template("error.html", error="Et ole luonut tiliä!")
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    account_type = request.form["role"]
    if account_type == "teacher":
        sql = "INSERT INTO teacher_accounts (username, password) VALUES (:username, :password) RETURNING id"
    else:
        sql = "INSERT INTO student_accounts (username, password) VALUES (:username, :password) RETURNING id"
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
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    courses_sql = """
                  SELECT courses.id, name, credits, COUNT(course_participants.student_id) AS student_count, STRING_AGG(teacher_accounts.username, ', ') AS teacher_names
                  FROM courses
                  LEFT JOIN course_participants ON courses.id = course_participants.course_id
                  LEFT JOIN course_teachers ON courses.id = course_teachers.course_id
                  LEFT JOIN teacher_accounts ON course_teachers.teacher_id = teacher_accounts.id
                  GROUP BY courses.id
                  ORDER BY name ASC
                  """
    courses = db.session.execute(text(courses_sql)).fetchall()
    return render_template("coursetools.html", courses=courses)

@app.route("/createcourse", methods=["POST"])
def createcourse():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
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

@app.route("/deletecourse")
def deletecourse():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args.get("id")
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(course_name_sql), {"course_id":course_id}).fetchone()[0]
    sql = "DELETE FROM courses WHERE id =:course_id"
    db.session.execute(text(sql), {"course_id": course_id})
    db.session.commit()
    return redirect(f"/coursetools?status=deleted&name={course_name}")

@app.route("/modifycourse", methods=["POST", "GET"])
def modifycourse():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args.get("id")
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(text(materials_sql), {"course_id": course_id}).fetchall()

    course_exercises_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id ORDER BY id"                     
    course_exercises = db.session.execute(text(course_exercises_sql), {"course_id": course_id}).fetchall()
    exercises = []
    for exercise in course_exercises:
        exercises.append((exercise[0], exercise[1], exercise[2]))

    course_participants_sql = """
                              SELECT id, username
                              FROM course_participants
                              LEFT JOIN student_accounts
                              ON course_participants.student_id = student_accounts.id
                              WHERE course_id = :course_id
                              """
    course_participants = db.session.execute(text(course_participants_sql), {"course_id": course_id}).fetchall()

    current_exercise_submissions_sql = """
                                       SELECT student_id, correct
                                       FROM exercise_answers
                                       WHERE exercise_id = :exercise_id
                                       """
    submissions = []
    for exercise in course_exercises:
        exercise_submission = {}
        all_submissions = db.session.execute(text(current_exercise_submissions_sql), {"exercise_id": exercise[0]}).fetchall()
        all_submissions_dict = {}
        for submission in all_submissions:
            all_submissions_dict[submission[0]] = submission[1]

        for student in course_participants:
            exercise_submission[student[0]] = {
                "username": student[1],
            }
            if student[0] not in all_submissions_dict:
                exercise_submission[student[0]]["state"] = "missing"
            elif all_submissions_dict[student[0]]:
                exercise_submission[student[0]]["state"] = "correct"
            elif not all_submissions_dict[student[0]]:
                exercise_submission[student[0]]["state"] = "incorrect"
        submissions.append(exercise_submission)
    return render_template(f"/modifycourse.html", course=course, exercises=exercises, materials=materials, submissions=submissions)

@app.route("/addtextmaterial", methods=["POST"])
def addtextmaterial():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.form["course_id"]
    title = request.form["title"]
    body = request.form["body"]
    add_material_sql = """
                       INSERT INTO text_materials (title, body, course_id)
                       VALUES (:title, :body, :course_id)
                       """
    db.session.execute(text(add_material_sql), {"title": title, "body": body, "course_id": course_id})
    db.session.commit()
    return redirect(f"/modifycourse?id={course_id}&status=material_added")

@app.route("/exercisecreated", methods=["POST"])
def exercisecreated():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    if request.method == "POST":
        if request.form["exercise_type"] == "text_question":
            course_id = request.form["course_id"]
            question = request.form["question"]
            example_answer = request.form["example_answer"]
            example_answer = json.dumps(example_answer)
            add_exercise_sql = """
                               INSERT INTO exercises (question, choices, course_id)
                               VALUES (:question, :choices, :course_id)
                               """
            db.session.execute(text(add_exercise_sql), {"question": question, "choices": example_answer, "course_id": course_id})
            db.session.commit()
        elif request.form["exercise_type"] == "multiple_choice":
            question = request.form["question"]
            course_id = request.form["course_id"]

            choice1 = request.form["choice1"]
            choice2 = request.form["choice2"]
            choice3 = request.form["choice3"]
            choice4 = request.form["choice4"]
            choices = [choice1, choice2, choice3, choice4]
            correct_answer = request.form["correct_answer"]
            
            choices_dict = {}
            choices_dict["choices"] = choices
            choices_dict["correct_answer"] = correct_answer
            choices_dict = json.dumps(choices_dict)
            add_exercise_sql = """
                               INSERT INTO exercises (question, choices, course_id)
                               VALUES (:question, :choices, :course_id)
                               """
            db.session.execute(text(add_exercise_sql), {"question": question, "choices": choices_dict, "course_id": course_id})
            db.session.commit()
        return redirect(f"/modifycourse?id={course_id}&status=exercise_added")

@app.route("/delete_exercise", methods=["POST", "GET"])
def delete_exercise():
    if not permission_check("teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args.get("course_id")
    exercise_id = request.args.get("exercise_id")
    delete_exercise_sql = """
                          DELETE FROM exercises
                          WHERE course_id = :course_id AND id = :exercise_id
                          """
    db.session.execute(text(delete_exercise_sql), {"course_id": course_id, "exercise_id": exercise_id})
    db.session.commit()
    return redirect(f"/modifycourse?id={course_id}&status=exercise_removed")

@app.route("/coursesview", methods=["POST", "GET"])
def coursesview():
    if not permission_check("student"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    user_id = session["user_id"]
    courses_sql = """
                  SELECT
                   courses.id,
                   courses.name,
                   courses.credits,
                   STRING_AGG(teacher_accounts.username, ', ') AS teacher_names,
                   ARRAY_AGG(course_participants.student_id) AS student_ids
                  FROM courses
                  LEFT JOIN course_participants ON
                  courses.id = course_participants.course_id
                  LEFT JOIN course_teachers ON
                  courses.id = course_teachers.course_id
                  LEFT JOIN teacher_accounts ON
                  course_teachers.teacher_id = teacher_accounts.id
                  GROUP BY courses.id
                  ORDER BY name ASC
                  """
    all_courses = db.session.execute(text(courses_sql)).fetchall()
    own_courses = list(filter(lambda c: user_id in c[4], all_courses))
    other_courses = list(filter(lambda c: user_id not in c[4], all_courses))
    exercises_done_sql = """
                         SELECT course_id, COUNT(id) 
                         FROM exercise_answers
                         WHERE student_id = :student_id
                         GROUP BY course_id
                         """
    exercises_done = db.session.execute(text(exercises_done_sql), {"student_id": user_id}).fetchall()
    exercises_done_dict = {}
    for course in exercises_done:
        exercises_done_dict[course[0]] = course[1]
    total_exercises_sql = """
                          SELECT course_id, COUNT(id)
                          FROM exercises
                          GROUP BY course_id
                          """
    total_exercises = db.session.execute(text(total_exercises_sql)).fetchall()
    total_exercises_dict = {}
    for course in total_exercises:
        total_exercises_dict[course[0]] = course[1]
    return render_template("/coursesview.html", own_courses=own_courses, other_courses=other_courses, exercises_done_dict=exercises_done_dict, total_exercises_dict=total_exercises_dict)

@app.route("/exercises_materials", methods=["POST", "GET"])
def exercises_materials():
    if not permission_check("student"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    student_in_course()
    course_id = request.args["id"]
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(text(materials_sql), {"course_id": course_id}).fetchall()
    
    course_exercises_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id ORDER BY id"                     
    course_exercises = db.session.execute(text(course_exercises_sql), {"course_id": course_id}).fetchall()
    exercises = []
    for exercise in course_exercises:
        exercises.append((exercise[0], exercise[1], exercise[2]))

    return render_template(f"/exercises_materials.html", course=course, exercises=exercises, materials=materials)

@app.route("/do_exercise", methods=["POST", "GET"])
def do_exercise():
    if not permission_check("student") or not student_in_course():
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args["course_id"]
    course = db.session.execute(text("SELECT id, name FROM courses WHERE id = :course_id"), {"course_id": course_id}).fetchone()
    exercise_id = request.args["exercise_id"]
    exercise_num = request.args["exercise_num"]
    exercise_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id AND id = :id"
    exercise = db.session.execute(text(exercise_sql), {"course_id": course_id, "id": exercise_id}).fetchone()
    return render_template(f"/do_exercise.html", exercise=exercise, exercise_num=exercise_num, course=course)

@app.route("/submit_answer", methods=["POST", "GET"])
def submit_answer():
    if not permission_check("student") or not student_in_course():
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    answer = request.form["answer"]
    student_id = session["user_id"]
    course_id = request.form["course_id"]
    exercise_id = request.form["exercise_id"]
    exercise_type = request.form["exercise_type"]
    exercise_num = request.form["exercise_num"]

    exercise_sql = "SELECT id, choices, course_id FROM exercises WHERE id = :exercise_id"
    exercise = db.session.execute(text(exercise_sql), {"exercise_id": exercise_id}).fetchone()

    check_if_answer_exists_sql = """
                                 SELECT answer, student_id, course_id, exercise_id
                                 FROM exercise_answers
                                 WHERE student_id = :student_id AND course_id = :course_id AND exercise_id = :exercise_id
                                 """
    result = db.session.execute(text(check_if_answer_exists_sql), {"answer": answer, "student_id": student_id, "course_id": course_id, "exercise_id": exercise_id}).fetchone()
    if result is not None:
        status = "already_submitted"
        return redirect(f"/do_exercise?course_id={course_id}&exercise_id={exercise_id}&exercise_num={exercise_num}&status={status}")

    add_exercise_sql = """
                       INSERT INTO exercise_answers (answer, student_id, course_id, exercise_id, correct)
                       VALUES (:answer, :student_id, :course_id, :exercise_id, :correct)
                       """
    if exercise_type == "text_exercise":
        if answer == exercise[1]:
            status = True
        else:
            status = False
    elif exercise_type == "multiple_choice":
        if answer == exercise[1]["correct_answer"]:
            status = True
        else:
            status = False
    db.session.execute(text(add_exercise_sql), {"answer": answer, "student_id": student_id, "course_id": course_id, "exercise_id": exercise_id, "correct": status})
    db.session.commit()
    return redirect(f"/do_exercise?course_id={course_id}&exercise_id={exercise_id}&exercise_num={exercise_num}&status={status}")

@app.route("/joincourse")
def joincourse():
    if not permission_check("student"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args.get("id")
    student_id = session["user_id"]
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(course_name_sql), {"course_id": course_id}).fetchone()[0]
    course_join_sql = """
                      INSERT INTO course_participants (course_id, student_id)
                      VALUES (:course_id, :student_id)
                      """
    db.session.execute(text(course_join_sql), {"course_id": course_id, "student_id": student_id})
    db.session.commit()
    return redirect(f"/coursesview?status=joined&name={course_name}")

@app.route("/leavecourse")
def leavecourse():
    if not permission_check("student") or not student_in_course():
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_id = request.args.get("id")
    student_id = session["user_id"]
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(course_name_sql), {"course_id": course_id}).fetchone()[0]
    leave_course_sql = """
                       DELETE FROM course_participants
                       WHERE student_id = :student_id
                       AND course_id = :course_id
                       """
    delete_submissions_sql = """
                             DELETE FROM exercise_answers
                             WHERE student_id = :student_id
                             AND course_id = :course_id
                             """
    db.session.execute(text(leave_course_sql), {"student_id": student_id, "course_id": course_id})
    db.session.commit()
    db.session.execute(text(delete_submissions_sql), {"student_id": student_id, "course_id": course_id})
    db.session.commit()
    return redirect(f"/coursesview?status=left&name={course_name}")
