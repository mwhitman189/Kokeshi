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
        if current_user.is_authenticated and current_user.has_role('super'):
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


users_schema = UserSchema(many=True)


class KokeshiDetails(db.Model):
    __tablename__ = 'kokeshi_details'
    kokeshiDetailsID = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64))
    dob = db.Column(db.String(32))
    height = db.Column(db.Integer())
    weight = db.Column(db.Integer())
    message = db.Column(db.String(300))
    is_message = db.Column(db.Boolean(), default=False)
    product_ID = db.Column(db.Integer(), db.ForeignKey(
        "products.productID"))


class KokeshiDetailsSchema(Schema):
    class Meta:
        model = KokeshiDetails


kokeshi_details_schema = KokeshiDetailsSchema(many=True)


class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    orderDetailsID = db.Column(db.Integer(), primary_key=True)
    total = db.Column(db.Integer())
    product_ID = db.Column(db.Integer(), db.ForeignKey(
        "products.productID"))
    kokeshi_details_ID = db.Column(db.Integer(), db.ForeignKey(
        "kokeshi_details.kokeshiDetailsID"))
    order_ID = db.Column(db.Integer(), db.ForeignKey(
        "orders.orderID"))


class OrderDetailsSchema(Schema):
    class Meta:
        model = OrderDetails
    kokeshi_details = fields.Nested(KokeshiDetailsSchema, many=True)


order_details_schema = OrderDetailsSchema(many=True)


class Product(db.Model):
    __tablename__ = 'products'
    productID = db.Column(db.Integer(), primary_key=True)
    productName = db.Column(db.String(64), index=True)
    productDescription = db.Column(db.String(120))
    price = db.Column(db.Integer())
    is_available = db.Column(db.Boolean(), default=True)
    order_details = db.relationship(
        'OrderDetails', backref=db.backref('products', lazy=True))
    supplier_ID = db.Column(
        db.Integer(), db.ForeignKey("suppliers.supplierID"))


class ProductSchema(Schema):
    class Meta:
        model = Product


products_schema = ProductSchema(many=True)


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    supplierID = db.Column(db.Integer(), primary_key=True)
    supplierName = db.Column(db.String(128), index=True)
    supplierPhone = db.Column(db.Integer(), nullable=False)
    supplierEmail = db.Column(db.String(255))
    supplier = db.relationship(
        'Product', backref=db.backref('suppliers', lazy=True))


class SupplierSchema(Schema):
    class Meta:
        model = Supplier


suppliers_schema = ProductSchema(many=True)


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer(), primary_key=True)
    wasOrdered = db.Column(db.Boolean(), unique=False, default=False)
    dateOrdered = db.Column(
        db.DateTime, server_default=func.now())
    wasFulfilled = db.Column(db.Boolean(), unique=False, default=False)
    customer_ID = db.Column(db.Integer(), db.ForeignKey(
        "customers.customerID"))
    payment_ID = db.Column(db.Integer(), db.ForeignKey(
        "payments.paymentID"))
    shipper_ID = db.Column(db.Integer(), db.ForeignKey("shippers.shipperID"))
    order_details = db.relationship(
        'OrderDetails', backref=db.backref('order_details', lazy=True))


class OrderSchema(Schema):
    class Meta:
        model = Order
    order_details = fields.Nested(OrderDetailsSchema, many=True)


orders_schema = OrderSchema(many=True)


class Payment(db.Model):
    __tablename__ = 'payments'
    paymentID = db.Column(db.Integer(), primary_key=True)
    paymentType = db.Column(db.String())
    orders = db.relationship(
        'Order', backref=db.backref('payments', lazy=True))


class PaymentSchema(Schema):
    class Meta:
        model = Payment


payments_schema = PaymentSchema(many=True)


class Shipper(db.Model):
    __tablename__ = 'shippers'
    shipperID = db.Column(db.Integer(), primary_key=True)
    company = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.Integer(), nullable=False)
    email = db.Column(db.String(255))
    contactName = db.Column(db.String(64))
    orders = db.relationship(
        'Order', backref=db.backref('shippers', lazy=True))


class ShipperSchema(Schema):
    class Meta:
        model = Shipper


shippers_schema = ShipperSchema(many=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    customerID = db.Column(db.Integer(), primary_key=True)
    lastName = db.Column(db.String(64), index=True)
    firstName = db.Column(db.String(64), index=True)
    title = db.Column(db.String(32))
    email = db.Column(db.String(255), nullable=False, index=True)
    shipAddress = db.Column(db.String(120), nullable=False)
    building = db.Column(db.String(64))
    address1 = db.Column(db.String(64))
    address2 = db.Column(db.String(64))
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(32), nullable=False)
    postalCode = db.Column(db.Integer(), nullable=False)
    orders = db.relationship(
        'Order', backref=db.backref('customers', lazy=True))


class CustomerSchema(Schema):
    class Meta:
        model = Customer
    orders = fields.Nested(OrderSchema, many=True)


customers_schema = CustomerSchema(many=True)
