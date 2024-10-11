import logging.config

from flask import Flask
from flask_caching import Cache
from flask_migrate import Migrate
from flask_session import Session as RedisSession
from flask_sqlalchemy import SQLAlchemy

from settings import Config, LoggingSettings


logging.config.dictConfig(LoggingSettings.logging_config())

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
RedisSession(app)
cache = Cache(app)


from . import (  # noqa
    bot,
    constants,
    api_views,
    jwt,
    admin,
    models,
    views,
    error_handlers,
)
