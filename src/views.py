import logging

from flask import Response, jsonify, render_template, request
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)

from . import app
from src.crud.user import user_crud


@app.route('/login', methods=['POST'])
async def login() -> Response:
    """Производит выдачу токена в куки пользователя.

    Keyword Arguments:
    ------------------
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
    Return: строку.

    """
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)
    return response


@app.route('/', methods=['GET'])
async def index() -> str:
    """Вывод начальной страницы."""
    return render_template('categories.html')


@app.route('/auth', methods=['GET'])
async def auntification() -> str:
    """Вывод страницы аунтификации."""
    return render_template('auth.html')
