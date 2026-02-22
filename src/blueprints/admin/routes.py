import os
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from extensions import db
from models import User, Profile, Skill, Experience, Contact, Project, ProjectImage
from .forms import ProfileForm, SkillForm, ExperienceForm, ContactForm

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static', url_prefix='/admin')


def _get_content(profile, contacts, projects):
    contact_map = {c.network_name.lower(): c.display_text for c in contacts if c.network_name and c.display_text}
    hero_image = profile.photo_url if profile and profile.photo_url else None
    if hero_image:
        hero_image = hero_image.replace('static/', '').replace('uploads/', '')
    about_education = [line.strip() for line in (profile.education or '').split('\n') if line.strip()] if profile else []
    return {
        'hero_label': 'Бережная и профессиональная поддержка',
        'hero_title': profile.full_name if profile and profile.full_name else 'Психолог Анна Луиза',
        'hero_text': profile.intro_text if profile and profile.intro_text else 'Помогаю вернуть опору, услышать себя и улучшить качество жизни.',
        'hero_button': 'Записаться на консультацию',
        'hero_image': hero_image,
        'about_image': hero_image,
        'about_title': 'Обо мне',
        'about_education': about_education or ['Высшее психологическое образование'],
        'products_title': 'Продукты',
        'products': [
            {'badge': 'Индивидуально', 'title': p.title_ru, 'text': p.short_desc_ru or '', 'meta': 'Онлайн / Оффлайн'}
            for p in projects[:6]
        ] or [{'badge': 'Индивидуально', 'title': 'Личная консультация', 'text': 'Разбор вашего запроса.', 'meta': '60 минут'}],
        'clients_title': 'Клиентам',
        'clients_subtitle': 'Работаю бережно и в вашем темпе.',
        'clients': [
            {'title': 'Тревога и стресс', 'text': 'Находим устойчивость и способы саморегуляции.'},
            {'title': 'Отношения', 'text': 'Помогаю выстраивать границы и близость.'},
            {'title': 'Самооценка', 'text': 'Возвращаем контакт с собой и внутреннюю опору.'},
        ],
        'supervision_title': 'Супервизия',
        'supervision_subtitle': 'Для начинающих и практикующих специалистов.',
        'supervision': [
            {'title': 'Разовая супервизия', 'price': '5 000 ₽', 'meta': '90 минут', 'bullets': ['Разбор кейса', 'Этический фокус']},
        ],
        'speaker_title': 'Я — спикер',
        'speaker_text': 'Провожу лекции и практические выступления о ментальном здоровье.',
        'speaker_button': 'Оставить заявку',
        'contacts_title': 'Контакты',
        'contacts_text': 'Оставьте заявку, и я свяжусь с вами в ближайшее время.',
        'contacts_phone': contact_map.get('телефон', '+7 (900) 000-00-00'),
        'contacts_email': contact_map.get('email', 'hello@luiza-psy.ru'),
        'contacts_telegram': contact_map.get('telegram', '@luiza_psy'),
    }


def _admin_records():
    current = current_app.config.setdefault('ADMIN_CLIENT_RECORDS', [])
    return current


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        error = 'Неверный логин или пароль'
    return render_template('admin/login.j2', error=error)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@admin_bp.route('/')
@login_required
def dashboard_redirect():
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    records = _admin_records()
    now = datetime.now()
    week_threshold = now - timedelta(days=7)
    week_total = sum(1 for r in records if datetime.fromisoformat(r['date_iso']) >= week_threshold)
    upcoming = sorted([r for r in records if datetime.fromisoformat(r['date_iso']) >= now], key=lambda x: x['date_iso'])[:5]
    stats = {'week_total': week_total, 'upcoming_total': len(upcoming), 'total': len(records)}
    return render_template('admin/dashboard.j2', stats=stats, upcoming=upcoming)


@admin_bp.route('/content')
@login_required
def content():
    profile = Profile.query.first()
    contacts = Contact.query.all()
    projects = Project.query.filter_by(is_published=True).order_by(Project.order_num.asc()).all()
    upload_folder = current_app.config['UPLOAD_FOLDER']
    uploads = []
    if os.path.isdir(upload_folder):
        uploads = sorted([f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))])
    return render_template('admin/content.j2', content=_get_content(profile, contacts, projects), uploads=uploads)


@admin_bp.route('/save-content', methods=['POST'])
@login_required
def save_content():
    profile = Profile.query.first() or Profile(full_name='Психолог Анна Луиза')
    if not profile.id:
        db.session.add(profile)

    profile.full_name = request.form.get('hero_title') or profile.full_name
    profile.intro_text = request.form.get('hero_text') or profile.intro_text
    about_education = request.form.get('about_education')
    if about_education is not None:
        profile.education = about_education

    phone = request.form.get('contacts_phone')
    email = request.form.get('contacts_email')
    telegram = request.form.get('contacts_telegram')
    mappings = [('Телефон', phone), ('Email', email), ('Telegram', telegram)]
    for network, value in mappings:
        if value is None:
            continue
        item = Contact.query.filter_by(network_name=network).first()
        if not item:
            item = Contact(network_name=network, link_url='', display_text=value)
            db.session.add(item)
        item.display_text = value

    db.session.commit()
    flash('Контент сохранен', 'success')
    return redirect(url_for('admin.content'))


