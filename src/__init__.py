from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_http_middleware import MiddlewareManager

from settings import Config
from .middleware import AdminTokenMiddleware

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY

app.config.from_object(Config)

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(AdminTokenMiddleware)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import bot, api_views, jwt, admin, models, views  # noqa