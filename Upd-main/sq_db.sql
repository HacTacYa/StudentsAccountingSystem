CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
surname text NOT NULL,
patronymic text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
surname text NOT NULL,
patronymic text NOT NULL,
user_id INT,
group_id JSON,
time integer NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS teachers (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
surname text NOT NULL,
patronymic text NOT NULL,
user_id INT,
group_id JSON,
time integer NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS superusers (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
surname text NOT NULL,
patronymic text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS studentmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);



CREATE TABLE IF NOT EXISTS groups (
    id integer PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    lesson_id JSON
);



CREATE TABLE IF NOT EXISTS lessons (
    id integer PRIMARY KEY AUTOINCREMENT,
    subject VARCHAR(100) NOT NULL,
    teacher_id INT,
    group_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

CREATE TABLE research_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    teacher_id INTEGER,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);

CREATE TABLE research_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'не завершена',
    deadline DATE,
    completed_at DATE,
    FOREIGN KEY (project_id) REFERENCES research_projects(id)
);

CREATE TABLE research_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    student_id INTEGER,
    report_text TEXT,
    submission_date DATE,
    grade INTEGER,
    FOREIGN KEY (project_id) REFERENCES research_projects(id),
    FOREIGN KEY (student_id) REFERENCES student(user_id)
);
