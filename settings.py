from os import getenv as get

from dotenv import load_dotenv


load_dotenv()


class Config(object):
    SQLALCHEMY_DATABASE_URI: str = (
        'postgresql://'
        f'{get("POSTGRES_USER")}:'
        f'{get("POSTGRES_PASSWORD")}@'
        f'{get("DB_HOST")}:5432/{get("POSTGRES_DB")}'
    )
    SECRET_KEY: str = get('SECRET_KEY')


class Settings:
    PORT: int = int(get('PORT', 5000))
    TELEGRAM_TOKEN: str = get('TELEGRAM_TOKEN')
    WEB_URL: str = get('WEB_URL', 'http://localhost:5000')
    WEBHOOK_PATH: str = f'/bot/{TELEGRAM_TOKEN}'
    WEBHOOK_URL: str = f'{WEB_URL}{WEBHOOK_PATH}'


settings = Settings()
