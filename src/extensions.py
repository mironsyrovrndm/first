from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Создаем объекты расширений
db = SQLAlchemy()
login_manager = LoginManager()


def init_extensions(_app):
    global db, login_manager

    # Инициализируем DB
    db.init_app(_app)

    # Инициализируем LoginManager
    login_manager.init_app(_app)
    login_manager.login_view = 'admin.login'  # Если есть блюпринт admin


# === ВАЖНОЕ ДОБАВЛЕНИЕ: User Loader ===
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Импортируем модель User (она должна быть в models.py)
    # Функция должна вернуть объект пользователя или None
    # Используем SQLAlchemy query
    return User.query.get(int(user_id))
