import sqlite3
import time
import math
import re
from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД (getMenu)")
        return []

    def getstudentMenu(self):
        sql = '''SELECT * FROM studentmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД (getstudentMenu)")
        return []

    def getteacherMenu(self):
        sql = '''SELECT * FROM teachermenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД (getteacherMenu)")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False

            base = url_for('static', filename='images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД (addPost) " + str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД (getPost) " + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД (getPostsAnonce) " + str(e))

        return []

    def addUser(self, name, surname, patronymic, role, email, psw, photo):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)",
                               (name, surname, patronymic, role, email, psw, photo))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД (addUser) " + str(e))
            return False
        return True

    def addStudent(self, user_id, group_id):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM student WHERE user_id = ?", (user_id,))
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Студент с таким user_id уже существует")
                return False

            # Вставляем в таблицу student
            self.__cur.execute("INSERT INTO student (user_id, group_id) VALUES(?, ?)", (user_id, group_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления студента в БД (addStudent) " + str(e))
            return False
        return True

    def addTeacher(self, user_id):
        try:
            self.__cur.execute(
                "INSERT INTO teacher (user_id) VALUES (?)",
                (user_id,)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка добавления преподавателя в БД (addTeacher) " + str(e))
            return False

    def addSuperUser(self, name, surname, patronymic, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM superusers WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO superusers VALUES(NULL,?, ?, ?, ?, ?, ?)",
                               (name, surname, patronymic, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД (addSuperUser) " + str(e))
            return False
        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (getUser) " + str(e))

        return False

    def getUserbyid(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (getUserdyid) " + str(e))

        return False

    def getUsersAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, name, surname FROM users ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД (getUsersAnonce) " + str(e))

        return []

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (getUserByEmail) " + str(e))

        return False

    def getGroupIDByUserID(self, user_id):
        try:
            self.__cur.execute(f"SELECT group_id FROM student WHERE user_id = '{user_id}'")
            res = self.__cur.fetchone()
            if not res:
                print("Группа не найдена")
                return False

            val = int(res['group_id'])
            return val
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (getGroupIDByUserID) " + str(e))
            return False

    def getGroupIdByName(self, group_name):
        """Получает id группы по её названию, если такая группа существует"""
        self.__cur.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
        result = self.__cur.fetchone()
        return result[0] if result else None

    def addGroup(self, group_name):
        """Создает новую группу и возвращает её id"""
        self.__cur.execute("INSERT INTO groups (group_name) VALUES (?)", (group_name,))
        self.__db.commit()
        return self.__cur.lastrowid

    def getAllGroups(self):
        self.__cur.execute("SELECT id, group_name FROM groups")
        return [{'id': row[0], 'name': row[1]} for row in self.__cur.fetchall()]

    def getLessons(self, group_id):
        try:
            self.__cur.execute("SELECT subject FROM lessons WHERE group_id = ?", (group_id,))
            res = self.__cur.fetchall()
            if not res:
                print("Дисциплины не найдены")
                return False

            print("Полученные дисциплины:", res)
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (getLessons) " + str(e))
            return False

    def addMessage(self, message, current_user, receiver_id):
        try:
            self.__cur.execute("INSERT INTO messages (message, sender_id, receiver_id) VALUES (?, ?, ?)",
                               (message, current_user, receiver_id))
            self.__db.commit()
            print("Сообщение успешно добавлено")
            return True

        except sqlite3.Error as e:
            print("Ошибка добавления сообщения в БД (addMessage) " + str(e))
            return False

    def getMessage(self, sender_id):
        try:
            self.__cur.execute(f"SELECT message, receiver_id FROM messages WHERE sender_id = ?", sender_id)
            res = self.__cur.fetchall()
            if not res:
                print("Сообщения не найдены")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения сообщений из БД (addMessage) " + str(e))
            return False

    def getTasksByProjectId(self, project_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, description, end_date, completed_at, status FROM tasks WHERE project_id = ?", (project_id,))
        tasks = cursor.fetchall()
        return tasks


    def addTask(self, project_id, title, description, deadline, completed_at=None, status='не завершена'):
        cursor = self.__db.cursor()
        cursor.execute(
            "INSERT INTO tasks (project_id, name, description, end_date, completed_at, status) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, title, description, deadline, completed_at, status)
        )
        self.__db.commit()
        return cursor.rowcount == 1


    def addProject(self, name, description, teacher_id, group_id, student_ids, start_date, end_date):
        try:
            # Добавляем проект и получаем его ID
            self.__cur.execute(
                "INSERT INTO project (name, description, teacher_id, group_id, start_date, end_date) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, description, teacher_id, group_id, start_date, end_date)
            )
            project_id = self.__cur.lastrowid  # Получаем ID созданного проекта

            # Обновляем таблицу студентов, добавляя project_id
            for student_id in student_ids:
                self.__cur.execute(
                    "UPDATE student SET project_id = ? WHERE student_id = ?",
                    (project_id, student_id)
                )

            self.__db.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении проекта: {e}")
            self.__db.rollback()
            return False

    def getProjects(self):
        try:
            self.__cur.execute("SELECT * FROM project")
            result = self.__cur.fetchall()
            return [dict(row) for row in result]  # Приводим строки к словарям
        except Exception as e:
            print(f"Ошибка при получении проектов: {e}")
            return []

    def getProjectById(self, project_id):
        try:
            self.__cur.execute("SELECT * FROM project WHERE id = ?", (project_id,))
            result = self.__cur.fetchone()
            return dict(result) if result else None  # Приводим строку к словарю, если запись найдена
        except Exception as e:
            print(f"Ошибка при получении проекта по id: {e}")
            return None

    def getTeacherProjects(self, teacher_id):
        try:
            query = """
                SELECT id, name, description, start_date, end_date 
                FROM project 
                WHERE teacher_id = ?
            """
            result = self.__cur.execute(query, (teacher_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Ошибка при получении проектов преподавателя: {e}")
            return []

    def getTasksByProjectId(self, project_id):
        try:
            self.__cur.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,))
            return self.__cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении задач: {e}")
            return []
    
    def updateTask(self, task_id, title, description, deadline, completed_at, status):
        try:
            self.cur.execute("UPDATE tasks SET title=?, description=?, deadline=?, completed_at=?, status=? WHERE id=?", 
                             (title, description, deadline, completed_at, status, task_id))
            self.con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка обновления задачи в базе данных: {e}")
            return False


    # Метод для получения ID преподавателя по user_id
    def getTeacherIDByUserID(self, user_id):
        self.__cur.execute("SELECT teacher_id FROM teacher WHERE user_id = ?", (user_id,))
        result = self.__cur.fetchone()
        return result[0] if result else None

    # Метод для получения всех студентов
    def getAllStudents(self):
        self.__cur.execute("SELECT student_id, name FROM student JOIN users ON student.user_id = users.id")
        return [{'id': row[0], 'name': row[1]} for row in self.__cur.fetchall()]

    # Метод для получения всех групп
    def getAllGroups(self):
        try:
            self.__cur.execute("SELECT id, group_name FROM groups")
            return [{'id': row[0], 'name': row[1]} for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print("Ошибка получения групп:", e)
            return []

    def getStudentsByGroupId(self, group_id):
        try:
            self.__cur.execute(
                "SELECT student_id, user_id, group_id, project_id FROM student WHERE group_id = ?", (group_id,)
            )
            students = self.__cur.fetchall()
            return students if students else []
        except Exception as e:
            print(f"Ошибка при получении студентов: {e}")
            return False

    def addEvent(self, name, description, start_date, link, project_ids):
        try:
            # Добавляем мероприятие в таблицу events
            self.__cur.execute(
                """
                INSERT INTO event (name, description, start_date, link) 
                VALUES (?, ?, ?, ?)
                """,
                (name, description, start_date, link)
            )
            event_id = self.__cur.lastrowid  # Получаем ID только что добавленного мероприятия

            # Обновляем поле event_id для выбранных проектов
            for project_id in project_ids:
                self.__cur.execute(
                    """
                    UPDATE project 
                    SET event_id = ? 
                    WHERE id = ?
                    """,
                    (event_id, project_id)
                )

            self.__db.commit()  # Фиксируем изменения в базе данных
            return True
        except Exception as e:
            print(f"Ошибка при добавлении мероприятия: {e}")
            self.__db.rollback()  # Откат в случае ошибки
            return False

    def getAllEvents(self):
        try:
            return self.__cur.execute("SELECT * FROM event").fetchall()
        except Exception as e:
            print(f"Ошибка при получении мероприятий: {e}")
            return []
        
    def addResearchProject(self, name, description, teacher_id, start_date, end_date):
        try:
            self.__cur.execute(
                "INSERT INTO research_projects (name, description, teacher_id, start_date, end_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, description, teacher_id, start_date, end_date)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления НИРС проекта: {e}")
            return False

    def getResearchProjects(self):
        try:
            self.__cur.execute("SELECT * FROM research_projects")
            result = self.__cur.fetchall()
            return [dict(row) for row in result]
        except sqlite3.Error as e:
            print(f"Ошибка получения НИРС проектов: {e}")
            return []

    def getResearchProjectById(self, project_id):
        try:
            self.__cur.execute("SELECT * FROM research_projects WHERE id = ?", (project_id,))
            result = self.__cur.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения НИРС проекта по id: {e}")
            return None

    def addResearchTask(self, project_id, title, description, deadline):
        try:
            self.__cur.execute(
                "INSERT INTO research_tasks (project_id, title, description, deadline) "
                "VALUES (?, ?, ?, ?)",
                (project_id, title, description, deadline)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления задачи НИРС: {e}")
            return False

    def getResearchTasksByProjectId(self, project_id):
        try:
            self.__cur.execute("SELECT * FROM research_tasks WHERE project_id = ?", (project_id,))
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения задач НИРС для проекта: {e}")
            return []

    def addResearchReport(self, project_id, student_id, report_text, submission_date, grade):
        try:
            self.__cur.execute(
                "INSERT INTO research_reports (project_id, student_id, report_text, submission_date, grade) "
                "VALUES (?, ?, ?, ?, ?)",
                (project_id, student_id, report_text, submission_date, grade)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления отчета НИРС: {e}")
            return False

    def getResearchReportsByProjectId(self, project_id):
        try:
            self.__cur.execute("SELECT * FROM research_reports WHERE project_id = ?", (project_id,))
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения отчетов НИРС для проекта: {e}")
            return []
