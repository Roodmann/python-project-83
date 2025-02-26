
from flask import Flask
import os
from dotenv import load_dotenv



load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.run()

@app.route('/')
def index():
    return 'Привет, это страница анализатора!'
