CREATE TABLE IF NOT EXISTS mainmenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    url text NOT NULL
);

-- Таблица для хранения меню студента
CREATE TABLE IF NOT EXISTS studentmenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    url text NOT NULL
);

-- Таблица для хранения меню преподавателя
CREATE TABLE IF NOT EXISTS teachermenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    url text NOT NULL
);

-- Таблица для хранения информации о пользователях
CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) not null,
    surname VARCHAR(255) not null,
    patronymic VARCHAR(255) not null,
    role VARCHAR(255) not null,
    email VARCHAR(255) NOT NULL,
    psw VARCHAR(255) NOT NULL,
    avatar BLOB DEFAULT NULL
);

-- Таблица для хранения информации о студентах
CREATE TABLE IF NOT EXISTS student (
    student_id integer PRIMARY KEY AUTOINCREMENT,
    user_id integer,
    group_id integer,
    project_id integer,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Таблица для преподавателей
CREATE TABLE IF NOT EXISTS teacher (
    teacher_id integer PRIMARY KEY AUTOINCREMENT,
    user_id integer,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Таблица для хранения групп студентов
CREATE TABLE IF NOT EXISTS groups (
    id integer PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(255) NOT NULL
);

-- Таблица для хранения проектов
CREATE TABLE IF NOT EXISTS project (
    id integer PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description text,
    teacher_id integer,
    group_id integer,
    start_date DATE,
    end_date DATE,
    event_id integer,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
    FOREIGN KEY (event_id) REFERENCES event(id)
);

-- Таблица для задач в проекте
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT,
    description TEXT,
    completed_at DATE,
    status TEXT DEFAULT 'не завершена',
    FOREIGN KEY (project_id) REFERENCES project(id)
);

-- Таблица для мероприятий в проекте
CREATE TABLE IF NOT EXISTS event (
    id integer PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    link TEXT
);

-- Таблица для отчетов по задачам
CREATE TABLE IF NOT EXISTS report (
    report_id integer PRIMARY KEY AUTOINCREMENT,
    task_id integer,
    description TEXT,
    type_of_result VARCHAR(255) NOT NULL,
    FOREIGN KEY (task_id) REFERENCES task(task_id)
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
