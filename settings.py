import os

from dotenv import load_dotenv


load_dotenv('infra/.env')


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')


class Settings:
    PORT: int = int(os.getenv('PORT', 5000))
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
    WEB_URL: str = os.getenv('WEB_URL', 'http://localhost:5000')
    WEBHOOK_PATH: str = f'/bot/{TELEGRAM_TOKEN}'
    WEBHOOK_URL: str = f'{WEB_URL}{WEBHOOK_PATH}'


settings = Settings()
