from flask import Flask, session
from flask_http_middleware import MiddlewareManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session as RedisSession

from settings import Config

from .middleware import AdminTokenMiddleware

app = Flask(__name__)

app.config.from_object(Config)

app.wsgi_app = MiddlewareManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
RedisSession(app)


from . import bot, api_views, jwt, admin, models, views  # noqa
