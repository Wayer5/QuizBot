from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from MedStat_Solutions_team3.settings import Config

from MedStat_Solutions_team3.src.models import (
    Category,
    QuizResult,
    Question,
    Quiz,
    Variant,
    UserAnswer
)


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
