from flask import flash
from flask_admin import BaseView
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import (
    current_user,
    verify_jwt_in_request,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from src.constants import (
    DELETE_ERROR_MESSAGE,
)


class BaseView(BaseView):

    """Базовый класс для всех представлений."""

    def is_accessible(self) -> bool:
        """Проверка доступа."""
        verify_jwt_in_request()
        return super().is_accessible() and current_user.is_admin


class CustomAdminView(ModelView):

    """Добавление в формы с CSRF."""

    list_template = 'csrf/list.html'
    edit_template = 'csrf/edit.html'
    create_template = 'csrf/create.html'

    def is_accessible(self) -> bool:
        """Проверка доступа."""
        verify_jwt_in_request()
        return current_user.is_admin


class IntegrityErrorMixin:

    """Миксин обработки ошибки удаления связанного объекта и БД."""

    delete_error_message = ''

    def delete_model(self, model: SQLAlchemy) -> bool:
        """Переопределяем метод удаления модели."""
        try:
            # Пытаемся удалить модель
            self.session.delete(model)
            self.session.commit()
            return True
        except IntegrityError as e:
            # Откатываем транзакцию
            self.session.rollback()
            # Логируем сообщение об ошибке (по желанию)
            print(f'Ошибка целостности: {str(e)}')
            # Отображаем пользовательское сообщение
            flash(DELETE_ERROR_MESSAGE + self.delete_error_message, 'error')
            return False


class NotVisibleMixin(BaseView):

    """Миксин для скрытия страницы из админки."""

    def is_visible(self) -> bool:
        """Скрывает представление из основного меню Flask-Admin."""
        return False
