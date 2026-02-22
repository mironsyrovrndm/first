from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, URL


class ProfileForm(FlaskForm):
    full_name = StringField('Полное имя', validators=[DataRequired()])
    intro_text = TextAreaField('Интро (Привет! Я...)', validators=[DataRequired()])

    # Заменяем текстовое поле ссылки на загрузку файла
    photo = FileField('Загрузить фото профиля', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Только картинки!')
    ])

    # Можно оставить скрытое поле для url, если нужно, но мы будем сохранять путь в БД

    specialization = TextAreaField('Специализация (общая, каждая с новой строки)')
    education = TextAreaField('Образование')
    looking_for = TextAreaField('Что я ищу')

    # === ЗАГОЛОВКИ ДЛЯ КОЛОНОК НАВЫКОВ ===
    skill_title_design = StringField('Заголовок колонки слева')
    skill_title_video = StringField('Заголовок колонки справа')
    skill_title_soft = StringField('Заголовок колонки Навыков')

    submit = SubmitField('Сохранить профиль')


class SkillForm(FlaskForm):
    category = SelectField('Категория', choices=[
        ('design', 'Слева'),
        ('video', 'Справа'),
        ('soft', 'Навыки')
    ], validators=[DataRequired()])
    name = StringField('Название навыка', validators=[DataRequired()])
    level = IntegerField('Уровень (1-10)', validators=[Optional(), NumberRange(min=1, max=10)])
    submit = SubmitField('Сохранить навык')


class ExperienceForm(FlaskForm):
    title = StringField('Должность/Проект', validators=[DataRequired()])
    period = StringField('Период (напр. 2024 - наст.вр.)')
    description = TextAreaField('Описание задач (каждая с новой строки)')
    submit = SubmitField('Сохранить опыт')


class ContactForm(FlaskForm):
    network_name = StringField('Название (Telegram)', validators=[DataRequired()])
    link_url = StringField('Ссылка', validators=[DataRequired()])
    display_text = StringField('Текст ссылки (@user)', validators=[DataRequired()])
    submit = SubmitField('Сохранить контакт')
