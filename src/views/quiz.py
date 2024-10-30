from flask import redirect, render_template, request, url_for
from flask_jwt_extended import current_user, jwt_required

from src import app
from src.constants import DEFAULT_PAGE_NUMBER, HTTP_NOT_FOUND, PER_PAGE
from src.crud.quiz import quiz_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user_answer import user_answer_crud


@app.route('/', methods=['GET'])
# Возможно можно добавить кэш для викторин
# @cache.cached(timeout=30, key_prefix='categories_view_cache')
async def quizzes() -> str:
    """Вывод страницы викторин."""
    page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
    per_page = PER_PAGE
    quizzes_paginated = quiz_crud.get_multi_query().paginate(
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
    )


@app.route('/<int:quiz_id>/refresh')
@jwt_required()
async def quiz_reload(quiz_id: int) -> str:
    """Перезагрузка викторины."""
    user_answers = await user_answer_crud.get_results_by_user_and_quiz(
        user_id=current_user.id,
        quiz_id=quiz_id,
    )
    quiz_result = await quiz_result_crud.get_by_user_and_quiz(
        user_id=current_user.id,
        quiz_id=quiz_id,
    )
    for user_answer in user_answers:
        user_answer.user_id = None
        await user_answer_crud.update_with_obj(user_answer)
    if quiz_result:
        quiz_result.user_id = None
        await quiz_result_crud.update_with_obj(quiz_result)
    return redirect(
        url_for('question',  quiz_id=quiz_id),
    )
