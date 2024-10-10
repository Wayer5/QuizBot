import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from flask import Response, abort
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    set_access_cookies,
)

from . import app
from .models import User

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> int:
    """Функция индефикатора.

    Функция обратного вызова, которая принимает любой объект,
    переданный в качестве идентификатора при создании JWTS, и преобразует
    его в сериализуемый формат JSON.

    """
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: Any, jwt_data: Any) -> Optional[User]:
    """Подгрузка пользователя.

    Функция обратного вызова,
    которая загружает пользователя из вашей базы данных всякий раз, когда
    осуществляется доступ к защищенному маршруту. Это должно возвращать любой
    объект python при успешном поиске или Нет, если поиск не удался по
    какой-либо причине (например если пользователь был удален из базы данных).

    """
    identity = jwt_data['sub']
    user = User.query.filter_by(id=identity).one_or_none()

    # Проверка на активность пользователя
    if user and not user.is_active:
        abort(401)

    return user


@app.after_request
def refresh_expiring_jwts(response: Response) -> Response:
    """Обновление токена.

    Используя обратный вызов after_request, мы обновляем любой
    токен, который находится в пределах 30 истекающих минуты.

    """
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
            logging.info('Token refreshed succesfully')
        return response
    except (RuntimeError, KeyError):
        return response
