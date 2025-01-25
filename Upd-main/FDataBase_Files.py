import sqlite3

def create_db_File():
    # Подключение к базе данных (если она существует, она будет открыта, если нет - создастся новая)
    conn = sqlite3.connect('files.db')
    c = conn.cursor()

    # Создание таблицы для хранения файлов
    c.execute('''CREATE TABLE IF NOT EXISTS files
                (id INTEGER PRIMARY KEY, filename TEXT, file_content BLOB)''')

    conn.commit()
    conn.close()

def save_file_to_db(filename):
    with open(filename, 'rb') as file:
        file_content = file.read()

    conn = sqlite3.connect('files.db')
    c = conn.cursor()

    # Вставка данных в таблицу
    c.execute("INSERT INTO files (filename, file_content) VALUES (?, ?)", (filename, file_content))

    conn.commit()
    conn.close()