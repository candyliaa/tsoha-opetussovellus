"""File containing all routes."""
import json
from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
import data
from app import app
from db import db

@app.route("/")
def index():
    """Return the main page for the user."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Route logic for logging in."""
    if request.method == "POST":
        if not "username" in request.form \
        or "password" not in request.form \
        or "role" not in request.form:
            return redirect("/login?failed=1")
        username = request.form["username"]
        password = request.form["password"]
        account_type = request.form["role"]
        user = data.login_fetch_user(account_type, username)
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
    """Create an account and insert into the database."""
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    account_type = request.form["role"]
    user_id = data.create_account(account_type, username, hash_value)
    session["username"] = username
    session["role"] = account_type
    session["user_id"] = user_id
    return render_template("accountcreated.html", username=request.form["username"])

@app.route("/logout")
def logout():
    """Delete current session values upon logging out."""
    del session["username"]
    del session["role"]
    del session["user_id"]
    return redirect("/")

@app.route("/coursetools", methods=["POST", "GET"])
def coursetools():
    """Show teachers a page to view all courses."""
    if not data.permission_check(session, "teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    courses = data.coursetools_courses()
    return render_template("coursetools.html", courses=courses)

@app.route("/createcourse", methods=["POST"])
def createcourse():
    """Create a course and add it to the database."""
    if not data.permission_check(session, "teacher"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    if request.method == "POST":
        course_name = request.form["course_name"]
        course_credits = int(request.form["credits"])
        if len(course_name) < 1 or credits < 1:
            return redirect("/coursetools?status=fail")
        if not data.create_course(course_name, course_credits, session):
            return redirect(f"/coursetools?status=already_exists&name={course_name}")
        else:
            return redirect(f"/coursetools?status=success&name={course_name}")

@app.route("/deletecourse")
def deletecourse():
    """Remove a course from the database."""
    course_id = request.args.get("id")
    if not data.permission_check(session, "teacher") \
    or not data.correct_teacher(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_name = data.delete_course(course_id)
    return redirect(f"/coursetools?status=deleted&name={course_name}")

@app.route("/modifycourse", methods=["POST", "GET"])
def modifycourse():
    """Add or exercises or text materials, or remove exercises."""
    course_id = request.args.get("id")
    if not data.permission_check(session, "teacher") or \
    not data.correct_teacher(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")

    course_data = data.modify_course_data(course_id)
    course = course_data["course"]
    course_materials = course_data["materials"]

    course_exercises = course_data["course_exercises"]
    exercises = []
    for exercise in course_exercises:
        exercises.append((exercise[0], exercise[1], exercise[2]))

    course_participants = course_data["course_participants"]
    current_exercise_submissions_sql = course_data["current_exercise_submissions_sql"]
    submissions = []
    for exercise in course_exercises:
        exercise_submission = {}
        all_submissions = db.session.execute(
            text(current_exercise_submissions_sql),
            {"exercise_id": exercise[0]}
        ).fetchall()
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
    return render_template("/modifycourse.html",
    course=course,
    exercises=exercises,
    materials=course_materials,
    submissions=submissions)

@app.route("/addtextmaterial", methods=["POST"])
def addtextmaterial():
    """Add text materials and insert into the database."""
    course_id = request.form["course_id"]
    if not data.permission_check(session, "teacher") or \
    not data.correct_teacher(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")

    course_id = request.form["course_id"]
    title = request.form["title"]
    body = request.form["body"]
    data.add_material(course_id, title, body)
    return redirect(f"/modifycourse?id={course_id}&status=material_added")

@app.route("/exercisecreated", methods=["POST"])
def exercisecreated():
    """Create an exercise of the user's choosing and insert into the database."""
    course_id = request.form["course_id"]
    if not data.permission_check(session, "teacher") or \
    not data.correct_teacher(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    if request.method == "POST":
        exercise_type = request.form["exercise_type"]
        if exercise_type == "text_question":
            course_id = request.form["course_id"]
            question = request.form["question"]
            example_answer = request.form["example_answer"]
            data.create_exercise(course_id, question, example_answer, exercise_type)
        elif exercise_type == "multiple_choice":
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
            data.create_exercise(course_id, question, example_answer, exercise_type, choices_dict)
        return redirect(f"/modifycourse?id={course_id}&status=exercise_added")

@app.route("/delete_exercise", methods=["POST", "GET"])
def delete_exercise():
    """Delete the chosen exercise and remove it from the database."""
    course_id = request.args.get("course_id")
    if not data.permission_check(session, "teacher") or \
    not data.correct_teacher(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")

    exercise_id = request.args.get("exercise_id")
    if not data.delete_exercise(course_id, exercise_id):
        return redirect(f"/modifycourse?id={course_id}status=remove_failed")
    return redirect(f"/modifycourse?id={course_id}&status=exercise_removed")

@app.route("/coursesview", methods=["POST", "GET"])
def coursesview():
    """Display a page for students to view all courses."""
    if not data.permission_check(session, "student"):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    user_id = session["user_id"]
    courses_sql = """
                  SELECT 
                    courses.id,
                    name,
                    credits,
                    COALESCE(student_ids, '{}'),
                    teacher_accounts.username
                  FROM courses
                  LEFT JOIN teacher_accounts ON courses.teacher_id = teacher_accounts.id
                  LEFT JOIN (
                    SELECT course_id, ARRAY_AGG(student_id) AS student_ids
                    FROM course_participants
                    GROUP BY course_id
                    ) 
                  p ON courses.id = p.course_id
                  """
    all_courses = db.session.execute(text(courses_sql)).fetchall()
    own_courses = list(filter(lambda c: user_id in c[3], all_courses))
    other_courses = list(filter(lambda c: user_id not in c[3], all_courses))
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
    """Display the exercises and materials for the given course."""
    course_id = request.args["id"]
    if not data.permission_check(session, "student") \
    or not data.student_in_course(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(text(materials_sql), {"course_id": course_id}).fetchall()

    student_id = session["user_id"]
    course_exercises_sql = """
                           SELECT 
                           exercises.id, 
                           question,
                           choices
                           FROM exercises
                           WHERE exercises.course_id = :course_id
                           ORDER BY id
                           """
    course_exercises = db.session.execute(text(course_exercises_sql), {"course_id": course_id, "student_id": student_id}).fetchall()
    exercise_submissions_sql = """
                               SELECT
                               exercise_id,
                               correct
                               FROM exercise_answers
                               WHERE exercise_answers.course_id = :course_id AND COALESCE(exercise_answers.student_id = :student_id)
                               """
    exercise_submissions = db.session.execute(text(exercise_submissions_sql), {"course_id": course_id, "student_id": student_id}).fetchall()
    submissions_dict = {}
    for submission in exercise_submissions:
        submissions_dict[submission[0]] = submission[1]
    return render_template("/exercises_materials.html", course=course, exercises=course_exercises, submissions=submissions_dict, materials=materials)

@app.route("/do_exercise", methods=["POST", "GET"])
def do_exercise():
    """Page for submitting answers to exercises, and inserting into the database."""
    course_id = request.args["course_id"]
    if not data.permission_check(session, "student") \
    or not data.student_in_course(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    course = db.session.execute(text("SELECT id, name FROM courses WHERE id = :course_id"), {"course_id": course_id}).fetchone()
    exercise_id = request.args["exercise_id"]
    exercise_num = request.args["exercise_num"]
    exercise_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id AND id = :id"
    exercise = db.session.execute(text(exercise_sql), {"course_id": course_id, "id": exercise_id}).fetchone()
    exercise_submission_sql = """
                               SELECT
                               answer,
                               correct
                               FROM exercise_answers
                               WHERE 
                                exercise_answers.course_id = :course_id 
                                AND COALESCE(exercise_answers.student_id = :student_id) 
                                AND exercise_id = :exercise_id
                               """
    exercise_submission = db.session.execute(text(exercise_submission_sql), {"course_id": course_id, "student_id": session["user_id"], "exercise_id": exercise_id}).fetchone()
    return render_template("/do_exercise.html", exercise=exercise, exercise_num=exercise_num, course=course, submission=exercise_submission)

@app.route("/submit_answer", methods=["POST", "GET"])
def submit_answer():
    """Check if there's already a submission for the exercise, then insert into the database."""
    course_id = request.form["course_id"]
    if not data.permission_check(session, "student") \
    or not data.student_in_course(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
    answer = request.form["answer"]
    student_id = session["user_id"]
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
        if len(request.form["answer"]) >= 50:
            status = True
    elif exercise_type == "multiple_choice":
        if answer == exercise[1]["correct_answer"]:
            status = True
        else:
            status = False
    db.session.execute(text(add_exercise_sql), {"answer": answer, "student_id": student_id, "course_id": course_id, "exercise_id": exercise_id, "correct": status})
    db.session.commit()
    return redirect(f"/do_exercise?course_id={course_id}&exercise_id={exercise_id}&exercise_num={exercise_num}&status={status}&show_answer={True}")

@app.route("/joincourse")
def joincourse():
    """Join a course and insert data accordingly to the database."""
    if not data.permission_check(session, "student"):
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
    """Leave a course and remove relevant data from the database."""
    course_id = request.args.get("id")
    if not data.permission_check(session, "student") \
    or not data.student_in_course(session, course_id):
        return render_template("error.html", error="Ei oikeutta nähdä tätä sivua")
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
