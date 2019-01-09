import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import User, Order, Customer, Role, user_schema, orders_schema, customers_schema, MyAdminIndexView, UserAdmin, RoleAdmin
from appInit import create_app
from extensions import db

app = Flask(__name__)

app.config.from_pyfile('config_default.cfg')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
