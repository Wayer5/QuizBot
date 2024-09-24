from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__)

app.config.from_object(Config)


from . import bot, api_views, admin  # noqa
