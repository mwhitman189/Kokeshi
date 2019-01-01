import os
from os import environ
import psycopg2
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from models import Base, Order, Customer
from flask_seasurf import SeaSurf

APPLICATION_NAME = "Kokeshi"

app = Flask(__name__)
csrf = SeaSurf(app)
app.config.from_pyfile('config_default.cfg')
app.config.from_envvar('KOKESHI_SETTINGS')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', DATABASE_DEFAULT)

engine = create_engine(os.environ['DATABASE_URL'])

db = SQLAlchemy(app)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.before_request
def force_https():
    if request.endpoint in app.view_functions and request.headers.get('X-Forwarded-Proto', None) == 'http':
        return redirect(request.url.replace('http://', 'https://'))


##################
# JSON API calls #
##################


@app.route('/orders/JSON/')
def showOrdersJSON():
    """
    Return order data in JSON
    """
    orders = db_session.query(Order).all()
    return jsonify(orders=[o.serialize for o in orders])


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
    Display a kokeshi designing page that, when submitted, updates the \ shopping cart with the order and redirects to the order page.
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

        db_session.add(new_order)
        db_session.commit()

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
    order = db_session.query(Order).filter_by(
        orderID=session['new_order_id']).one()

    if request.method == 'POST':
        customer = Customer(
            lastName=request.form['lastName'],
            firstName=request.form['firstName'],
            title=request.form['title'],
            email=request.form['email'],
        )
        # Connect order to freshly entered customer data
        customer.orderID.append(order)

        db_session.add(customer)
        db_session.commit()

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


### Initialize App ###
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 8000.
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
