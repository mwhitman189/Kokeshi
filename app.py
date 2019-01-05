from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_seasurf import SeaSurf
from flask_heroku import Heroku

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    APPLICATION_NAME = "Kokeshi"

    app = Flask(__name__)
    heroku = Heroku(app)
    csrf = SeaSurf(app)
    app.config.from_pyfile('config_default.cfg')

    try:
        app.config.from_envvar('KOKESHI_SETTINGS')
    except:
        print("No environment variable named 'KOKESHI_SETTINGS'")

    from models import User, Customer, Order
    from views import *

    db.init_app(app)
    migrate.init_app(app, db)

    return app
