import logging

from flask import (
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from sqlalchemy.sql.expression import true

from . import app
from .models import Question, QuizResult, Variant
from src.crud.category import category_crud
from src.crud.quiz import quiz_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user import user_crud
from src.models import QuizResult
from src.crud.user_answer import user_answer_crud


@app.route('/login', methods=['POST'])
async def login() -> Response:
    """Производит выдачу токена в куки пользователя.

    Keyword Arguments:
    -----------------
    tgUsername -- имя пользователя в телеграме (после знака @).
    tgId -- айди пользователя.
    Return: Строку.

    """
    username = request.json.get('tgUsername', None)
    user_id = request.json.get('tgId', None)
    logging.info(f'User {username} with id {user_id} is trying to login')
    user = await user_crud.get_by_telegram_id(user_id)
    if user and user.telegram_id == user_id and user.is_active:
        access_token = create_access_token(identity=user)
        logging.info(
            f'User {username} with id {user_id} logged in successfully',
        )
        response = jsonify({'msg': 'login successful'})
        set_access_cookies(response, access_token)
        return response
    logging.info(f'User {username} with id {user_id} failed to login')
    return jsonify({'msg': 'Bad username or password'}), 401


@app.route('/logout', methods=['POST'])
def logout() -> Response:
    """Удаляет токен пользователя.

    Keyword Arguments:
    -----------------
    Return: строку.

    """
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)
    return response


@app.route('/auth', methods=['GET'])
async def auntification() -> str:
    """Вывод страницы аунтификации."""
    return render_template('auth.html')


@app.route('/', methods=['GET'])
async def categories() -> str:
    """Вывод страницы категорий."""
    categories = category_crud.get_multi()
    return render_template('categories.html', categories=categories)


@app.route('/<int:category_id>/', methods=['GET'])
async def quizzes(category_id: int) -> str:
    """Вывод страницы викторин."""
    quizzes = quiz_crud.get_by_category_id(category_id)
    return render_template('quizzes.html', quizzes=quizzes)


@app.route('/me', methods=['GET'])
@jwt_required()
def profile() -> Response:
    """Отображаем профиль пользователя."""
    user = current_user
    quiz_results = QuizResult.query.filter_by(user_id=user.id).all()

    total_questions = sum(result.total_questions for result in quiz_results)
    correct_answers_count = sum(
        result.correct_answers_count for result in quiz_results)

    return render_template('user_profile.html',
                           user=user,
                           quiz_results=quiz_results,
                           total_questions=total_questions,
                           correct_answers_count=correct_answers_count)


@app.route('/me', methods=['POST'])
@jwt_required()
def delete_profile() -> Response:
    """Удаляет профиль пользователя и сохраняет результаты викторин."""
    # user = current_user
    # quiz_results = QuizResult.query.filter_by(user_id=user.id).all()
    # Обновляем результаты викторин, чтобы убрать связь с пользователем
    # for result in quiz_results:
    #     result.user_id = None
    #     user_crud.update(result, {'user_id': None})

    user_crud.remove(current_user)
    return render_template('categories.html')


@app.route('/me', methods=['GET'])
@jwt_required()
def profile() -> Response:
    """Отображаем профиль пользователя."""
    user = current_user
    quiz_results = QuizResult.query.filter_by(user_id=user.id).all()

    total_questions = sum(result.total_questions for result in quiz_results)
    correct_answers_count = sum(
        result.correct_answers_count for result in quiz_results)

    return render_template('user_profile.html',
                           user=user,
                           quiz_results=quiz_results,
                           total_questions=total_questions,
                           correct_answers_count=correct_answers_count)


@app.route('/me', methods=['POST'])
@jwt_required()
def delete_profile() -> Response:
    """Удаляет профиль пользователя и сохраняет результаты викторин."""
    # user = current_user
    # quiz_results = QuizResult.query.filter_by(user_id=user.id).all()
    # Обновляем результаты викторин, чтобы убрать связь с пользователем
    # for result in quiz_results:
    #     result.user_id = None
    #     user_crud.update(result, {'user_id': None})

    user_crud.remove(current_user)
    return render_template('categories.html')


@app.route('/<int:category_id>/<int:quiz_id>/', methods=['GET'])
@jwt_required()
async def next_question(category_id: int, quiz_id: int) -> str:
    """Вывод последней викторины пользователя."""
    quiz_result = QuizResult.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
    ).first()
    if quiz_result is None:
        # Получаем первый вопрос викторины
        question = (
            Question.query.filter(
                Question.quiz_id == quiz_id,
                Question.is_active == true(),
            )
            .order_by(Question.id)
            .first()
        )
    else:
        # Если результат викторины существует,
        # то получаем последний доступный вопрос
        last_question_id = quiz_result.question_id
        question = Question.query.filter(
            Question.quiz_id == quiz_id,
            Question.id > last_question_id,
            Question.is_active == true(),
        ).first()

    if question is None:
        quiz_result.is_complete = True
        quiz_result_crud.update_with_obj(quiz_result)
        return redirect(url_for('results'))

    return redirect(
        url_for(
            'question',
            category_id=category_id,
            quiz_id=quiz_id,
            question_id=question.id,
        ),
    )


@app.route(
    '/<int:category_id>/<int:quiz_id>/<int:question_id>',
    methods=['GET', 'POST'],
)
@jwt_required()
async def question(category_id: int, quiz_id: int, question_id: int) -> str:
    """Переключаем вопросы после ответов на них."""
    if request.method == 'POST':
        answer_id = int(
            request.form.get('answer'),
        )  # получить идентификатор выбранного ответа

        # Получаем текущий вопрос по его ID
        current_question = Question.query.get_or_404(question_id)

        # Получаем выбранный ответ по его ID
        chosen_answer = Variant.query.get_or_404(answer_id)

        # Обновить результаты викторины
        quiz_result = QuizResult.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id,
        ).first()

        if quiz_result and quiz_result.question_id == question_id:
            redirect(url_for('quizzes', category_id=category_id))
        if quiz_result is None:
            quiz_result = quiz_result_crud.create(
                {
                    'user_id': current_user.id,
                    'quiz_id': quiz_id,
                    'question_id': question_id,
                    'total_questions': len(
                        Question.query.filter_by(quiz_id=quiz_id).all(),
                    ),
                    'correct_answers_count': 0,
                    'is_complete': False,
                },
            )
        if chosen_answer.is_right_choice:
            quiz_result.correct_answers_count += 1
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

        return render_template(
            'question_result.html',
            category_id=category_id,
            quiz_id=current_question.quiz_id,
            answer=chosen_answer.title,
            description=chosen_answer.description,
            user_answer=chosen_answer.is_right_choice,
        )

    # Получаем идентификатор текущего вопроса из URL
    current_question = Question.query.get_or_404(question_id)

    # Получаем все вопросы для текущей викторины
    questions = (
        Question.query.filter_by(
            quiz_id=current_question.quiz_id,
        )
        .order_by(
            Question.id,
        )
        .all()
    )

    # Находим индекс текущего вопроса в списке вопросов
    current_index = questions.index(current_question)

    # Находим предыдущий вопрос, если есть
    prev_question = questions[current_index - 1] if current_index > 0 else None

    # Получаем варианты ответов
    answers = current_question.variants

    return render_template(
        'question.html',
        question=current_question,
        answers=answers,
        prev_question=prev_question,
    )


@app.route('/results')
def results() -> Response:
    """Пишем о том, что тест закончен."""
    return 'Тест завершен! Спасибо за участие.'
