from datetime import timedelta
from os import getenv as get

from dotenv import load_dotenv

load_dotenv()


class Config(object):

    """Конфиг flask."""

    SQLALCHEMY_DATABASE_URI: str = (
        'postgresql://'
        f'{get("POSTGRES_USER")}:'
        f'{get("POSTGRES_PASSWORD")}@'
        f'{get("DB_HOST")}:5432/{get("POSTGRES_DB")}'
    )
    SECRET_KEY: str = get('SECRET_KEY', 'secret')
    JWT_SECRET_KEY: str = get('JWT_SECRET_KEY', 'secret')
    # Отключаем csrf в одном модуле
    # Используем его из другого
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_CSRF_IN_COOKIES = True
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class Settings:

    """Настройки приложения."""

    PORT: int = int(get('PORT', 5000))
    TELEGRAM_TOKEN: str = get('TELEGRAM_TOKEN')
    WEB_URL: str = get('WEB_URL', 'http://localhost:5000')
    WEBHOOK_PATH: str = f'/bot/{TELEGRAM_TOKEN}'
    WEBHOOK_URL: str = f'{WEB_URL}{WEBHOOK_PATH}'
    SECRET_KEY: str = get('SECRET_KEY')


settings = Settings()
