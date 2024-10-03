import logging

from flask import (
    Response,
    jsonify,
    render_template,
    request,
)
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from . import app
from src.crud.category import category_crud
from src.crud.quiz import quiz_crud
from src.crud.user import user_crud
from src.models import QuizResult


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
    user = await user_crud.get_by_username(username)
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
    user = current_user
    quiz_results = QuizResult.query.filter_by(user_id=user.id).all()
    # Обновляем результаты викторин, чтобы убрать связь с пользователем
    for result in quiz_results:
        result.user_id = None
        user_crud.update(result, {'user_id': None})

    user_crud.remove(user)
    return render_template('categories.html')
