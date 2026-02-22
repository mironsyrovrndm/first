import sys
import os

# Добавляем родительскую директорию (корень проекта) в путь поиска модулей,
# чтобы Python увидел пакет 'src' при запуске скрипта из папки src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import User


def create_admin():
    with app.app_context():
        # Проверяем, есть ли уже админ
        existing_user = User.query.filter_by(username='admin').first()

        if not existing_user:
            # Создаем пользователя (пароль без хеша для простоты, как вы просили)
            u = User(username='admin', password_hash='admin')
            db.session.add(u)
            db.session.commit()
            print("---------------------------------------------------")
            print("SUCCESS: Admin user created!")
            print("Login: admin")
            print("Password: admin")
            print("---------------------------------------------------")
        else:
            print("---------------------------------------------------")
            print("INFO: User 'admin' already exists.")
            print("---------------------------------------------------")


if __name__ == "__main__":
    create_admin()
