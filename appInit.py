from extensions import db, migrate, csrf, ma, heroku, login_manager


def create_app():

    import os
    from os import environ
    import psycopg2
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from flask_heroku import Heroku
    from flask_admin.contrib.sqla import ModelView
    from flask_wtf.csrf import CSRFProtect
    from flask_security import login_required
    from flask import render_template, request, redirect, jsonify, url_for, flash, session
    from sqlalchemy.orm import relationship, sessionmaker
    from flask_sqlalchemy import SQLAlchemy
    from models import User, Order, Customer, Role, KokeshiDetails, OrderDetails, Product, Supplier, Payment, Shipper, users_schema, orders_schema, products_schema, customers_schema, kokeshi_details_schema, order_details_schema, suppliers_schema, payments_schema, shippers_schema, MyAdminIndexView, UserAdmin, RoleAdmin
    from flask_admin import Admin
    from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
    from flask_security import SQLAlchemyUserDatastore, Security, utils
    from wtforms.fields import PasswordField
    from passlib.hash import pbkdf2_sha256
    from flask_marshmallow import Marshmallow

    APPLICATION_NAME = "Kokeshi"

    app = Flask(__name__)
    csrf.init_app(app)
    app.config.from_pyfile('config_default.cfg')

    try:
        app.config.from_envvar('KOKESHI_SETTINGS')
    except:
        pass
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = '$2b$12$1pO0bbJOrozMPSKdzOB6a.'
    app.config['SECURITY_REGISTERABLE'] = True

    admin = Admin(app, index_view=MyAdminIndexView())
    # Initialize the SQLAlchemy data store and Flask-Security.
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))

    #######################
    # User administration #
    #######################

    @app.before_first_request
    def before_first_request():
        db.create_all()
        user_datastore.find_or_create_role(
            name='super', description='Super User')
        user_datastore.find_or_create_role(
            name='admin', description='Administrator')
        user_datastore.find_or_create_role(
            name='artisan', description='Artisan')

        encrypted_password = utils.encrypt_password('password')

        if not user_datastore.get_user('super@example.com'):
            user_datastore.create_user(
                email='super@example.com',
                password=encrypted_password
            )
        if not user_datastore.get_user('admin@example.com'):
            user_datastore.create_user(
                email='admin@example.com',
                password=encrypted_password
            )
        if not user_datastore.get_user('artisan@example.com'):
            user_datastore.create_user(
                email='artisan@example.com',
                password=encrypted_password
            )

        db.session.commit()

        user_datastore.add_role_to_user('super@example.com', 'super')
        user_datastore.add_role_to_user('admin@example.com', 'admin')
        user_datastore.add_role_to_user('artisan@example.com', 'artisan')
        db.session.commit()

    @app.route('/login', methods=['GET', 'POST'])
    def showLogin():
        # Here we use a class of some kind to represent and validate our
        # client-side form data. For example, WTForms is a library that will
        # handle this for us, and we use a custom LoginForm to validate.
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(user)

            flask.flash('Logged in successfully.')

            next = flask.request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return flask.redirect(next or flask.url_for('index'))
        return flask.render_template('login.html', form=form)

    @app.route('/logout')
    def showLogout():
        logout_user()

        flask.flash('Logged out successfully.')

        return 'Logged out'

    ##########################
    # General Administration #
    ##########################

    @app.before_request
    def force_https():
        if os.environ.get('DATABASE_URL') is not None:
            if not request.is_secure:
                url = request.url.replace('http://', 'https://', 1)
                code = 301
                return redirect(url, code=code)

    ##################
    # JSON API calls #
    ##################

    @app.route('/orders/JSON/')
    @login_required
    def showOrdersJSON():
        """
        Return order data in JSON
        """
        orders = Order.query.all()
        return jsonify(orders_schema.dump(orders).data)

    @app.route('/orders/unfulfilled/JSON/')
    @login_required
    def showUnfulfilledOrdersJSON():
        """
        Return unfulfilled order data in JSON
        """
        unful_orders = Order.query.filter_by(wasOrdered=False).all()

        return jsonify(orders_schema.dump(unful_orders).data)

    @app.route('/customers/JSON/')
    @login_required
    def showCustomersJSON():
        """
        Return customer data in JSON
        """
        customers = Customer.query.all()

        return jsonify(customers_schema.dump(customers).data)

    #######################
    # Client facing pages #
    #######################

    @app.route('/')
    @app.route('/home/')
    def showHome():
        """
        Display the landing page.
        """
        return render_template('home.html')

    @app.route('/about/')
    def showAboutPage():
        """
        Display the About Us page.
        """
        return render_template('about.html')

    @app.route('/design/', methods=['GET', 'POST'])
    def showDesignPage():
        """
        Display a kokeshi designing page that, when submitted, updates the shopping cart with the order and redirects to the order page.
        """

        if request.method == 'POST':
            if 'message' in request.form:
                kokeshi = KokeshiDetails(
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight'],
                    message=request.form['message'],
                )

            else:
                kokeshi = KokeshiDetails(
                    item=request.form['item'],
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight'],
                )

            db.session.add(new_order)
            db.session.commit()

            # Set order ID session variable to use when the customer enters
            # their data
            session['new_order_id'] = kokeshi.kokeshiDetailsID
            session['new_order_total'] = 250

            flash("Success! Your order for '%s kokeshi' has been added to your cart." %
                  kokeshi.name)

            return redirect(url_for('showOrderPage'))

        else:
            return render_template('design.html')

    @app.route('/order/')
    def showOrderPage():
        """
        Display the order page.
        """

        return render_template('order.html')

    @app.route('/checkout/', methods=['GET', 'POST'])
    def showCheckoutPage():
        """
        Display the checkout page
        """
        order = db.session.query(Order).filter_by(
            orderID=session['new_order_id']).one()

        if request.method == 'POST':
            customer = Customer(
                lastName=request.form['lastName'],
                firstName=request.form['firstName'],
                title=request.form['title'],
                email=request.form['email'],
            )
            # Connect order to freshly entered customer data
            customer.orders.append(order)
            order.wasOrdered = True

            db.session.add(customer)
            db.session.commit()

            flash("Thank you, %s %s. We will contact you within 48 hours. We appreciate your patience." %
                  (customer.title, customer.lastName))
            return redirect(url_for('showConfirmPage'))

        else:
            return render_template('checkout.html')

    @app.route('/confirmation/')
    def showConfirmPage():
        """
        Display the order confirmation page after an order is submitted
        """

        return render_template('confirmation.html')

    @app.route('/contact/')
    def showContactPage():
        """
        Display the contact information page
        """

        return render_template('contact.html')

    db.init_app(app)
    migrate.init_app(app, db)

    return app


def register_extensions(app):

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    heroku.init_app(app)

    return None
