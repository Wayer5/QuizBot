from flask import request, session
from flask_admin import Admin
from flask_babelex import Babel

from . import app

# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app)
# Создания экземпляра админ панели
admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')


@babel.localeselector
def get_locale() -> None:
    """Перевод админ панели на другие языки."""
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    # Меняется только параметр 'ru'
    return session.get('lang', 'ru')