@admin_bp.route('/clients')
@login_required
def clients():
    return render_template('admin/clients.j2', records=sorted(_admin_records(), key=lambda x: x['date_iso']), created=False)


@admin_bp.route('/add-client', methods=['POST'])
@login_required
def add_client():
    date = request.form.get('client_date')
    time = request.form.get('client_time') or '00:00'
    dt = datetime.fromisoformat(f'{date}T{time}')
    records = _admin_records()
    next_id = max((r['id'] for r in records), default=0) + 1
    records.append({
        'id': next_id,
        'name': request.form.get('client_name', ''),
        'phone': request.form.get('client_phone', ''),
        'telegram': request.form.get('client_telegram', ''),
        'complaint': request.form.get('client_complaint', ''),
        'status': 'Новая',
        'date': dt.strftime('%d.%m.%Y %H:%M'),
        'date_iso': dt.isoformat(),
    })
    return render_template('admin/clients.j2', records=sorted(records, key=lambda x: x['date_iso']), created=True)


@admin_bp.route('/update-client-status', methods=['POST'])
@login_required
def update_client_status():
    record_id = int(request.form.get('record_id'))
    new_status = request.form.get('status')
    for record in _admin_records():
        if record['id'] == record_id:
            record['status'] = new_status
            break
    return redirect(url_for('admin.clients'))


@admin_bp.route('/upload-hero', methods=['POST'])
@login_required
def upload_hero():
    profile = Profile.query.first() or Profile(full_name='Психолог Анна Луиза')
    if not profile.id:
        db.session.add(profile)
    photo = request.files.get('photo')
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        profile.photo_url = filename
        db.session.commit()
    return redirect(url_for('admin.content'))


@admin_bp.route('/delete-hero', methods=['POST'])
@login_required
def delete_hero():
    profile = Profile.query.first()
    if profile and profile.photo_url:
        profile.photo_url = None
        db.session.commit()
    return redirect(url_for('admin.content'))


@admin_bp.route('/upload-about', methods=['POST'])
@login_required
def upload_about():
    return redirect(url_for('admin.upload_hero'))


@admin_bp.route('/delete-about', methods=['POST'])
@login_required
def delete_about():
    return redirect(url_for('admin.delete_hero'))


@admin_bp.route('/upload-gallery', methods=['POST'])
@login_required
def upload_gallery():
    photos = request.files.getlist('photo')
    for photo in photos:
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('admin.content'))


@admin_bp.route('/delete-gallery', methods=['POST'])
@login_required
def delete_gallery():
    filename = (request.form.get('filename') or '').replace('..', '')
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('admin.content'))


# === legacy routes kept ===
@admin_bp.route('/legacy', methods=['GET', 'POST'])
@login_required
def index():
    profile = Profile.query.first()
    if not profile:
        profile = Profile(full_name="New User")
        db.session.add(profile)
        db.session.commit()

    profile_form = ProfileForm(obj=profile)
    if profile_form.validate_on_submit() and 'submit_profile' in request.form:
        if profile_form.photo.data:
            file = profile_form.photo.data
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            file.save(os.path.join(upload_dir, filename))
            profile.photo_url = filename
        profile_form.populate_obj(profile)
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('admin.index'))

    skills = Skill.query.all()
    experience = Experience.query.all()
    contacts = Contact.query.all()
    projects = Project.query.order_by(Project.order_num.asc()).all()
    return render_template('admin/index.j2', profile_form=profile_form, skills=skills, experience=experience, contacts=contacts, projects=projects)


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
        project.title_ru = request.form.get('title_ru')
        project.title_en = request.form.get('title_en') or ''
        project.short_desc_ru = request.form.get('short_desc_ru')
        project.short_desc_en = request.form.get('short_desc_en') or ''
        project.full_desc_ru = request.form.get('full_desc_ru')
        project.full_desc_en = request.form.get('full_desc_en') or ''
        project.video_url = request.form.get('video_url')
        project.order_num = int(request.form.get('order') or 0)
        project.is_published = 'is_published' in request.form

        upload_dir = current_app.config['UPLOAD_FOLDER']

        preview = request.files.get('preview_image')
        if preview and preview.filename:
            filename = secure_filename(f"preview_{preview.filename}")
            preview.save(os.path.join(upload_dir, filename))
            project.preview_image = filename

        if not project.id:
            db.session.add(project)
            db.session.flush()

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
    upload_dir = current_app.config['UPLOAD_FOLDER']
    clean_filename = img.image_filename.replace('uploads/', '').replace('static/', '')
    try:
        os.remove(os.path.join(upload_dir, clean_filename))
    except OSError:
        pass
    db.session.delete(img)
    db.session.commit()
    flash('Фото удалено', 'info')
    return redirect(url_for('admin.edit_project', id=project_id))
