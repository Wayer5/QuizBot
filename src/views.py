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
    set_access_cookies,
    unset_jwt_cookies,
)

from . import app
from .models import Question
from src.crud.category import category_crud
from src.crud.quiz import quiz_crud
from src.crud.user import user_crud


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
    if user and user.telegram_id == user_id:
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


@app.route('/quizzes', methods=['GET'])
async def quizzes() -> str:
    """Вывод страницы викторин."""
    category_id = request.args.get('category_id', type=int)
    if category_id:
        quizzes = quiz_crud.get_by_category_id(category_id)
    else:
        quizzes = quiz_crud.get_multi()
    return render_template('quizzes.html', quizzes=quizzes)


@app.route('/question', methods=['GET', 'POST'])
def question() -> Response:
    """Переключаем вопросы после ответов на них."""
    if request.method == 'POST':
        question_id = int(request.form.get('question_id'))
        answer = request.form.get('answer')

        # Обработка ответа
        print(f'Ответ на вопрос {question_id}: {answer}')

        # Получаем текущий вопрос по его ID
        current_question = Question.query.get_or_404(question_id)

        # Переход к следующему вопросу той же викторины
        next_question = (
            Question.query.filter(
                Question.quiz_id == current_question.quiz_id,
                Question.id > current_question.id,
            )
            .order_by(Question.id)
            .first()
        )

        if next_question:
            return redirect(
                url_for(
                    'question',
                    question_id=next_question.id,
                    quiz_id=current_question.quiz_id,
                ),
            )
        return redirect(url_for('results'))

    # Получаем идентификатор текущего вопроса из URL
    question_id = int(request.args.get('question_id', 1))
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
