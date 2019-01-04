import os
from os import environ
import psycopg2
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from models import User, Order, Customer
from run import app
from __init__ import db


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
    orders = db.session.query(Order).all()
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

    if request.method == 'POST':
        customer = Customer(
            lastName=request.form['lastName'],
            firstName=request.form['firstName'],
            title=request.form['title'],
            email=request.form['email'],
        )
        # Connect order to freshly entered customer data
        customer.orderID.append(order)

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