from flask import (
    render_template,
    session,
    url_for,
)
from flask_jwt_extended import (
    current_user,
    jwt_required,
)

from src import app
from src.crud.question import question_crud
from src.crud.quiz import quiz_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user_answer import user_answer_crud
from src.utils import Dotdict, obj_to_dict


@app.route(
    '/results/<int:quiz_id>/',
    defaults={'test': False},
)
@app.route('/results/<int:quiz_id>/<test>')
@jwt_required()
async def results(quiz_id: int, test: str) -> str:
    """Результаты викторины."""
    user = current_user

    if not test:
        # Получаем результат викторины для конкретного пользователя и викторины
        quiz_result = await quiz_result_crud.get_by_user_and_quiz(
            user.id,
            quiz_id,
        )
    else:
        test_answers = obj_to_dict(session.get('test_answers', []))
        session['test_answers'] = []
        correct_answers = sum(
            1
            for answer in test_answers
            if answer.get('answer').get('is_right_choice')
        )
        total_questions = len(test_answers)
        quiz_result = Dotdict(
            {
                'user_id': user.id,
                'quiz_id': quiz_id,
                'total_questions': total_questions,
                'correct_answers_count': correct_answers,
                'all_questions': [qr.question for qr in test_answers],
                'user_answers': [qr.answer for qr in test_answers],
            },
        )

    if not quiz_result:
        return 'Результаты викторины не найдены', 404

    # Получаем название викторины
    quiz = await quiz_crud.get_by_id(quiz_id)
    quiz_title = quiz.title if quiz else 'Неизвестная викторина'

    # Считаем общее количество вопросов и количество правильных ответов
    total_questions = quiz_result.total_questions
    correct_answers_count = quiz_result.correct_answers_count

    # Добавляем вопросы к результату
    quiz_result.questions = []
    if not test:
        user_answers = await user_answer_crud.get_results_by_user_and_quiz(
            user.id,
            quiz_id,
        )
        # Получаем все вопросы по викторине
        questions = await question_crud.get_all_by_quiz_id(quiz_result.quiz_id)
    else:
        user_answers = quiz_result.get('user_answers')
        questions = quiz_result.get('all_questions')

    for question in questions:
        user_answer = next(
            (ua for ua in user_answers if ua.question_id == question.id),
            None,
        )
        # Найдем правильный вариант ответа
        correct_variant = next(
            (v for v in question.variants if v.is_right_choice),
            None,
        )
        # Получаем текст ответа пользователя
        # Так как из сессии получаем модель variant
        # а тут из модели user_answer
        # то условие будет разным
        user_answer = (
            user_answer
            if test
            else next(
                (
                    v
                    for v in question.variants
                    if v.id == user_answer.answer_id
                ),
                None,
            )
        )
        # Собираем все возможные ответы
        possible_answers = [v.title for v in question.variants]
        image_url = url_for('get_question_image', question_id=question.id)
        quiz_result.questions.append(
            {
                'title': question.title,
                'user_answer': user_answer.title,
                'correct_answer': (
                    correct_variant.title if correct_variant else None
                ),
                'possible_answers': possible_answers,
                # Описание правильного ответа
                'correct_description': correct_variant.description
                if correct_variant
                else None,
                'image_url': image_url if image_url else None,
            },
        )

    return render_template(
        'full_results.html',
        user=user,
        quiz_results=[quiz_result],
        total_questions=total_questions,
        correct_answers_count=correct_answers_count,
        quiz_title=quiz_title,
        test=test,
    )
