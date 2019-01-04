import os
from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import datetime
import random
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(64), nullable=False, index=True, unique=True)
    is_authorized = Column(db.Boolean, unique=False, default=False)
    password_hash = Column(db.String(64))

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
        return user_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'username': self.username,
            'picture': self.picture,
            'email': self.email,
        }


class Customer(db.Model):
    __tablename__ = 'customer'
    customerID = Column(db.Integer, primary_key=True)
    lastName = Column(db.String(64), index=True)
    firstName = Column(db.String(64), index=True)
    title = Column(db.String(32))
    email = Column(db.String(120), nullable=False, index=True, unique=True)
    orderID = db.relationship(
        'Order', backref=db.backref('customer', lazy=True))

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'customerID': self.customerID,
            'lastName': self.lastName,
            'firstName': self.firstName,
            'title': self.title,
            'email': self.email,
            'orderID': self.orderID
        }


class Order(db.Model):
    __tablename__ = 'order'
    orderID = Column(db.Integer, primary_key=True)
    item = Column(db.String(64), nullable=False)
    name = Column(db.String(64))
    dob = Column(db.String(32))
    height = Column(db.Integer)
    weight = Column(db.Integer)
    message = Column(db.String(300))
    isOrdered = Column(db.Boolean, unique=False, default=False)
    dateOrdered = Column(DateTime, default=datetime.datetime.utcnow)
    customer_ID = Column(db.Integer, db.ForeignKey(
        "customer.customerID"), nullable=False)

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'orderID': self.orderID,
            'item': self.item,
            'name': self.name,
            'dob': self.dob,
            'height': self.height,
            'weight': self.weight,
            'message': self.message,
            'isOrdered': self.isOrdered,
            'dateOrdered': self.dateOrdered,
            'customer_ID': self.customer_ID
        }
