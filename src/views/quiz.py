from flask import (
    render_template,
    request,
)

from src import app
from src.constants import DEFAULT_PAGE_NUMBER, HTTP_NOT_FOUND, PER_PAGE
from src.crud.quiz import quiz_crud


@app.route('/<int:category_id>/', methods=['GET'])
async def quizzes(category_id: int) -> str:
    """Вывод страницы викторин."""
    page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
    per_page = PER_PAGE
    quizzes_paginated = quiz_crud.get_by_category_id(category_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    if not quizzes_paginated.items:
        return render_template('errors/404.html'), HTTP_NOT_FOUND

    return render_template(
        'quizzes.html',
        quizzes=quizzes_paginated.items,
        pagination=quizzes_paginated,
        category_id=category_id,
    )
