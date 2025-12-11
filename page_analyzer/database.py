
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


@contextmanager
def get_db(app):
    """соединение с базой данных"""
    print("Попытка подключения к базе по URL:", app.config["DATABASE_URL"])
    conn = psycopg2.connect(
        app.config["DATABASE_URL"],
        connect_timeout=10 # Тайм-аут для попытки установить соединение с базой данных
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = %s", (10000,)) # Устанавливаем тайм-аут для выполнения каждого SQL-запроса в рамках текущей сессии.
        yield conn
    finally:
        conn.close()



def check_url_existence(app, url_name):
    """Проверяет наличие URL с заданным именем в базе данных"""
    
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url_name,))
            result = cur.fetchone()

    if result:
        url_id = result['id'] # Идентификатор URL, если он существует в базе данных
    else:
        url_id = None # Значение None, если URL с таким именем не найден
    
    return url_id


def add_urls(app, url_name):
    """Добавляет новый URL с указанным именем в базу данных и возвращает его ID"""
    
    with get_db(app) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url_name,))
            url_id = cur.fetchone()[0]
        conn.commit()

    return url_id


def get_one_url(app, url_id):
    """Получает информацию о URL по его ID из базы данных"""
    
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
            row = cur.fetchone()

    return row


def get_checks_for_url(app, url_id):
    """Получает все проверки, связанные с указанным URL по его ID"""
    
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
            checks = cur.fetchall()

    return checks



def get_all_urls(app):
    """Получает список всех URL-ов из базы данных, отсортированный по убыванию ID"""
    
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM urls ORDER BY id DESC")
            urls = cur.fetchall()

    return urls


def create_check_entry(app, url_id, status_code, created_at, h1=None, title=None, description=None):
    """Создает новую запись проверки в базе данных с указанными параметрами"""
    
    with get_db(app) as conn:
        with conn.cursor() as cur: 
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s)",
                (url_id, status_code, h1, title, description, created_at))
        conn.commit()

def save_check_result(app, url, check_result):
    """Сохраняет результаты проверки в базу данных"""

    with get_db(app) as conn:
        with conn.cursor() as cur: 
            cur.execute('''
                INSERT INTO url_checks (url, h1, title, description)
                VALUES (%s, %s, %s, %s)
                ''', (url, check_result['h1'], check_result['title'], 
                    check_result['description'])
                )
        conn.commit()
