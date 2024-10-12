import logging
import os
from datetime import datetime, timedelta
from os import getenv as get

from dotenv import load_dotenv
from redis.client import Redis

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
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(
        host=get('REDIS_HOST'),
        port=6379,
        db=0,
        username=get('REDIS_USER'),
        password=get('REDIS_USER_PASSWORD'),
    )
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=3)
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = (
        f'redis://'
        f'{get("REDIS_USER")}:'
        f'{get("REDIS_USER_PASSWORD")}@'
        f'{get("REDIS_HOST")}:6379/2'
    )
    try:
        info = SESSION_REDIS.info()
        logging.info(info['redis_version'])
        response = SESSION_REDIS.ping()
        if response:
            logging.info('Подключение успешно!')
            logging.inf0(response)
        else:
            logging.info('Не удалось подключиться к Redis.')
    except Exception as e:
        logging.info(f'Ошибка: {e}')


class Settings:

    """Настройки приложения."""

    PORT: int = int(get('PORT', 5000))
    TELEGRAM_TOKEN: str = get('TELEGRAM_TOKEN')
    WEB_URL: str = get('WEB_URL', 'http://localhost:5000')
    WEBHOOK_PATH: str = f'/bot/{TELEGRAM_TOKEN}'
    WEBHOOK_URL: str = f'{WEB_URL}{WEBHOOK_PATH}'
    SECRET_KEY: str = get('SECRET_KEY')


class LoggingSettings:

    """Настройки логирования."""

    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOGGING_MAX_FILE_SIZE = 1024 * 1024 * 10  # 10MB
    LOGGING_BACKUP_COUNT = 5

    @classmethod
    def logging_dir_path(cls) -> str:
        """Путь к директории логов."""
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir

    @classmethod
    def logging_file_path(cls) -> str:
        """Путь к файлу логов."""
        log_file_name = datetime.now().strftime(('%Y-%m-%d')) + '_.log'
        return f'{cls.logging_dir_path()}/{log_file_name}'

    @classmethod
    def logging_config(cls) -> dict:
        """Конфигурация логирования."""
        return {
            'version': 1,
            'formatters': {
                'default': {
                    'format': cls.LOGGING_FORMAT,
                    'datefmt': cls.LOGGING_DATE_FORMAT,
                },
            },
            'handlers': {
                'all_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': cls.logging_file_path(),
                    'maxBytes': cls.LOGGING_MAX_FILE_SIZE,
                    'backupCount': cls.LOGGING_BACKUP_COUNT,
                    'formatter': 'default',
                    'level': logging.DEBUG,
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'level': logging.INFO,
                },
            },
            'root': {
                'level': logging.DEBUG,
                'handlers': ['all_file', 'console'],
            },
        }


settings = Settings()
