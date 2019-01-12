import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import User, Order, Customer, Role, OrderDetails, Product, Supplier, Payment, Shipper, users_schema, orders_schema, products_schema, customers_schema, order_details_schema, suppliers_schema, payments_schema, shippers_schema, MyAdminIndexView, UserAdmin, RoleAdmin
from appInit import create_app
from extensions import db

app = Flask(__name__)

app.config.from_pyfile('config_default.cfg')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
