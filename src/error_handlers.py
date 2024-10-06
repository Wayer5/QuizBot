from flask import Response, render_template, request, url_for

from . import app


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
    is_category_page = request.path == url_for('categories')
    return render_template("404.html", is_category_page=is_category_page), 404
