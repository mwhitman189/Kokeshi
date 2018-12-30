import os
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from models import Base, Order, Customer
from flask_seasurf import SeaSurf

APPLICATION_NAME = "Kokeshi"

app = Flask(__name__)
csrf = SeaSurf(app)
app.config.from_object('config.development')
app.config['SECRET_KEY'] = 'super duper secret key'

engine = create_engine('sqlite:///models.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


##################
# JSON API calls #
##################
def createCustomer(browsing_session):
    """
    Add customer to database
    """
    newCustomer = Customer(
        lastName=request.form['lastName'],
        firstName=request.form['firstName'],
        title=request.form['title'],
        email=request.form['email']
    )

    db_session.add(customer)
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise
    customer = db_session.query(Customer).filter_by(
        email=db_session['email']).one()
    return customer.customerID


def getCustomerInfo(customer_id):
    customer = db_session.query(Customer).filter_by(
        customerID=customer_id).one()
    return customer


def getCustomerID(email):
    try:
        customer = db_session.query(Customer).filter_by(email=email).one()
        return customer.customerID
    except:
        return None


def setCart(cartItem):
    cart = cartItem
    session['cart'] = cart
    print session['cart'].orderID
    return session['cart']

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

        db_session.add(new_order)
        db_session.commit()
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
    if request.method == 'POST':
        customer = Customer(
            lastName=request.form['lastName'],
            firstName=request.form['firstName'],
            title=request.form['title'],
            email=request.form['email'],
        )

        db_session.add(customer)
        db_session.commit()

        order = db_session.query(Order).filter_by(
            orderID=session['new_order_id']).one()

        flash("Thank you, %s %s. We will contact you within 48 hours. We appreciate your patience." %
              (customer.title, customer.lastName))
        return redirect(url_for('showConfirmPage'))

    else:
        return render_template('checkout_1.html')


@app.route('/confirmation/')
def showConfirmPage():
    """
    Display the order confirmation page after an order is submitted
    """
    order = db_session.query(Order).filter_by(
        orderID=session['new_order_id']).all()
    return jsonify(order=[o.serialize for o in order])

    # return render_template('confirmation.html')


@app.route('/contact/')
def showContactPage():
    """
    Display the contact information page
    """

    return render_template('contact.html')


### Initialize App ###
if __name__ == '__main__':
    app.debug = True
    # Bind to PORT if defined, otherwise default to 8000.
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
