
from flask import Flask, render_template, request, flash, redirect, url_for
import os
from dotenv import load_dotenv

from validation import is_valid_url, normalize_url
from .database import check_url_existence, add_urls, get_one_url, get_checks_for_url, get_all_urls
from datetime import datetime



load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
# app.run()

@app.route('/')
def index():
    return render_template('index.html')


@app.post("/urls")
def add_url():
    # получаем данные из формы request.form
    url_name = request.form.get('url')
    # нормализуем URL
    normalized_url_name = normalize_url(url_name)
    # валидируем наш юрл,  если ошибка, то выводим сообщение (flash_message) и редиректим на index
    if not is_valid_url(url_name):
        flash("Некорректный URL! Пожалуйста введите корректный URL", "Error")

        return render_template(
                                'index.html',
                                url_name=url_name
                                ), 422
    # Добавляем юрл (через псукопг)
    existing_url = check_url_existence(app, normalized_url_name)
    
    # Если URL уже существует, редиректим на страницу с существующим коротким URL
    if existing_url:
        return redirect(url_for('show_url_by_id', url_id=existing_url.id))
    
    # если юрл уже есть - редиректим на конкретный юрл
    # если все норм, то редиректим на конретный юрл
    new_url =add_urls(app, normalized_url_name)
    
    return redirect(url_for('show_url_by_id', url_id=new_url.id))


@app.get("/urls")
def get_urls():
    # Получаем из бд наши юрлы
    urls = get_all_urls(app)
    # Добавляем их в шаблон и воззвращаем его
    
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:url_id>')
def show_url_by_id(url_id):
    # получаем юрл из бд
    _url = get_one_url(app, url_id)
    # если все нормально, то возвращаем шаблон с нужными данными
    if _url:
        return render_template('urls.html', url=_url)
    # если проблемы, то флэшим сообщение и редиректим на список с урлами
    else:
        flash('URL not found', 'error')
        
        return redirect(url_for('get_urls'))


# Обработчик маршрута POST /urls/<id>/checks
@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    # Получаем данные из запроса
    url_id = id
    created_at = datetime.now()
    return f"Проверка создана. URL ID: {url_id}, Created at: {created_at}"


@app.route('/urls/<int:url_id>')
def show_url(url_id):
    _url = get_one_url(app, url_id)  # Функция, которая получает URL по ID
    checks = get_checks_for_url(url_id)  # Получаем все проверки для данного URL ID
    return render_template('urls.html', url=_url, checks=checks)

""""
existing_url = check_url_existence(url_name) должен быть existing_url = check_url_existence(app, normalized_url_name)
(обрати внимание, что здесь лучше использовать уже нормализованный URL).
new_url = add_urls(url_name) должен быть new_url = add_urls(app, normalized_url_name).
_url = get_one_url(url_id) должен быть _url = get_one_url(app, url_id). 
"""
