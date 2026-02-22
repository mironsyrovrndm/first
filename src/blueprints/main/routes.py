import os
from flask import Blueprint, render_template, session, request, send_from_directory, current_app, abort
from models import Profile, Contact, Project


main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main-static')


def _build_content(profile, contacts, projects):
    contact_map = {c.network_name.lower(): c.display_text for c in contacts if c.network_name and c.display_text}

    hero_image = profile.photo_url if profile and profile.photo_url else None
    if hero_image:
        hero_image = hero_image.replace('static/', '').replace('uploads/', '')

    about_education = []
    if profile and profile.education:
        about_education = [line.strip() for line in profile.education.split('\n') if line.strip()]

    products = [
        {
            'badge': 'Индивидуально',
            'title': p.title_ru,
            'text': p.short_desc_ru or 'Описание скоро появится.',
            'meta': 'Онлайн / Оффлайн',
        }
        for p in projects[:6]
    ]

    return {
        'hero_label': 'Бережная и профессиональная поддержка',
        'hero_title': profile.full_name if profile and profile.full_name else 'Психолог Анна Луиза',
        'hero_text': profile.intro_text if profile and profile.intro_text else 'Помогаю вернуть опору, услышать себя и улучшить качество жизни.',
        'hero_button': 'Записаться на консультацию',
        'hero_image': hero_image,
        'about_image': hero_image,
        'about_title': 'Обо мне',
        'about_education': about_education or ['Высшее психологическое образование', 'Дополнительная подготовка по психотерапии'],
        'products_title': 'Продукты',
        'products': products or [
            {'badge': 'Индивидуально', 'title': 'Личная консультация', 'text': 'Разбор вашего запроса и план работы.', 'meta': '60 минут'}
        ],
        'clients_title': 'Клиентам',
        'clients_subtitle': 'Работаю бережно и в темпе, который подходит вам.',
        'clients': [
            {'title': 'Тревога и стресс', 'text': 'Находим устойчивость и способы саморегуляции.'},
            {'title': 'Отношения', 'text': 'Помогаю выстраивать границы и близость.'},
            {'title': 'Самооценка', 'text': 'Возвращаем контакт с собой и внутреннюю опору.'},
        ],
        'supervision_title': 'Супервизия',
        'supervision_subtitle': 'Для начинающих и практикующих специалистов.',
        'supervision': [
            {'title': 'Разовая супервизия', 'price': '5 000 ₽', 'meta': '90 минут', 'bullets': ['Разбор кейса', 'Этический фокус']},
            {'title': 'Пакет 4 встреч', 'price': '18 000 ₽', 'meta': 'В течение месяца', 'bullets': ['Поддержка между встречами', 'План развития']},
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


@main_bp.route('/')
@main_bp.route('/<lang>/')
def index(lang='ru'):
    session['lang'] = lang
    profile = Profile.query.first()
    contacts = Contact.query.all()
    projects = Project.query.filter_by(is_published=True).order_by(Project.order_num.asc()).all()

    gallery_images = []
    for p in projects:
        if p.preview_image and not p.preview_image.startswith('http'):
            gallery_images.append(p.preview_image.replace('static/', '').replace('uploads/', ''))

    return render_template(
        'main/index.j2',
        content=_build_content(profile, contacts, projects),
        gallery_images=gallery_images,
        submitted=False,
    )


@main_bp.route('/contact', methods=['POST'])
def contact():
    profile = Profile.query.first()
    contacts = Contact.query.all()
    projects = Project.query.filter_by(is_published=True).order_by(Project.order_num.asc()).all()
    gallery_images = [
        p.preview_image.replace('static/', '').replace('uploads/', '')
        for p in projects
        if p.preview_image and not p.preview_image.startswith('http')
    ]

    return render_template(
        'main/index.j2',
        content=_build_content(profile, contacts, projects),
        gallery_images=gallery_images,
        submitted=True,
    )


@main_bp.route('/media/<category>/<path:photo_id>')
def media(category, photo_id):
    if category not in {'hero', 'about', 'uploads'}:
        abort(404)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, photo_id)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(upload_folder, photo_id)


@main_bp.route('/<lang>/projects/<int:id>')
def project_detail(lang, id):
    session['lang'] = lang
    project = Project.query.get_or_404(id)
    return render_template('main/project_detail.j2', project=project, lang=lang)
