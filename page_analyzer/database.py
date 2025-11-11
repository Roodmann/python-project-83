
import psycopg2



def get_db(app):
    """соединение с базой данных"""
    
    conn = psycopg2.connect(app.config["DATABASE_URL"])
    return conn


def check_url_existence(app, url_name):
    """Проверяет наличие URL с заданным именем в базе данных"""
    
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT id FROM urls WHERE name = %s", (url_name,))
    result = cur.fetchone()

    if result:
        url_id = result[0] # Идентификатор URL, если он существует в базе данных
    else:
        url_id = None # Значение None, если URL с таким именем не найден

    conn.close()
    return url_id


def add_urls(app, url_name):
    """Добавляет новый URL с указанным именем в базу данных и возвращает его ID"""
    
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url_name,))
    url_id = cur.fetchone()[0]

    conn.commit()
    conn.close()
    return url_id


def get_one_url(app, url_id):
    """Получает информацию о URL по его ID из базы данных"""
    
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
    row = cur.fetchone()
    return row


def get_checks_for_url(app, url_id):
    """Получает все проверки, связанные с указанным URL по его ID"""
    
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT * FROM checks WHERE url_id = %s", (url_id,))
    checks = cur.fetchall()
    conn.close()
    return checks



def get_all_urls(app):
    """Получает список всех URL-ов из базы данных, отсортированный по убыванию ID"""
    
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM urls ORDER BY id DESC")
    urls = cur.fetchall()
    return urls


def create_check_entry(app, url_id, status_code, created_at):
    """Создает новую запись проверки в базе данных с указанными параметрами"""
    
    conn = get_db(app)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO checks (url_id, status_code, created_at) VALUES (%s, %s, %s)",
    (url_id, status_code, created_at) )
    conn.commit()
    conn.close()


def save_check_result(app, url, check_result):
    """Сохраняет результаты проверки в базу данных"""

    conn = get_db(app)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO checks (url, h1, title, description)
        VALUES (%s, %s, %s, %s)
    ''', (url, check_result['h1'], check_result['title'], check_result['description']))
    conn.commit()
