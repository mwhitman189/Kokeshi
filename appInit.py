from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_seasurf import SeaSurf
from flask_heroku import Heroku

db = SQLAlchemy()
migrate = Migrate()


def create_app():

    import os
    from os import environ
    import psycopg2
    from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship, sessionmaker
    from sqlalchemy import create_engine
    from flask_sqlalchemy import SQLAlchemy
    from models import User, Order, Customer, user_schema, order_schema, orders_schema, customer_schema

    APPLICATION_NAME = "Kokeshi"

    app = Flask(__name__)
    heroku = Heroku(app)
    csrf = SeaSurf(app)
    app.config.from_pyfile('config_default.cfg')

    try:
        app.config.from_envvar('KOKESHI_SETTINGS')
    except:
        pass

    db = SQLAlchemy(app)

    ############################
    # Administrative functions #
    ############################

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
    def showOrdersJSON():
        """
        Return order data in JSON
        """
        orders = Order.query.all()
        return jsonify(orders_schema.dump(orders).data)

    @app.route('/orders/unfulfilled/JSON/')
    def showUnfulfilledOrdersJSON():
        """
        Return unfulfilled order data in JSON
        """
        unful_orders = Order.query.filter_by(wasOrdered=False).all()

        return jsonify(orders_schema.dump(unful_orders).data)

    @app.route('/customers/JSON/')
    def showCustomersJSON():
        """
        Return customer data in JSON
        """
        customers = Customer.query.all()

        return jsonify(customer_schema.dump(customers).data)

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
                new_order = Order(
                    item=request.form['item'],
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight'],
                    message=request.form['message']
                )

            else:
                new_order = Order(
                    item=request.form['item'],
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight']
                )

            db.session.add(new_order)
            db.session.commit()

            # Set order ID session variable to use when the customer enters
            # their data
            session['new_order_id'] = new_order.orderID

            flash("Success! Your order of '%s kokeshi' has been added to your cart." %
                  new_order.item)

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
        print order.orderID

        if request.method == 'POST':
            customer = Customer(
                lastName=request.form['lastName'],
                firstName=request.form['firstName'],
                title=request.form['title'],
                email=request.form['email'],
            )
            # Connect order to freshly entered customer data
            customer.orders.append(order)

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
