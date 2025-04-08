
import psycopg2

try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='test', user='postgres', password='secret', host='host')

except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

    # У строки следующий формат: {provider}://{user}:{password}@{host}:{port}/{db}
# export DATABASE_URL=postgresql://janedoe:mypassword@localhost:5432/mydb



def check_url_existence(url_name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM urls WHERE name = %s", (url_name,))
    result = cur.fetchone()

    if result:
        url_id = result[0]
    else:
        url_id = None

    conn.close()
    return url_id


def add_url(url_name):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url_name,))
    url_id = cur.fetchone()[0]

    conn.commit()
    conn.close()
    return url_id


def get_one_url(url_id):
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
    row = cur.fetchone()
    return row
