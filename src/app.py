import os
from importlib import import_module
from flask import Blueprint, Flask, send_from_directory
from extensions import init_extensions


def create_app() -> Flask:
    _app = Flask(__name__, static_folder='static')

    # 1. Загружаем конфиг
    _app.config.from_pyfile("settings.py")
    _app.config.from_envvar("FLASK_SETTINGS")

    return _app


app = create_app()

with app.app_context():
    init_extensions(app)
    for name in ['main', 'admin']:
        try:
            mod = import_module(f"src.blueprints.{name}.routes")
            for item in vars(mod).values():
                if isinstance(item, Blueprint):
                    app.register_blueprint(item)
                    break
        except Exception as e:
            print(f"Error loading {name}: {e}")


# === РОУТ ДЛЯ КАРТИНОК ===
# Отдает файлы из папки /uploads (которая в конфиге)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
