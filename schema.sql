DROP DATABASE IF EXISTS tsoha;

CREATE DATABASE tsoha;

\c tsoha

CREATE TABLE student_accounts (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);

CREATE TABLE teacher_accounts (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);

CREATE TABLE courses (id SERIAL PRIMARY KEY, name TEXT UNIQUE, credits INTEGER);

CREATE TABLE course_teachers (course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, teacher_id INTEGER REFERENCES teacher_accounts(id));

CREATE TABLE course_participants (course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, student_id INTEGER REFERENCES student_accounts(id));

CREATE TABLE exercises (id SERIAL PRIMARY KEY, question TEXT, choices JSON, course_id INTEGER REFERENCES courses(id));

CREATE TABLE text_materials (id SERIAL PRIMARY KEY, title TEXT, body TEXT, course_id INTEGER REFERENCES courses(id));
