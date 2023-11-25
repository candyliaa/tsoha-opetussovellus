"""File that contains helper functions for routes.py."""
from sqlalchemy.sql import text
from db import db

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

def create_account(account_type: str, username: str, hash_value: str):
    """Create an account and insert data into the database."""
    if account_type == "teacher":
        sql = "INSERT INTO teacher_accounts (username, password) VALUES (:username, :password) RETURNING id"
    else:
        sql = "INSERT INTO student_accounts (username, password) VALUES (:username, :password) RETURNING id"
    return_value = db.session.execute(text(sql), {"username": username, "password": hash_value}).fetchone()
    db.session.commit()
    return return_value[0]
