DROP TABLE IF EXISTS tutor CASCADE;
DROP TABLE IF EXISTS student CASCADE;
DROP TABLE IF EXISTS lesson CASCADE;
DROP TABLE IF EXISTS notification CASCADE;
DROP TABLE IF EXISTS chat CASCADE;


CREATE TABLE IF NOT EXISTS tutor
(
    tutor_id SERIAL PRIMARY KEY,
    chat_id integer NOT NULL,
    full_name VARCHAR(50),
    phone_number VARCHAR(20),
    added_at timestamp
);

CREATE TABLE IF NOT EXISTS student
(
    student_id SERIAL PRIMARY KEY,
    unique_id VARCHAR(50) NOT NULL,
    full_name VARCHAR(50),
    tutor_id INTEGER,
    chat_id integer,
    phone_number VARCHAR(20),
	payment_amount FLOAT,
	payment_currency VARCHAR(10),
    added_at timestamp,
    CONSTRAINT fk_student_tutor
      FOREIGN KEY(tutor_id) 
        REFERENCES tutor(tutor_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lesson
(
    lesson_id SERIAL PRIMARY KEY,
    tutor_id INTEGER,
    student_id integer,
	lesson_datetime TIMESTAMP,
    description VARCHAR(100),
    added_at timestamp,
    CONSTRAINT fk_lesson_tutor
      FOREIGN KEY(tutor_id) 
        REFERENCES tutor(tutor_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_lesson_student
      FOREIGN KEY(student_id) 
        REFERENCES student(student_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notification
(
    notification_id SERIAL PRIMARY KEY,
    tutor_id INTEGER,
    student_id integer,
    lesson_id integer,
	notification_datetime TIMESTAMP,
    description VARCHAR(100),
    tg_message VARCHAR(200),
    added_at timestamp,
    CONSTRAINT fk_notification_tutor
      FOREIGN KEY(tutor_id) 
        REFERENCES tutor(tutor_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notification_student
      FOREIGN KEY(student_id) 
        REFERENCES student(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notification_lesson
      FOREIGN KEY(lesson_id) 
        REFERENCES lesson(lesson_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat
(
	chat_id SERIAL PRIMARY KEY,
	tg_chat_id INTEGER,
	chat_state VARCHAR(100),
	added_at timestamp
);