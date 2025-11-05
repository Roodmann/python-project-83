
from flask import Flask, render_template, request, flash, redirect, url_for
import os
import requests
from dotenv import load_dotenv


from page_analyzer.url_validator import is_valid_url, normalize_url
from .database import check_url_existence, add_urls, get_one_url, get_all_urls, create_check_entry
from datetime import datetime



load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
# app.run()

@app.route('/')
def index():
    """Обработчик главной страницы сайта"""
    
    return render_template('index.html')


@app.post("/urls")
def add_url():
    """Обработчик POST-запроса для добавления нового URL"""
    
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
    """Обработчик GET-запроса для получения списка всех URL"""
    
    # Получаем из бд наши юрлы
    urls = get_all_urls(app)
    # Добавляем их в шаблон и воззвращаем его
    
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:url_id>')
def show_url_by_id(url_id):
    """Обработчик GET-запроса для отображения деталей конкретного URL по его ID"""
    
    # получаем юрл из бд
    _url = get_one_url(app, url_id)
    # если все нормально, то возвращаем шаблон с нужными данными
    if _url:
        return render_template('url.html', url=_url)
    # если проблемы, то флэшим сообщение и редиректим на список с урлами
    else:
        flash('URL not found', 'error')
        
        return redirect(url_for('get_urls'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    """Обработчик для создания новой проверки статуса указанного URL"""
    
    url_obj = get_one_url(app, id)  # Получение объекта URL
    #Если URL не найден, выводит сообщение об ошибке и перенаправляет на страницу списка URL.
    if not url_obj: 
        flash("URL не найден", "error")
        return redirect(url_for('get_urls'))

    created_at = datetime.now()# Текущая дата и время для записи проверки

    try:
        response = requests.get(url_obj.name, timeout=3)# Выполняем запрос к указанному URL с тайм-аутом
        response.raise_for_status()# Проверяем, что запрос прошел успешно
        flash('Страница успешно проверена', 'success')
        # Создаем новую запись проверки в базе данных
        create_check_entry(app, url_obj.id, response.status_code, created_at)
    
    except requests.RequestException:
        # В случае ошибки при выполнении запроса выводим сообщение об ошибке
        flash('Произошла ошибка при проверке', 'danger')
        # Перенаправляем пользователя на страницу с деталями URL
        return redirect(url_for('show_url_by_id', url_id=id))
