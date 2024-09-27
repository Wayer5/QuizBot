import logging

from flask import jsonify
from flask import request
from flask_jwt_extended import (
    create_access_token,
    unset_jwt_cookies,
    set_access_cookies,
)
from flask import render_template

from . import app
from src.crud.user import user_crud


@app.route("/login", methods=["POST"])
async def login():
    """Производит выдачу токена в куки пользователя

    Keyword arguments:
    tgUsername -- имя пользователя в телеграме (после знака @)
    tgId -- айди пользователя
    Return: Строку
    """

    username = request.json.get("tgUsername", None)
    user_id = request.json.get("tgId", None)
    logging.info(f"User {username} with id {user_id} is trying to login")
    user = await user_crud.get_by_username(username)
    if user and user.telegram_id == user_id:
        access_token = create_access_token(identity=user)
        logging.info(
            f"User {username} with id {user_id} logged in successfully"
        )
        response = jsonify({"msg": "login successful"})
        set_access_cookies(response, access_token)
        return response
    else:
        logging.info(f"User {username} with id {user_id} failed to login")
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    """Удаляет токен пользователя

    Keyword arguments:
    Return: строку
    """

    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route('/', methods=['GET'])
async def index():
    return render_template('categories.html')


@app.route('/auth', methods=['GET'])
async def auntification():
    return render_template('auth.html')
