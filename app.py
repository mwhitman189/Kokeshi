import os
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from models import Base, Order
from flask_seasurf import SeaSurf

APPLICATION_NAME = "Kokeshi"

app = Flask(__name__)
csrf = SeaSurf(app)
app.config.from_object('config.development')
app.config['SECRET_KEY'] = 'super duper secret key'

engine = create_engine('sqlite:///models.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


##################
# JSON API calls #
##################
@app.route('/orders/JSON/')
def showOrdersJSON():
    """
    Return order data in JSON
    """
    orders = session.query(Order).all()
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
        session.add(new_order)
        session.commit()
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


@app.route('/checkout/')
def showCheckoutPage():
    """
    Display the checkout page
    """

    return render_template('checkout.html')


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
