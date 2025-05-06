
from flask import Flask, render_template, request, flash, redirect, url_for
import os
from dotenv import load_dotenv

from validation import is_valid_url
from .database import check_url_existence, add_urls, get_one_url



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
    # валидируем наш юрл,  если ошибка, то выводим сообщение (flash_message) и редиректим на index
    if not is_valid_url(url_name):
        flash("Некорректный URL! Пожалуйста введите корректный URL", "Error")

        return render_template(
                                'index.html',
                                url_name=url_name
                                ), 422
    # Добавляем юрл (через псукопг)
    existing_url = check_url_existence(url_name)
    
    # Если URL уже существует, редиректим на страницу с существующим коротким URL
    if existing_url:
        return redirect(url_for('show_url_by_id', url_id=existing_url.id))
    
    # если юрл уже есть - редиректим на конкретный юрл
    # если все норм, то редиректим на конретный юрл
    new_url = add_urls(url_name)
    
    return redirect(url_for('show_url_by_id', url_id=new_url.id))


@app.get("/urls")
def get_urls():
    # Получаем из бд наши юрлы
    urls = add_url()
    # Добавляем их в шаблон и воззвращаем его
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:url_id>')
def show_url_by_id(url_id):
    # получаем юрл из бд
    _url = get_one_url(url_id)
    # если все нормально, то возвращаем шаблон с нужными данными
    if _url:
        return render_template('urls.html', url=_url)
    # если проблемы, то флэшим сообщение и редиректим на список с урлами
    else:
        flash('URL not found', 'error')
        return redirect(url_for('get_urls'))
