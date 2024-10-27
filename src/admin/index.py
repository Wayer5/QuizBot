from flask import Response, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_jwt_extended import (
    current_user,
    verify_jwt_in_request,
)


class MyAdminIndexView(AdminIndexView):

    """Класс для переопределения главной страницы администратора."""

    @expose('/')
    def index(self) -> Response:
        """Переопределение главной страницы администратора."""
        verify_jwt_in_request()
        if current_user.is_admin is False:
            return redirect(url_for('quizzes'))
        admin_menu = self.admin.menu()
        return self.render('admin/admin_index.html', admin_menu=admin_menu)
