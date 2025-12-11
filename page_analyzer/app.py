from page_analyzer.parser import check_page
from flask import (Flask, 
                    render_template, 
                    request, 
                    flash, 
                    redirect, 
                    url_for,
                    jsonify
                )

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

from page_analyzer.url_validator import is_valid_url, normalize_url

from .database import (check_url_existence, 
                    add_urls, 
                    get_one_url, 
                    get_all_urls, 
                    create_check_entry, 
                    get_checks_for_url
                )




load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
#app.run()

@app.route('/')
def index():
    """Обработчик главной страницы сайта"""

    return render_template('index.html', description='Описание главной страницы')


@app.post("/urls")
def add_url():
    """Обработчик POST-запроса для добавления нового URL"""
    
    # Получаем данные из формы request.form
    url_name = request.form.get('url')
    if not is_valid_url(url_name):
        # Возврат JSON с ошибкой и статусом 422
        return jsonify({"error": "Некорректный URL"}), 422
    # Нормализуем URL
    normalized_url_name = normalize_url(url_name)
    # Возвращает идентификатор существующего URL, если он есть, или None, если нет.
    existing_url_id = check_url_existence(app, normalized_url_name)
    # Если URL с таким нормализованным адресом уже существует в базе,
    # перенаправляем пользователя на страницу отображения этого существующего короткого URL.
    if existing_url_id:
        return redirect(url_for('show_url_by_id', url_id=existing_url_id))
    new_url_id = add_urls(app, normalized_url_name)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for('show_url_by_id', url_id=new_url_id))


@app.get("/urls")
def get_urls():
    """Обработчик GET-запроса для получения списка всех URL"""
    
    # Получаем из бд наши юрлы
    urls = get_all_urls(app)
    # Добавляем их в шаблон и воззвращаем его
    
    return render_template('urls.html', urls=urls, description='Описание главной страницы')


@app.get('/urls/<int:url_id>')
def show_url_by_id(url_id):
    """Обработчик GET-запроса для отображения деталей конкретного URL по его ID"""
    
    # получаем юрл из бд
    url_obj = get_one_url(app, url_id)
    # если все нормально, то возвращаем шаблон с нужными данными
    if url_obj:
        url_checks = get_checks_for_url(app, url_id)
        return render_template('url.html', url=url_obj, url_checks=url_checks, description='Описание главной страницы')
    # если проблемы, то флэшим сообщение и редиректим на список с урлами
    else:
        flash('URL not found', 'danger')
        
        return redirect(url_for('get_urls'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    """Обработчик для создания новой проверки статуса указанного URL"""

    print(f"Запуск проверки для URL с ID: {id}")
    
    url_obj = get_one_url(app, id)  # Получение объекта URL
    print(f"Объект URL из базы: {url_obj}")
    #Если URL не найден, выводит сообщение об ошибке и перенаправляет на страницу списка URL.
    if not url_obj:
        print("URL не найден в базе данных.")
        flash("URL не найден", "danger")
        return redirect(url_for('get_urls'))

    created_at = datetime.now()# Текущая дата и время для записи проверки
    print(f"Дата и время проверки: {created_at}")

    try:
        print(f"Выполнение GET-запроса к URL: {url_obj['name']}")
        response = requests.get(url_obj['name'], timeout=3)# Выполняем запрос к указанному URL с тайм-аутом
        print(f"Ответ получен с кодом: {response.status_code}")
        response.raise_for_status()# Проверяем, что запрос прошел успешно
        print("Запрос прошел успешно.")
        flash('Страница успешно проверена', 'success')
        # Парсим HTML-ответ
        html_content = response.text
        parsed_data = check_page(html_content)
        flash(f"Результаты парсинга: {parsed_data}")
        # Создаем новую запись проверки в базе данных
        create_check_entry(
            app,
            url_obj['id'],
            response.status_code,
            created_at,
            parsed_data.get('h1'),
            parsed_data.get('title'),
            parsed_data.get('description'),
        )
        print("Запись о проверке успешно добавлена.")

        return redirect(url_for('show_url_by_id', url_id=id))
    
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        # В случае ошибки при выполнении запроса выводим сообщение об ошибке
        flash('Произошла ошибка при проверке', 'danger')
        # Перенаправляем пользователя на страницу с деталями URL
        return redirect(url_for('show_url_by_id', url_id=id))
