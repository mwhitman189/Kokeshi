from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_heroku import Heroku
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
ma = Marshmallow()
login_manager = LoginManager()
heroku = Heroku()
mail = Mail()
