from flask_http_middleware import BaseHTTPMiddleware
from flask_jwt_extended import verify_jwt_in_request


class AdminTokenMiddleware(BaseHTTPMiddleware):
    """Проверка токена для доступа к админке."""
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        response = call_next(request)
        if 'admin' not in request.url:
            return response
        if not verify_jwt_in_request():
            raise Exception('Access denied')
        return response
