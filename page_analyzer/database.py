
import psycopg2


# пытаемся подключиться к базе данных
def get_db(app):
    conn = psycopg2.connect(app.config["DATABASE_URL"])
    return conn

#except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    #print('Can`t establish connection to database')

    # У строки следующий формат: {provider}://{user}:{password}@{host}:{port}/{db}
# export DATABASE_URL=postgresql://janedoe:mypassword@localhost:5432/mydb

#conn = get_db(app)

def check_url_existence(app, url_name):
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT id FROM urls WHERE name = %s", (url_name,))
    result = cur.fetchone()

    if result:
        url_id = result[0]
    else:
        url_id = None

    conn.close()
    return url_id


def add_urls(app, url_name):
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url_name,))
    url_id = cur.fetchone()[0]

    conn.commit()
    conn.close()
    return url_id


def get_one_url(app, url_id):
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
    row = cur.fetchone()
    return row


def get_checks_for_url(app, url_id):
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT * FROM checks WHERE url_id = %s", (url_id,))
    checks = cur.fetchall()
    conn.close()
    return checks



def get_all_urls(app):
    conn = get_db(app)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM urls ORDER BY id DESC")
    urls = cur.fetchall()
    return urls


def create_check_entry(app, url_id, status_code, created_at):
    conn = get_db(app)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO checks (url_id, status_code, created_at) VALUES (%s, %s, %s)",
    (url_id, status_code, created_at) )
    conn.commit()
    conn.close()