from datetime import datetime
from typing import Optional, Union

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
from src.models.question import Question as QuestionModel
from src.utils import Dotdict, obj_to_dict


@app.route(
    '/<int:category_id>/<int:quiz_id>/',
    methods=['GET', 'POST'],
    defaults={'test': None},
)
@app.route('/<int:category_id>/<int:quiz_id>/<test>', methods=['GET', 'POST'])
@jwt_required()
async def question(
    category_id: int, quiz_id: int, test: Optional[str] = None,
) -> str:
    """Обрабатывает запросы к странице с вопросами викторины.

    Args:
    ----
        category_id (int): ID категории викторины.
        quiz_id (int): ID викторины.
        test (Optional[str], optional): Флаг тестового режима.
        Если присутствует, результаты викторины не сохраняются.

    Returns:
    -------
        str: HTML-код страницы с вопросом или результатами.

    """
    if request.method == 'POST':
        return await handle_question_post(category_id, quiz_id, test)

    # GET request logic
    return await handle_question_get(category_id, quiz_id, test)


async def handle_question_post(
    category_id: int, quiz_id: int, test: Optional[str] = None,
) -> str:
    """Обрабатывает POST-запросы к странице с вопросами.

    Получает ответ пользователя, проверяет его и перенаправляет
    на страницу с результатами.

    Args:
    ----
        category_id (int): ID категории викторины.
        quiz_id (int): ID викторины.
        test (Optional[str], optional): Флаг тестового режима.

    Returns:
    -------
        str: HTML-код страницы с результатами ответа.

    """
    question_id = int(request.form.get('question_id'))
    answer_id = int(request.form.get('answer'))

    current_question = await question_crud.get(question_id)
    chosen_answer = await variant_crud.get(answer_id)

    if test:
        # Сохраняем ответы в сессии пользователя
        session['test_answers'] = session.get('test_answers', []) + [
            Dotdict(
                {
                    'question': Dotdict(obj_to_dict(current_question)),
                    'answer': Dotdict(obj_to_dict(chosen_answer)),
                },
            ),
        ]
    else:
        await update_quiz_results(
            current_user.id,
            quiz_id,
            question_id,
            chosen_answer.is_right_choice,
        )
        await save_user_answer(
            current_user.id,
            current_question.id,
            chosen_answer.id,
            chosen_answer.is_right_choice,
        )

    image_url = url_for('get_question_image', question_id=question_id)
    return render_template(
        'question_result.html',
        category_id=category_id,
        quiz_id=quiz_id,
        answer=chosen_answer.title,
        description=chosen_answer.description,
        user_answer=chosen_answer.is_right_choice,
        image_url=image_url if image_url else None,
        test=test,
    )


async def handle_question_get(
    category_id: int, quiz_id: int, test: Optional[str] = None,
) -> Union[str, redirect]:
    """Обрабатывает GET-запросы к странице с вопросами.

    Отображает следующий неотвеченный вопрос викторины.

    Args:
    ----
        category_id (int): ID категории викторины.
        quiz_id (int): ID викторины.
        test (Optional[str], optional): Флаг тестового режима.

    Returns:
    -------
        Union[str, redirect]: HTML-код страницы с вопросом или перенаправление
            на страницу результатов, если все вопросы отвечены.

    """
    if test:
        completed = [
            qst.get('question').get('id')
            for qst in session.get('test_answers', [])
        ]
        question: Optional[QuestionModel] = next(
            (
                qst
                for qst in await question_crud.get_all_by_quiz_id(quiz_id)
                if qst.id not in completed
            ),
            None,
        )
    else:
        question: Optional[QuestionModel] = await question_crud.get_new(
            quiz_id=quiz_id, user_id=current_user.id,
        )

    if question is None:
        return await handle_quiz_end(quiz_id, test)

    answers = question.variants
    return render_template(
        'question.html',
        question=question,
        answers=answers,
        test=test,
    )


async def update_quiz_results(
    user_id: int, quiz_id: int, question_id: int, is_correct_answer: bool,
) -> None:
    """Обновляет результаты викторины для пользователя.

    Args:
    ----
        user_id (int): ID пользователя.
        quiz_id (int): ID викторины.
        question_id (int): ID вопроса.
        is_correct_answer (bool): Флаг, указывающий, был ли ответ
            на вопрос верным.

    """
    quiz_result = await quiz_result_crud.get_by_user_and_quiz(
        user_id=user_id, quiz_id=quiz_id,
    )
    if quiz_result is None:
        quiz_result = await quiz_result_crud.create(
            {
                'user_id': user_id,
                'quiz_id': quiz_id,
                'total_questions': 0,
                'correct_answers_count': 0,
                'is_complete': False,
            },
        )
    quiz_result.total_questions += 1
    if is_correct_answer:
        quiz_result.correct_answers_count += 1
    await quiz_result_crud.update_with_obj(quiz_result)


async def save_user_answer(
    user_id: int, question_id: int, answer_id: int, is_right: bool,
) -> None:
    """Сохраняет ответ пользователя в базе данных.

    Args:
    ----
        user_id (int): ID пользователя.
        question_id (int): ID вопроса.
        answer_id (int): ID выбранного ответа.
        is_right (bool): Флаг, указывающий, был ли ответ верным.

    """
    await user_answer_crud.create(
        {
            'user_id': user_id,
            'question_id': question_id,
            'answer_id': answer_id,
            'is_right': is_right,
        },
    )


async def handle_quiz_end(
    quiz_id: int, test: Optional[str] = None,
) -> redirect:
    """Обрабатывает завершение викторины.

    Перенаправляет пользователя на страницу с результатами.

    Args:
    ----
        quiz_id (int): ID викторины.
        test (Optional[str], optional): Флаг тестового режима.

    Returns:
    -------
        redirect: Перенаправление на страницу с результатами.

    """
    if test:
        return redirect(url_for('results', quiz_id=quiz_id, test=True))

    quiz_result = await quiz_result_crud.get_by_user_and_quiz(
        user_id=current_user.id, quiz_id=quiz_id,
    )
    if quiz_result is not None and not quiz_result.is_complete:
        quiz_result.is_complete = True
        quiz_result.ended_on = datetime.utcnow()
        print(quiz_result.ended_on)
        await quiz_result_crud.update_with_obj(quiz_result)
    return redirect(url_for('results', quiz_id=quiz_id))
