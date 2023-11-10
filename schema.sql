CREATE DATABASE tsoha;

\c tsoha

CREATE TABLE student_accounts (id SERIAL PRIMARY KEY, name TEXT, password TEXT)

CREATE TABLE teacher_accounts (id SERIAL PRIMARY KEY, name TEXT, password TEXT)

CREATE TABLE courses (id SERIAL PRIMARY KEY, name TEXT, credits INTEGER)

CREATE TABLE course_teachers (course_id REFERENCES courses(id), teacher_id REFERENCES teacher_accounts(id))

CREATE TABLE course_participants (course_id REFERENCES courses(id), student_id REFERENCES student_accounts(id))

CREATE TABLE exercises (id SERIAL PRIMARY KEY, type TEXT)
