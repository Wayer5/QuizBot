import logging.config

from flask import Flask
from flask_caching import Cache
from flask_migrate import Migrate
from flask_session import Session as RedisSession
from flask_sqlalchemy import SQLAlchemy

from .settings import Config, LoggingSettings

logging.config.dictConfig(LoggingSettings.logging_config())

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
RedisSession(app)
cache = Cache(app)

from .views import (  # noqa
    auth,
    category,
    image,
    pro_file,
    question,
    quiz,
    result,
)

from .models import (  # noqa
    base,
    category,
    question,
    quiz_result,
    quiz,
    quiz_question,
    telegram_user,
    user_answer,
    user,
    variant,
)

from .admin import (  # noqa
    base,
    category,
    connect,
    index,
    question,
    quiz,
    user,
)

from . import (  # noqa
    bot,
    constants,
    api_views,
    error_handlers,
    jwt_utils,
)
