from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import datetime
import random
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, index=True, unique=True)
    is_authorized = Column(Boolean, unique=False, default=False)
    password_hash = Column(String(64))

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


class Customer(Base):
    __tablename__ = 'customer'
    customerID = Column(Integer, primary_key=True)
    lastName = Column(String(64), index=True)
    firstName = Column(String(64), index=True)
    title = Column(String(32))
    email = Column(String(120), nullable=False, index=True, unique=True)
    orderID = relationship("Order", backref="customer")

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


class Order(Base):
    __tablename__ = 'order'
    orderID = Column(Integer, primary_key=True)
    item = Column(String(64), nullable=False)
    name = Column(String(64))
    dob = Column(String(32))
    height = Column(Integer)
    weight = Column(Integer)
    message = Column(String(300))
    isOrdered = Column(Boolean, unique=False, default=False)
    dateOrdered = Column(DateTime, default=datetime.datetime.utcnow)
    customer_ID = Column(Integer, ForeignKey(
        "customer.customerID"))

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


hostname = 'localhost'
username = 'kokeshi'
password = 'kokeshi189fiend#it'
database = 'kokeshi'

engine = create_engine('postgresql+psycopg2://' +
                       username + ':' + password + '@' + hostname + '/' + database)

Base.metadata.create_all(engine)
