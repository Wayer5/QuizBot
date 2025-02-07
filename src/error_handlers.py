from typing import Callable

from flask import Response, render_template, request

from . import app
from .constants import HTTP_NOT_FOUND, UNAUTHORIZED
from .jwt_utils import jwt


@app.errorhandler(404)
def page_not_found(error: Exception) -> Response:
    """Обработчик ошибки 404 для всех запросов.

    Args:
    ----
    error (Exception): Ошибка, вызвавшая обработку.

    Returns:
    -------
    Response: HTML-страница для отображения ошибки 404.

    """
    if request.path.startswith('/admin'):
        # Ошибка на странице админки
        return (
            render_template(
                'errors/404.html',
                is_admin=True,
            ),
            HTTP_NOT_FOUND,
        )
    # Ошибка на пользовательской странице
    index = True if request.path == '/' else False
    return (
        render_template(
            'errors/404.html',
            is_admin=False,
            index=index,
        ),
        HTTP_NOT_FOUND,
    )


@jwt.unauthorized_loader
def unauthorized_callback(callback: Callable) -> Response:
    """Обработка ошибки 401 при отсутствии jwt токена."""
    return render_template('errors/401.html'), UNAUTHORIZED


@app.errorhandler(401)
def unauthorize(error: Exception) -> Response:
    """Обработчик ошибки 401 для всех запросов.

    Args:
    ----
    error (Exception): Ошибка, вызвавшая обработку.

    Returns:
    -------
    Response: HTML-страница для отображения ошибки 404.

    """
    return render_template('errors/401.html'), UNAUTHORIZED
