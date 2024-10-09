from flask import Flask
from flask_migrate import Migrate
from flask_session import Session as RedisSession
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
RedisSession(app)


from . import bot, api_views, jwt, admin, models, views  # noqa
