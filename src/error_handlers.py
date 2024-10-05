from flask import Response, jsonify, render_template, request

from . import app


class InvalidAPIUsage(Exception):

    """Класс для обработки ошибок использования API."""

    status_code: int = 400

    def __init__(self, message: str, status_code: int = None) -> None:
        """Инициализация ошибки API.

        Args:
            message (str): Сообщение об ошибке.
            status_code (int, optional): Статус-код HTTP. Defaults to None.

        """
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict:
        """Возвращает ошибку в виде словаря.

        Returns:
            dict: Словарь с сообщением об ошибке.

        """
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error: InvalidAPIUsage) -> jsonify:
    """Обработчик ошибок API.

    Args:
        error (InvalidAPIUsage): Экземпляр ошибки.

    Returns:
        jsonify: JSON-ответ с сообщением об ошибке и статус-кодом.

    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def page_not_found(error: Exception) -> Response:
    """Обработчик ошибки 404 для всех запросов.

    Args:
        error (Exception): Ошибка, вызвавшая обработку.

    Returns:
        Response: HTML-страница или JSON-ответ в зависимости от URL.

    """
    if request.path.startswith("/api/"):
        return jsonify({"message": "Resource not found"}), 404
    return render_template("404.html"), 404
