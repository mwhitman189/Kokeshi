import os
from flask import redirect, url_for
from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import datetime
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form
from flask_admin.model import BaseModelView
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, utils
from wtforms.fields import PasswordField
from extensions import db, ma


# Create a table to support a many-to-many relationship between Users and Roles
UsersRoles = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    # Our Role has three fields, ID, name and description
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# User class
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        'Role',
        secondary=UsersRoles,
        backref=db.backref('users', lazy='dynamic')
    )

    def __str__(self):
        return self.email


class MyModelView(BaseModelView):
    form_base_class = Form

    def is_accessible(self):
        if current_user.is_authenticated \
            and current_user.has_role('admin') \
                or current_user.has_role('super'):
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('showLogin'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.has_role('admin'):
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('showLogin'))


# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = ('password',)
    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)
    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    # Prevent administration of Users unless the currently logged-in user has the "admin" role

    def is_accessible(self):
        return True  # current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.

    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')


class Schema(ModelSchema):
    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=strict, **kwargs)


class UserSchema(Schema):
    class Meta:
        model = User


user_schema = UserSchema()


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64))
    dob = db.Column(db.String(32))
    height = db.Column(db.Integer())
    weight = db.Column(db.Integer())
    message = db.Column(db.String(300))
    total = db.Column(db.Integer())
    wasOrdered = db.Column(db.Boolean(), unique=False, default=False)
    dateOrdered = db.Column(
        db.DateTime, server_default=func.now())
    wasFulfilled = db.Column(db.Boolean(), unique=False, default=False)
    customer_ID = db.Column(db.Integer(), db.ForeignKey(
        "customers.customerID"))


class OrderSchema(Schema):
    class Meta:
        model = Order


orders_schema = OrderSchema(many=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    customerID = db.Column(db.Integer(), primary_key=True)
    lastName = db.Column(db.String(64), index=True)
    firstName = db.Column(db.String(64), index=True)
    title = db.Column(db.String(32))
    email = db.Column(db.String(120), nullable=False, index=True)
    orders = db.relationship(
        'Order', backref=db.backref('customers', lazy=True))


class CustomerSchema(Schema):
    class Meta:
        model = Customer
    orders = fields.Nested(OrderSchema, many=True)


customers_schema = CustomerSchema(many=True)
