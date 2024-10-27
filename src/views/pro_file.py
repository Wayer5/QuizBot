from flask import (
    Response,
    render_template,
    request,
)
from flask_jwt_extended import (
    current_user,
    jwt_required,
)

from src import app, cache
from src.constants import (
    DEFAULT_PAGE_NUMBER,
    ITEMS_PER_PAGE,
)
from src.crud.question import question_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user import user_crud
from src.crud.user_answer import user_answer_crud


@app.route('/me', methods=['GET'])
@cache.cached(timeout=5)
@jwt_required()
async def profile() -> Response:
    """Отображаем профиль пользователя."""
    user = current_user
    page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
    per_page = ITEMS_PER_PAGE

    all_quiz_results = await quiz_result_crud.get_results_by_user(user.id)
    total_questions = sum(
        result.total_questions for result in all_quiz_results
    )
    correct_answers_count = sum(
        result.correct_answers_count for result in all_quiz_results
    )

    pagination = await quiz_result_crud.get_results_by_user_paginated(
        user.id,
        page,
        per_page,
    )
    quiz_results = pagination.items

    # Добавляем вопросы к каждому результату
    for result in quiz_results:
        result.questions = []
        user_answers = await user_answer_crud.get_results_by_user(user.id)

        # Получаем все вопросы по викторине
        questions = await question_crud.get_all_by_quiz_id(result.quiz_id)

        for question in questions:
            user_answer = next(
                (ua for ua in user_answers if ua.question_id == question.id),
                None,
            )
            correct_answer_text = next(
                (v.title for v in question.variants if v.is_right_choice),
                None,
            )

            # Получаем текст ответа пользователя
            user_answer_text = next(
                (
                    v.title
                    for v in question.variants
                    if v.id == (user_answer.answer_id if user_answer else None)
                ),
                'Не отвечено',
            )

            result.questions.append(
                {
                    # Текст вопроса
                    'title': question.title,
                    # Текст ответа
                    'user_answer': user_answer_text,
                    # Правильный ответ
                    'correct_answer': correct_answer_text,
                    # Пояснение
                    'explanation': question.explanation
                    if hasattr(question, 'explanation')
                    else None,
                },
            )

    return render_template(
        'user_profile.html',
        user=user,
        quiz_results=quiz_results,
        total_questions=total_questions,
        correct_answers_count=correct_answers_count,
        pagination=pagination,
    )


@app.route('/me', methods=['POST'])
@jwt_required()
async def delete_profile() -> Response:
    """Удаляет профиль пользователя, сохраняя результаты викторин."""
    user = current_user
    quiz_results = await quiz_result_crud.get_results_by_user(user.id)

    # Обновляем результаты викторин, чтобы убрать связь с пользователем
    for result in quiz_results:
        result.user_id = None
        await user_crud.update(result, {'user_id': None})

    user_answers = await user_answer_crud.get_results_by_user(user.id)

    # Обновляем ответы пользователя, убирая связь с таблицей пользователи
    for answer in user_answers:
        answer.user_id = None
        await user_crud.update(answer, {'user_id': None})

    if cache.has(f'user_{user.id}'):
        cache.delete(f'user_{user.id}')
    await user_crud.remove(current_user)

    return 'Профиль удален', 204
