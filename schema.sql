DROP DATABASE IF EXISTS tsoha;

CREATE DATABASE tsoha;

\c tsoha

CREATE TABLE student_accounts (id SERIAL PRIMARY KEY, username TEXT, password TEXT);

CREATE TABLE teacher_accounts (id SERIAL PRIMARY KEY, username TEXT, password TEXT);

CREATE TABLE courses (id SERIAL PRIMARY KEY, username TEXT, credits INTEGER);

CREATE TABLE course_teachers (course_id INTEGER REFERENCES courses(id), teacher_id INTEGER REFERENCES teacher_accounts(id));

CREATE TABLE course_participants (course_id INTEGER REFERENCES courses(id), student_id INTEGER REFERENCES student_accounts(id));

CREATE TABLE exercises (id SERIAL PRIMARY KEY, type TEXT);
