import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import Customer, User, Order
from app import create_app

app = Flask(__name__)

app.config.from_pyfile('config_default.cfg')

manager = Manager(create_app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
