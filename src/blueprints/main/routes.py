from flask import Blueprint, render_template, session
from models import Profile, Skill, Experience, Contact, Project

# Объявляем Blueprint 'main'
main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
@main_bp.route('/<lang>/')
def index(lang='ru'):
    # Сохраняем язык в сессии (если нужно)
    session['lang'] = lang

    # 1. Данные профиля и скиллов (из первой функции)
    profile = Profile.query.first()
    design_skills = Skill.query.filter_by(category='design').all()
    video_skills = Skill.query.filter_by(category='video').all()
    soft_skills = Skill.query.filter_by(category='soft').all()
    experience = Experience.query.all()
    contacts = Contact.query.all()

    # 2. Данные проектов (из второй функции)
    # ИСПРАВЛЕНО: order -> order_num
    projects = Project.query.filter_by(is_published=True).order_by(Project.order_num.asc()).all()

    # 3. Рендерим общий шаблон
    return render_template('main/index.j2',
                           profile=profile,
                           design_skills=design_skills,
                           video_skills=video_skills,
                           soft_skills=soft_skills,
                           experience=experience,
                           contacts=contacts,
                           projects=projects,  # Передаем проекты
                           lang=lang)          # Передаем язык


@main_bp.route('/<lang>/projects/<int:id>')
def project_detail(lang, id):
    session['lang'] = lang
    project = Project.query.get_or_404(id)

    # Если проект скрыт (is_published=False), можно добавить проверку здесь:
    # if not project.is_published: abort(404)

    return render_template('main/project_detail.j2', project=project, lang=lang)
