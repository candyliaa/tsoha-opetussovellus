"""File that contains helper functions for routes.py."""
from sqlalchemy.sql import text
from db import db

# Permission check functions
def permission_check(session: dict, role = None):
    """Check if user has the correct role to access webpage."""
    if "role" not in session.keys() or session["role"] != role:
        return False
    return True

def student_in_course(session: dict, course_id: str):
    """Check if a student is enrolled in a course before they can view it."""
    student_id = session["user_id"]
    student_in_course_check_sql = """
                                  SELECT student_id
                                  FROM course_participants
                                  WHERE student_id = :student_id AND course_id = :course_id
                                  """
    if db.session.execute(text(student_in_course_check_sql),
    {"student_id": student_id, "course_id": course_id}).fetchone() is None:
        return False
    return True

def correct_teacher(session: dict, course_id: str):
    """Check if the user is the teacher of the class they're trying to modify."""
    teacher_id = session["user_id"]
    correct_teacher_check_sql = """
                                SELECT teacher_id
                                FROM courses
                                WHERE courses.id = :course_id
                                """
    if db.session.execute(text(correct_teacher_check_sql),
    {"course_id": course_id}).fetchone()[0] != teacher_id:
        return False
    return True

# Login and account creation functions
def login_fetch_user(account_type: str, username: str):
    """Fetch user data from database."""
    if account_type == "teacher":
        sql = "SELECT id, password FROM teacher_accounts WHERE username = :username"
    else:
        sql = "SELECT id FROM student_accounts WHERE username = :username"
    return db.session.execute(text(sql), {"username": username}).fetchone()

def create_account(account_type: str, username: str, hash_value: str):
    """Create an account and insert data into the database."""
    if account_type == "teacher":
        sql = "INSERT INTO teacher_accounts (username, password) VALUES (:username, :password) RETURNING id"
    else:
        sql = "INSERT INTO student_accounts (username, password) VALUES (:username, :password) RETURNING id"
    return_value = db.session.execute(text(sql), {"username": username, "password": hash_value}).fetchone()
    db.session.commit()
    return return_value[0]

# Helper functions for the SQL queries for teacher actions
def coursetools_courses():
    """Fetch all courses for the coursetools page."""
    courses_sql = """
                  SELECT 
                    courses.id,
                    name,
                    credits,
                    p.student_count,
                    teacher_accounts.username
                  FROM courses
                  LEFT JOIN teacher_accounts ON courses.teacher_id = teacher_accounts.id
                  LEFT JOIN (
                    SELECT course_id, COUNT(student_id) AS student_count
                    FROM course_participants
                    GROUP BY course_id
                    ) 
                  p ON courses.id = p.course_id
                  """
    return db.session.execute(text(courses_sql)).fetchall()

def create_course(course_name: str, course_credits: int, session: dict):
    """Check if course exists and insert course data into the database upon creation."""
    check_sql = "SELECT name FROM courses WHERE name = :course_name"
    if db.session.execute(text(check_sql), {"course_name": course_name}).fetchone() is not None:
        return False
    sql = "INSERT INTO courses (name, credits, teacher_id) VALUES (:course_name, :credits, :teacher_id)"
    db.session.execute(text(sql), {"course_name": course_name, "credits": course_credits, "teacher_id": session["user_id"]})
    db.session.commit()

def delete_course(course_id: int):
    """Delete course from database and return the name of deleted course."""
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(course_name_sql), {"course_id":course_id}).fetchone()[0]
    if course_name is None:
        return False
    delete_sql = "DELETE FROM courses WHERE id =:course_id"
    db.session.execute(text(delete_sql), {"course_id": course_id})
    db.session.commit()
    return course_name

def modify_course_data(course_id: int):
    """Return relevant data the modify_course route uses."""
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(text(materials_sql), {"course_id": course_id}).fetchall()

    course_exercises_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id ORDER BY id"                     
    course_exercises = db.session.execute(text(course_exercises_sql), {"course_id": course_id}).fetchall()

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
    data_dict = {
        "course": course,
        "materials": materials,
        "course_exercises": course_exercises,
        "course_participants": course_participants,
        "current_exercise_submissions_sql": current_exercise_submissions_sql
    }

    return data_dict

def delete_exercise(course_id: int, exercise_id: int):
    """Remove exercise from database upon deletion."""
    fetch_exercise_sql = """
                         SELECT id
                         FROM exercises
                         WHERE course_id = :course_id AND id := exercise_id
                         """
    if db.session.execute( \
        text(fetch_exercise_sql), \
        {"course_id": course_id, "exercise_id": exericse_id} \
        ).fetchone()[0] is None:
            return False

    delete_exercise_sql = """
                        DELETE FROM exercises
                        WHERE course_id = :course_id AND id = :exercise_id
                        """
    db.session.execute(text(delete_exercise_sql), {"course_id": course_id, "exercise_id": exercise_id})
    db.session.commit()
