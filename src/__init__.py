from MedStat_Solutions_team3.src.models import (
    Category,
    Question,
    Quiz,
    QuizResult,
    UserAnswer,
    Variant,
)
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

__all__ = [
    'Category',
    'QuizResult',
    'Question',
    'Quiz',
    'Variant',
    'UserAnswer',
]

from . import bot, api_views, admin  # noqa