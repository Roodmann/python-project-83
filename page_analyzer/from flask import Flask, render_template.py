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

@app.route('/')
def index():
    return render_template('index.html')

@app.post("/urls")
def add_url():
    url_name = request.form.get('url')
    normalized_url_name = normalize_url(url_name)
    if not is_valid_url(url_name):
        flash("Некорректный URL! Пожалуйста введите корректный URL", "Error")
        return render_template('index.html', url_name=url_name), 422

    existing_url = check_url_existence(app, normalized_url_name)
    if existing_url:
        return redirect(url_for('show_url', url_id=existing_url.id))
    new_url = add_urls(app, normalized_url_name)
    return redirect(url_for('show_url', url_id=new_url.id))

@app.get("/urls")
def get_urls():
    urls = get_all_urls(app)
    return render_template('urls.html', urls=urls)

@app.get('/urls/<int:url_id>')
def show_url(url_id):
    _url = get_one_url(app, url_id)
    checks = get_checks_for_url(url_id)
    if _url:
        return render_template('url.html', url=_url, checks=checks)
    else:
        flash('URL not found', 'error')
        return redirect(url_for('get_urls'))

@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    created_at = datetime.now()
    # Логика создания проверки
    return f"Проверка создана. URL ID: {id}, Created at: {created_at}"