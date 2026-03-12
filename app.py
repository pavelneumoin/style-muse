from flask import Flask
import os
from dotenv import load_dotenv
from database import init_db

# Инициализируем БД
init_db()

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'style-muse-magic-secret-key-2026')

from routes.main import main_bp

app.register_blueprint(main_bp, url_prefix='/style-muse')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)