# from flask_admin.contrib.sqla import ModelView
from flask import request
from flask_admin import Admin
from flask_babel import Babel

from . import app  # , db

# Создания экземпляра админ панели
admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')


# Пример перевода столбцов модели на русский язык для админки

# # Класс представления модели для Flask-Admin
# class OpinionAdmin(ModelView):
#     # Задаем "verbose_name" для полей
#     column_labels = {
#         'id': 'ИД',
#         'title': 'Название',
#         'text': 'Текст',
#         'source': 'Источник',
#         'timestamp': 'Время добавления',
#         'added_by': 'Автор'
#     }
#     column_exclude_list = ['text', ]


# admin.add_view(OpinionAdmin(Opinion, db.session, name='Мнения'))


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
