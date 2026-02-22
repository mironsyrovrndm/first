from flask_login import UserMixin
from extensions import db
import re


# Админ (для входа в админку)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))


# Профиль (Основная инфо: Имя, Фото, Интро + Заголовки навыков)
class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)

    # Основная информация
    full_name = db.Column(db.String(100), nullable=False, default="New User")
    intro_text = db.Column(db.Text)  # "Привет! Я Нина..."
    photo_url = db.Column(db.String(255))  # Путь к файлу

    # Блоки текста (можно через Enter)
    specialization = db.Column(db.Text)  # "ФИРМЕННЫЙ СТИЛЬ... / 3D"
    education = db.Column(db.Text)  # "СПбГУПТД..."
    looking_for = db.Column(db.Text)  # "з/п 60к+..."

    # === НОВЫЕ ПОЛЯ: Настраиваемые заголовки для колонок навыков ===
    # По умолчанию ставим то, что было раньше в верстке
    skill_title_design = db.Column(db.String(100), default="Графический дизайн + Web + 3D")
    skill_title_video = db.Column(db.String(100), default="Видео и анимация")
    skill_title_soft = db.Column(db.String(100), default="Soft Skills")


# Навыки (Hard & Soft)
class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # 'design', 'video', 'soft'
    name = db.Column(db.String(100))  # "Adobe Photoshop"
    level = db.Column(db.Integer)  # 7 (из 10), для Soft skills можно null


# Опыт работы
class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  # "Фриланс (граф. дизайнер)"
    period = db.Column(db.String(50))  # "2024 - наст.вр."
    description = db.Column(db.Text)  # Список задач через enter


# Контакты
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    network_name = db.Column(db.String(50))  # "Behance", "Telegram"
    link_url = db.Column(db.String(255))  # "https://be.net/..."
    display_text = db.Column(db.String(100))  # "ninaart..."


# Проекты
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)

    # --- Поля для превью (Главная страница) ---
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=True)
    short_desc_ru = db.Column(db.Text, nullable=True)  # Краткое описание
    short_desc_en = db.Column(db.Text, nullable=True)
    preview_image = db.Column(db.String(255), nullable=True)  # Обложка (превью)

    # --- Поля для внутренней страницы ---
    full_desc_ru = db.Column(db.Text, nullable=True)
    full_desc_en = db.Column(db.Text, nullable=True)

    # Ссылка на видео (храним то, что вставил пользователь)
    video_url = db.Column(db.String(500), nullable=True)

    # --- Системные поля ---
    # ИСПРАВЛЕНО: order -> order_num (чтобы совпадать с базой данных)
    order_num = db.Column(db.Integer, default=0)

    is_published = db.Column(db.Boolean, default=True)  # Черновик или нет
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Связь с галереей (удаление проекта удалит и фотки из БД)
    gallery_images = db.relationship('ProjectImage', backref='project', cascade='all, delete-orphan')

    @property
    def video_embed_url(self):
        """Конвертирует ссылку YouTube/RuTube в Embed-ссылку для iframe"""
        if not self.video_url:
            return None

        url = self.video_url.strip()

        # 1. YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            regex = (
                r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            match = re.match(regex, url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(6)}"

        # 2. RuTube
        if 'rutube.ru' in url:
            # Из https://rutube.ru/video/12345/ делаем https://rutube.ru/play/embed/12345/
            regex = r'rutube\.ru/video/([a-zA-Z0-9]+)'
            match = re.search(regex, url)
            if match:
                return f"https://rutube.ru/play/embed/{match.group(1)}"
            if '/play/embed/' in url:
                return url

        return None  # Если ссылка не распознана


class ProjectImage(db.Model):
    __tablename__ = 'project_images'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
