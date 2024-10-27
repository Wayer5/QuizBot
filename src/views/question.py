from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_jwt_extended import (
    current_user,
    jwt_required,
)

from src import app
from src.crud.question import question_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user_answer import user_answer_crud
from src.crud.variant import variant_crud
from src.utils import Dotdict, obj_to_dict


@app.route(
    '/<int:quiz_id>/',
    methods=['GET', 'POST'],
    defaults={'test': None},
)
@app.route('/<int:quiz_id>/<test>', methods=['GET', 'POST'])
@jwt_required()
def question(quiz_id: int, test: str) -> str:
    """Переключаем вопросы после ответов на них."""
    if test and session.get('test_answers') is None:
        session['test_answers'] = []

    if request.method == 'POST':
        question_id = int(request.form.get('question_id'))
        answer_id = int(request.form.get('answer'))

        # Получаем текущий вопрос по его ID
        current_question = question_crud.get(question_id)

        # Получаем выбранный ответ по его ID
        chosen_answer = variant_crud.get(answer_id)
        if test:
            # Сохраняем ответы в сессии пользователя
            temp = session['test_answers']
            temp.append(
                Dotdict(
                    {
                        'question': Dotdict(obj_to_dict(current_question)),
                        'answer': Dotdict(obj_to_dict(chosen_answer)),
                    },
                ),
            )
            session['test_answers'] = temp
        else:
            # Обновить результаты викторины
            quiz_result = quiz_result_crud.get_by_user_and_quiz(
                user_id=current_user.id,
                quiz_id=quiz_id,
            )
            if quiz_result is None:
                quiz_result = quiz_result_crud.create(
                    {
                        'user_id': current_user.id,
                        'quiz_id': quiz_id,
                        'question_id': question_id,
                        'total_questions': 0,
                        'correct_answers_count': 0,
                        'is_complete': False,
                    },
                )
            if chosen_answer.is_right_choice:
                quiz_result.correct_answers_count += 1
            quiz_result.total_questions += 1
            quiz_result.question_id = question_id
            quiz_result_crud.update_with_obj(quiz_result)
            user_answer_crud.create(
                {
                    'user_id': current_user.id,
                    'question_id': current_question.id,
                    'answer_id': chosen_answer.id,
                    'is_right': chosen_answer.is_right_choice,
                },
            )
        image_url = url_for('get_question_image', question_id=question_id)
        return render_template(
            'question_result.html',
            quiz_id=quiz_id,
            answer=chosen_answer.title,
            description=chosen_answer.description,
            user_answer=chosen_answer.is_right_choice,
            image_url=image_url if image_url else None,
            test=test,
        )
    if not test:
        # Вывод последней викторины пользователя.
        question = question_crud.get_new(
            quiz_id=quiz_id,
            user_id=current_user.id,
        )
    else:
        completed: list[int] = [
            qst.get('question').get('id')
            for qst in session.get('test_answers')
        ]
        question = question_crud.get_all_by_quiz_id(quiz_id)
        question = [qst for qst in question if qst.id not in completed]
        question = question[0] if question else None

    if question is None:
        if test:
            return redirect(url_for('results', quiz_id=quiz_id, test=True))
        quiz_result = quiz_result_crud.get_by_user_and_quiz(
            user_id=current_user.id,
            quiz_id=quiz_id,
        )
        if quiz_result is not None and not quiz_result.is_complete:
            quiz_result.is_complete = True
            quiz_result_crud.update_with_obj(quiz_result)
        return redirect(url_for('results', quiz_id=quiz_id))

    # Получаем варианты ответов
    answers = question.variants

    return render_template(
        'question.html',
        question=question,
        answers=answers,
        test=test,
    )
