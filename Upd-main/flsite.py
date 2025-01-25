import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, jsonify
from FDataBase import FDataBase
from FDataBase_Files import save_file_to_db, create_db_File
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from functools import wraps
from datetime import datetime


import pygame
from PIL import Image
import base64

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

massages_list = []


############## Функции базы данных ###################


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db1.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()

    #################### Конец функций базы данных ################


'''
@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 0 and len(request.form['post']) > 0:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)
'''


def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.getrole() != role:
                flash("You do not have access to this page.", "warning")
                return redirect(url_for('profile'))
            return func(*args, **kwargs)

        return decorated_function

    return decorator


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


@app.route("/", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        role = request.form.get('role')
        group_name = request.form.get('group_id')  # Название группы студента (если поле пустое, вернется None)

        # Проверка обязательности group_id для студентов
        if role == "Студент" and not group_name:
            flash("Для студентов номер группы обязателен.", "error")
            return render_template("register.html", title="Регистрация")

        # Основная логика обработки данных студента
        photo = request.files.get('photo')
        photo_df = photo.read()
        if (len(request.form['name']) > 0 and len(request.form['email']) > 4
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']
                and len(request.form['surname']) > 4 and len(request.form['patronymic']) > 4
                and len(role) > 4 and role in ["Преподаватель", "Студент", "Студент_Преподаватель"]):

            hash = generate_password_hash(request.form['psw'])

            # Добавляем пользователя в таблицу users
            res = dbase.addUser(request.form['name'], request.form['surname'], request.form['patronymic'],
                                request.form['role'], request.form['email'], hash, photo_df)

            user = dbase.getUserByEmail(request.form['email'])
            if user:
                user_id = user[0]  # id пользователя в базе данных

                if role == "Студент":
                    # Проверка существования группы
                    group_id = dbase.getGroupIdByName(group_name)
                    if not group_id:
                        # Если группы нет, создаем её и получаем новый group_id
                        group_id = dbase.addGroup(group_name)

                    # Добавляем студента с group_id
                    res = dbase.addStudent(user_id, group_id)

                elif role == "Преподаватель":
                    res = dbase.addTeacher(user_id)

                elif role == "Студент_Преподаватель":
                    group_id = dbase.getGroupIdByName(group_name)
                    if not group_id:
                        group_id = dbase.addGroup(group_name)
                    res = dbase.addStudent(user_id, group_id)
                    res = dbase.addTeacher(user_id)

            else:
                flash("Пользователь не найден", "error")

            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", title="Регистрация")


@app.route('/projects')
@login_required
def view_projects():
    db = get_db()
    dbase = FDataBase(db)

    if current_user.getrole() == "Студент":
        menu = dbase.getstudentMenu()
    elif current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
    else:
        menu = dbase.getMenu()
        return redirect(url_for('index'))

    projects = dbase.getProjects()

    return render_template('projects.html', menu=menu, projects=projects)


@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
@role_required("Преподаватель")
def create_project():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form['projectName']
        description = request.form['projectDescription']
        group_id = request.form['groupId']
        student_ids = request.form.getlist('students')  # Получаем список студентов
        start_date = request.form['startDate']
        end_date = request.form['endDate']

        # Получаем идентификатор преподавателя
        teacher_id = dbase.getTeacherIDByUserID(current_user.get_id())  # Возвращает int
        if not teacher_id:
            flash("Ошибка: Преподаватель не найден", "error")
            return redirect(url_for('create_project'))

        # Добавляем проект
        res = dbase.addProject(name, description, teacher_id, group_id, student_ids, start_date, end_date)
        if res:
            flash("Проект успешно создан", "success")
            return redirect(url_for('view_projects'))
        else:
            flash("Ошибка при создании проекта", "error")

    # Передача данных о группах и студентах для выбора
    groups = dbase.getAllGroups()  # Метод для получения всех групп
    return render_template('create_project.html', menu=dbase.getteacherMenu(), groups=groups)


@app.route('/get_students/<int:group_id>')
@login_required
def get_students(group_id):
    db = get_db()
    dbase = FDataBase(db)

    # Получаем студентов по ID группы
    students = dbase.getStudentsByGroupId(group_id)
    if students is False:
        return jsonify({'error': 'Не удалось получить список студентов'}), 500

    # Преобразуем студентов в словари
    students_list = [dict(student) for student in students]
    return jsonify({'students': students_list})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/tasks/update/<int:project_id>')
@login_required
def view_tasks(project_id):
    db = get_db()
    dbase = FDataBase(db)

    # Получаем задачи для проекта
    tasks = dbase.getTasksByProjectId(project_id)  # Метод для получения задач
    project = dbase.getProjectById(project_id)  # Получаем информацию о проекте (если нужно)

    if current_user.getrole() == "Студент":
        menu = dbase.getstudentMenu()
    elif current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
    else:
        menu = dbase.getMenu()

    if not project:
        flash("Проект не найден.", "error")
        return redirect(url_for('view_projects'))

    return render_template('tasks.html', tasks=tasks, project=project, menu=menu)

@app.route('/tasks/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required("Преподаватель")
def create_task(project_id):
    db = get_db()
    dbase = FDataBase(db)

    project = dbase.getProjectById(project_id)
    if not project:
        flash("Проект не найден", "error")
        return redirect(url_for('view_projects'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        completed_at = request.form['completed_at']
        status = request.form['status']

        # Преобразование строковых дат в объекты datetime.date
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        except ValueError:
            flash("Неверный формат даты. Пожалуйста, используйте формат 'ГГГГ-ММ-ДД'.", "error")
            return redirect(url_for('create_task', project_id=project_id))

        completed_at = datetime.strptime(completed_at, '%Y-%m-%d').date() if completed_at else None

        if dbase.addTask(project_id, title, description, deadline, completed_at, status):
            flash("Задача успешно добавлена", "success")
            return redirect(url_for('view_tasks', project_id=project_id))
        else:
            flash("Ошибка при добавлении задачи", "error")

    if current_user.getrole() == "Студент":
        menu = dbase.getstudentMenu()
    elif current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
    else:
        menu = dbase.getMenu()

    #if request.method == 'POST':
    #    title = request.form['title']
    #    description = request.form['description']
    #    deadline = request.form['deadline']  # Дата дедлайна из формы

        # Преобразуем строку даты в формат Python
    #    from datetime import datetime
    #    deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

    #    if dbase.addTask(project_id, title, description, deadline):
    #        flash("Задача успешно добавлена", "success")
    #        return redirect(url_for('view_tasks', project_id=project_id))
    #    else:
    #        flash("Ошибка при добавлении задачи", "error")

    return render_template('create_task.html', project=project, menu=menu)

from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
@role_required("Преподаватель")
def edit_task(task_id):
    db = get_db()
    dbase = FDataBase(db)

    task = dbase.getTaskById(task_id)
    if not task:
        flash("Задача не найдена", "error")
        return redirect(url_for('view_tasks'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        completed_at = request.form['completed_at']
        status = request.form['status']

        # Преобразование строковых дат в объекты datetime.date
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            completed_at_date = datetime.strptime(completed_at, '%Y-%m-%d').date() if completed_at else None
        except ValueError:
            flash("Неверный формат даты. Пожалуйста, используйте формат 'ГГГГ-ММ-ДД'.", "error")
            return redirect(url_for('edit_task', task_id=task_id))

        if dbase.updateTask(task_id, title, description, deadline_date, completed_at_date, status):
            flash("Задача успешно обновлена", "success")
            return redirect(url_for('view_tasks', project_id=task['project_id']))
        else:
            flash("Ошибка при обновлении задачи", "error")

    return render_template('edit_task.html', task=task)

@app.route('/events', methods=['GET'])
@login_required
def events():
    db = get_db()
    dbase = FDataBase(db)

    if current_user.getrole() == "Студент":
        menu = dbase.getstudentMenu()
    elif current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
        events = dbase.getAllEvents()
    else:
        menu = dbase.getMenu()
        events = []

    return render_template('events.html', menu=menu, events=events)


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
@role_required("Преподаватель")
def add_event():
    db = get_db()
    dbase = FDataBase(db)

    if current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
    else:
        return redirect(url_for('index'))  # Ограничиваем доступ

    if request.method == 'POST':
        name = request.form.get('eventTitle')
        description = request.form.get('eventDescription')
        start_date = request.form.get('eventStartDate')
        link = request.form.get('eventLink')
        project_ids = request.form.getlist('projects')  # Получаем список выбранных проектов

        if name and link and project_ids:
            success = dbase.addEvent(name, description, start_date, link, project_ids)
            if success:
                flash("Мероприятие успешно добавлено!", "success")
            else:
                flash("Ошибка при добавлении мероприятия.", "error")
        else:
            flash("Заполните все поля!", "error")

        return redirect(url_for('events'))

    # Получение списка проектов преподавателя
    projects = dbase.getTeacherProjects(current_user.get_id())
    return render_template('add_event.html', projects=projects, menu=menu)


@app.route('/profile')
# @login_required
def profile():
    # Проверка на авторизацию
    is_authenticated = current_user.is_authenticated

    # Получение данных о пользователе
    if is_authenticated:
        FIO = [current_user.getSurName(), current_user.getName(), current_user.getPatronymic()]
        img = current_user.getavatar()
        if isinstance(img, str):
            img = img.encode('utf-8')
        img1 = base64.b64encode(img).decode('utf-8')

        # Определяем меню в зависимости от роли
        if current_user.getrole() == "Студент":
            menu = dbase.getstudentMenu()
        elif current_user.getrole() == "Преподаватель":
            menu = dbase.getteacherMenu()
        else:
            menu = dbase.getMenu()  # Общее меню, если роль неизвестна

    else:
        menu = []  # Если пользователь не авторизован, меню пустое

    return render_template("profile.html", menu=menu, fio=FIO, image1=img1, user_authenticated=is_authenticated)


def table_exists(db, table_name):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


@app.route('/messages')
def messages():
    FIO = [current_user.getPatronymic(), current_user.getName(), current_user.getSurName()]
    img = current_user.getavatar()
    img1 = base64.b64encode(img).decode('utf-8')
    db = get_db()
    dbase = FDataBase(db)

    if current_user.getrole() == "Студент":
        menu = dbase.getstudentMenu()
    elif current_user.getrole() == "Преподаватель":
        menu = dbase.getteacherMenu()
    else:
        menu = dbase.getMenu()

    return render_template('messages.html', menu=menu, users=dbase.getUsersAnonce(),
                           fio=FIO, image1=img1)


@app.route('/send_message', methods=['POST'])
def send_message():
    db = get_db()
    dbase = FDataBase(db)
    data = request.form
    recipient_id = int(data['recipient'])
    message_text = data['message']

    print(f"Recipient ID: {recipient_id}, Message: {message_text}")  # Отладочное сообщение

    user = dbase.getUser(recipient_id)
    if not user:
        return jsonify({'success': False, 'error': 'Получатель не найден'})

    sender_id = UserLogin.get_id(current_user)
    if sender_id is None:
        return jsonify({'success': False, 'error': 'Текущий пользователь не найден'})

    success = dbase.addMessage(message_text, sender_id, recipient_id)
    if not success:
        return jsonify({'success': False, 'error': 'Ошибка при отправке сообщения'})

    return jsonify({'success': True})


@app.route('/get_messages', methods=['POST'])
def get_messages():
    db = get_db()
    dbase = FDataBase(db)
    data = request.get_json()  # Используйте request.get_json() для обработки JSON ввода
    recipient_id = int(data['recipient'])

    user = dbase.getUser(recipient_id)
    if not user:
        return jsonify({'success': False, 'error': 'Получатель не найден'})

    messages = dbase.getMessage(
        UserLogin.get_id(current_user))  # Предполагаем, что этот метод получает все сообщения для отправителя

    if not messages:
        return jsonify({'success': False, 'error': 'Сообщения не найдены'})

    # Конвертируем каждое сообщение в словарь
    messages_list = [{'message': msg['message'], 'receiver_id': msg['receiver_id']} for msg in messages]

    return jsonify({'success': True, 'messages': messages_list})


@app.route('/subjects')
def subjects():
    db = get_db()
    dbase = FDataBase(db)

    FIO = [current_user.getPatronymic(), current_user.getName(), current_user.getSurName()]
    img = current_user.getavatar()
    img1 = base64.b64encode(img).decode('utf-8')

    user_id = UserLogin.get_id(current_user)
    group_id = dbase.getGroupIDByUserID(user_id)
    disciplines_list = dbase.getLessons(group_id)

    if not disciplines_list:
        disciplines_list = []

    return render_template('subjects.html', disciplines=disciplines_list, menu=dbase.getMenu(), fio=FIO,
                           image1=img1)


@app.route("/user/<int:id_user>")
# @login_required
def showUser(id_user):
    db = get_db()
    dbase = FDataBase(db)
    user = dbase.getUser(id_user)
    FIO = [current_user.getPatronymic(), current_user.getName(), current_user.getSurName()]
    img = user['avatar']
    img1 = base64.b64encode(img).decode('utf-8')
    if not user:
        abort(404)
    return render_template('user.html', menu=dbase.getMenu(), user=user, fio=FIO, image1=img1)

@app.route('/research_projects')
def research_projects():
    db = get_db()
    dbase = FDataBase(db)
    projects = db.getResearchProjects()
    return render_template('research_projects.html', projects=projects)

@app.route('/add_nirs_result/<int:project_id>/<int:student_id>', methods=['POST', 'GET'])
@login_required
@role_required("Преподаватель")
def add_nirs_result(project_id, student_id):
    db = get_db()
    dbase = FDataBase(db)

    # Получаем информацию о проекте и студенте
    project = dbase.getProjectById(project_id)
    student = dbase.getStudentById(student_id)

    if not project or not student:
        flash("Проект или студент не найден.", "error")
        return redirect(url_for('view_projects'))

    if request.method == 'POST':
        # Получаем данные из формы
        result = request.form['result']
        comments = request.form['comments']
        date = datetime.now()

        # Добавляем результат НИРС в базу данных
        if dbase.addNirsResult(project_id, student_id, result, comments, date):
            flash("Результат НИРС успешно добавлен.", "success")
            return redirect(url_for('view_projects'))
        else:
            flash("Ошибка при добавлении результата НИРС.", "error")

    return render_template('add_nirs_result.html', project=project, student=student)

@app.route('/view_nirs_results/<int:project_id>', methods=['GET'])
@login_required
@role_required("Преподаватель")
def view_nirs_results(project_id):
    db = get_db()
    dbase = FDataBase(db)

    project = dbase.getProjectById(project_id)
    if not project:
        flash("Проект не найден.", "error")
        return redirect(url_for('view_projects'))

    # Получаем все результаты НИРС для студентов проекта
    results = dbase.getNirsResultsByProjectId(project_id)

    return render_template('view_nirs_results.html', project=project, results=results)

@app.route('/edit_nirs_result/<int:result_id>', methods=['POST', 'GET'])
@login_required
@role_required("Преподаватель")
def edit_nirs_result(result_id):
    db = get_db()
    dbase = FDataBase(db)

    # Получаем результат НИРС по ID
    result = dbase.getNirsResultById(result_id)
    if not result:
        flash("Результат НИРС не найден.", "error")
        return redirect(url_for('view_nirs_results', project_id=result['project_id']))

    if request.method == 'POST':
        # Получаем данные из формы
        result_value = request.form['result']
        comments = request.form['comments']

        # Обновляем результат НИРС в базе данных
        if dbase.updateNirsResult(result_id, result_value, comments):
            flash("Результат НИРС успешно обновлен.", "success")
            return redirect(url_for('view_nirs_results', project_id=result['project_id']))
        else:
            flash("Ошибка при обновлении результата НИРС.", "error")

    return render_template('edit_nirs_result.html', result=result)

@app.route('/delete_nirs_result/<int:result_id>', methods=['GET'])
@login_required
@role_required("Преподаватель")
def delete_nirs_result(result_id):
    db = get_db()
    dbase = FDataBase(db)

    # Получаем результат НИРС по ID
    result = dbase.getNirsResultById(result_id)
    if not result:
        flash("Результат НИРС не найден.", "error")
        return redirect(url_for('view_nirs_results', project_id=result['project_id']))

    # Удаляем результат НИРС
    if dbase.deleteNirsResult(result_id):
        flash("Результат НИРС успешно удален.", "success")
    else:
        flash("Ошибка при удалении результата НИРС.", "error")

    return redirect(url_for('view_nirs_results', project_id=result['project_id']))

@app.route('/view_nirs_results_student/<int:project_id>', methods=['GET'])
@login_required
def view_nirs_results_student(project_id):
    db = get_db()
    dbase = FDataBase(db)

    project = dbase.getProjectById(project_id)
    if not project:
        flash("Проект не найден.", "error")
        return redirect(url_for('view_projects'))

    # Получаем результаты НИРС для текущего студента
    results = dbase.getNirsResultsByStudentIdAndProjectId(current_user.get_id(), project_id)

    return render_template('view_nirs_results_student.html', project=project, results=results)

if __name__ == "__main__":
    app.run(debug=True)
    #create_db()
