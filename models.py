import os
from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import datetime
import random
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from appInit import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager


class User(db.model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = Admin(app)
admin.add_view(ModelView(User, db.session))


"""class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False,
                         index=True, unique=True)
    authorization = db.Column(db.String(64), unique=False, default=False)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id"""


class UserSchema(ModelSchema):
    class Meta:
        model = User


user_schema = UserSchema()


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64))
    dob = db.Column(db.String(32))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    message = db.Column(db.String(300))
    wasOrdered = db.Column(db.Boolean, unique=False, default=False)
    dateOrdered = db.Column(
        db.DateTime, server_default=func.now())
    wasFulfilled = db.Column(db.Boolean, unique=False, default=False)
    customer_ID = db.Column(db.Integer, db.ForeignKey(
        "customers.customerID"))


class OrderSchema(ModelSchema):
    class Meta:
        model = Order


orders_schema = OrderSchema(many=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    customerID = db.Column(db.Integer, primary_key=True)
    lastName = db.Column(db.String(64), index=True)
    firstName = db.Column(db.String(64), index=True)
    title = db.Column(db.String(32))
    email = db.Column(db.String(120), nullable=False, index=True)
    orders = db.relationship(
        'Order', backref=db.backref('customers', lazy=True))


class CustomerSchema(ModelSchema):
    class Meta:
        model = Customer
    orders = fields.Nested(OrderSchema, many=True)


customers_schema = CustomerSchema(many=True)
