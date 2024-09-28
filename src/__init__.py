from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config, settings

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import bot, api_views, admin, models  # noqa