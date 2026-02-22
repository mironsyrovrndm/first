import os

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from extensions import db
from models import User, Profile, Skill, Experience, Contact, Project, ProjectImage
from .forms import ProfileForm, SkillForm, ExperienceForm, ContactForm

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')


# === Авторизация ===
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # В продакшене используйте check_password_hash
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.index'))

        flash('Неверный логин или пароль', 'danger')
    return render_template('admin/login.j2')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# === Главная страница админки ===
@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # 1. Получаем профиль
    profile = Profile.query.first()
    if not profile:
        profile = Profile(full_name="New User")
        db.session.add(profile)
        db.session.commit()

    # 2. Заполняем форму данными из БД
    profile_form = ProfileForm(obj=profile)

    # 3. Обработка сохранения профиля
    if profile_form.validate_on_submit() and 'submit_profile' in request.form:
        # === ЗАГРУЗКА ФОТО ===
        if profile_form.photo.data:
            file = profile_form.photo.data
            filename = secure_filename(file.filename)

            # Берем путь из конфига (как в app.py)
            upload_dir = current_app.config['UPLOAD_FOLDER']

            # Сохраняем файл
            file.save(os.path.join(upload_dir, filename))

            # В базу пишем просто имя файла (без префикса static/uploads/, т.к. у нас есть роут)
            profile.photo_url = filename

        # Сохраняем остальные поля
        profile_form.populate_obj(profile)
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('admin.index'))

    # 4. Данные для списков
    skills = Skill.query.all()
    experience = Experience.query.all()
    contacts = Contact.query.all()

    # Проекты на главной админки
    projects = Project.query.order_by(Project.order_num.asc()).all()

    return render_template('admin/index.j2',
                           profile_form=profile_form,
                           skills=skills,
                           experience=experience,
                           contacts=contacts,
                           projects=projects)


# === CRUD для Скиллов ===
@admin_bp.route('/skill/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill()
        form.populate_obj(skill)
        db.session.add(skill)
        db.session.commit()
        flash('Навык добавлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Добавить навык")


# НОВЫЙ РОУТ: Редактирование навыка
@admin_bp.route('/skill/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_skill(id):
    skill = Skill.query.get_or_404(id)
    form = SkillForm(obj=skill)
    if form.validate_on_submit():
        form.populate_obj(skill)
        db.session.commit()
        flash('Навык обновлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Редактировать навык")


@admin_bp.route('/skill/delete/<int:id>')
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Навык удален', 'warning')
    return redirect(url_for('admin.index'))


# === CRUD для Опыта ===
@admin_bp.route('/experience/add', methods=['GET', 'POST'])
@login_required
def add_experience():
    form = ExperienceForm()
    if form.validate_on_submit():
        exp = Experience()
        form.populate_obj(exp)
        db.session.add(exp)
        db.session.commit()
        flash('Опыт добавлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Добавить опыт")


# НОВЫЙ РОУТ: Редактирование опыта
@admin_bp.route('/experience/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_experience(id):
    exp = Experience.query.get_or_404(id)
    form = ExperienceForm(obj=exp)
    if form.validate_on_submit():
        form.populate_obj(exp)
        db.session.commit()
        flash('Опыт обновлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Редактировать опыт")


@admin_bp.route('/experience/delete/<int:id>')
@login_required
def delete_experience(id):
    exp = Experience.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    return redirect(url_for('admin.index'))


# === CRUD для Контактов ===
@admin_bp.route('/contact/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = ContactForm()
    if form.validate_on_submit():
        c = Contact()
        form.populate_obj(c)
        db.session.add(c)
        db.session.commit()
        flash('Контакт добавлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Добавить контакт")


# НОВЫЙ РОУТ: Редактирование контакта
@admin_bp.route('/contact/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    c = Contact.query.get_or_404(id)
    form = ContactForm(obj=c)
    if form.validate_on_submit():
        form.populate_obj(c)
        db.session.commit()
        flash('Контакт обновлен', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_item.j2', form=form, title="Редактировать контакт")


@admin_bp.route('/contact/delete/<int:id>')
@login_required
def delete_contact(id):
    c = Contact.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('admin.index'))


# === CRUD для ПРОЕКТОВ ===
@admin_bp.route('/projects')
@login_required
def projects_list():
    projects = Project.query.order_by(Project.order_num.asc()).all()
    return render_template('admin/projects_list.j2', projects=projects)


@admin_bp.route('/project/new', methods=['GET', 'POST'])
@admin_bp.route('/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id=None):
    if id:
        project = Project.query.get_or_404(id)
    else:
        project = Project()

    if request.method == 'POST':
        # 1. Текстовые поля
        project.title_ru = request.form.get('title_ru')
        project.title_en = request.form.get('title_en') or ''
        project.short_desc_ru = request.form.get('short_desc_ru')
        project.short_desc_en = request.form.get('short_desc_en') or ''
        project.full_desc_ru = request.form.get('full_desc_ru')
        project.full_desc_en = request.form.get('full_desc_en') or ''
        project.video_url = request.form.get('video_url')
        project.order_num = int(request.form.get('order') or 0)
        project.is_published = 'is_published' in request.form

        # 2. ПУТЬ ДЛЯ ЗАГРУЗКИ (ИСПРАВЛЕНО: берем из конфига)
        upload_dir = current_app.config['UPLOAD_FOLDER']

        # 3. Загрузка ПРЕВЬЮ
        preview = request.files.get('preview_image')
        if preview and preview.filename:
            filename = secure_filename(f"preview_{preview.filename}")
            preview.save(os.path.join(upload_dir, filename))

            # Сохраняем имя файла (можно без uploads/, т.к. роут сам знает откуда брать)
            project.preview_image = filename

        # 4. Сохраняем проект
        if not project.id:
            db.session.add(project)
            db.session.flush()

        # 5. Загрузка ГАЛЕРЕИ
        gallery_files = request.files.getlist('gallery_images')
        current_count = ProjectImage.query.filter_by(project_id=project.id).count()
        limit = 15

        for file in gallery_files:
            if file.filename and current_count < limit:
                filename = secure_filename(f"proj_{project.id}_{file.filename}")
                file.save(os.path.join(upload_dir, filename))

                img = ProjectImage(project_id=project.id, image_filename=filename)
                db.session.add(img)
                current_count += 1

        db.session.commit()
        flash('Проект сохранен!', 'success')

        return redirect(url_for('admin.edit_project', id=project.id))

    return render_template('admin/project_form.j2', project=project)


@admin_bp.route('/project/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Проект удален', 'warning')
    return redirect(url_for('admin.projects_list'))


@admin_bp.route('/project/gallery/delete/<int:img_id>')
@login_required
def delete_gallery_image(img_id):
    img = ProjectImage.query.get_or_404(img_id)
    project_id = img.project_id

    # ИСПРАВЛЕНО: путь из конфига
    upload_dir = current_app.config['UPLOAD_FOLDER']

    # Чистим имя файла от старых префиксов, если они были в базе
    clean_filename = img.image_filename.replace('uploads/', '').replace('static/', '')

    try:
        os.remove(os.path.join(upload_dir, clean_filename))
    except OSError:
        pass

    db.session.delete(img)
    db.session.commit()
    flash('Фото удалено', 'info')
    return redirect(url_for('admin.edit_project', id=project_id))
