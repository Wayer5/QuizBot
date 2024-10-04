from typing import Callable

from flask import Request, Response
from flask_http_middleware import BaseHTTPMiddleware
from flask_jwt_extended import (
    current_user,
    verify_jwt_in_request,
)


class AdminTokenMiddleware(BaseHTTPMiddleware):

    """Проверка токена для доступа к админке."""

    def __init__(self) -> None:
        """Инит как инит."""
        super().__init__()

    def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Проверка на авторизацию и наличие прав админа.

        Args:
        ----
            request (Request): запрос, содержащий данные.
            call_next (Callable): функция, вызывает ответ на запрос.

        """
        if 'admin' not in request.url:
            return call_next(request)

        verify_jwt_in_request()
        if current_user.is_admin is False or current_user.is_active is False:
            raise Exception('Access denied')
        return call_next(request)
