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
    from models import User, Order, Customer, Role, OrderDetails, Product, Supplier, Payment, Shipper, users_schema, orders_schema, products_schema, customers_schema, order_details_schema, suppliers_schema, payments_schema, shippers_schema, MyAdminIndexView, UserAdmin, RoleAdmin
    from flask_admin import Admin
    from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
    from flask_security import SQLAlchemyUserDatastore, Security, utils
    from wtforms.fields import PasswordField
    from passlib.hash import pbkdf2_sha256
    from flask_marshmallow import Marshmallow
    import stripe
    import datetime

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

    STRIPE_PUBLISHABLE_KEY = 'pk_test_GM1d2F2DgrIl6jnkIwSaZ8Dd'
    # Stripe payments implementation
    stripe_keys = {
        'secret_key': os.environ['STRIPE_SECRET_KEY'],
        'publishable_key': STRIPE_PUBLISHABLE_KEY
    }

    stripe.api_key = stripe_keys['secret_key']

    #################
    # App functions #
    #################

    #######################
    # User administration #
    #######################

    """@app.before_first_request
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

        db_items = [
            Product(
                productName="Zao Kokeshi",
                productDescription="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                productName="Yonezawa Kokeshi",
                productDescription="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                productName="Sagae Kokeshi",
                productDescription="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                productName="Tendo Kokeshi",
                productDescription="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                productName="Message",
                productDescription="A handwritten message on the back of the kokeshi doll",
                price=50,
                is_available=True
            ),
            Supplier(
                supplierName="Sato",
                supplierPhone="08011112222",
                supplierEmail="admin@example.com"
            ),
            Supplier(
                supplierName="Miyagi",
                supplierPhone="090000009999",
                supplierEmail="artisan@example.com"
            ),
            Shipper(
                companyName="Kuro Neko",
                companyPhone="08051516161",
                companyEmail="blackCat@example.com",
                contactName="Kurosawa"
            )
        ]

        for item in db_items:
            db.session.add(item)

        db.session.commit()"""

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

    @app.route('/suppliers/JSON')
    @login_required
    def showSuppliersJSON():
        """
        Return order data in JSON
        """
        suppliers = Supplier.query.all()

        return jsonify(suppliers_schema.dump(suppliers).data)

    @app.route('/shippers/JSON')
    @login_required
    def showShippersJSON():
        """
        Return order data in JSON
        """
        shippers = Shipper.query.all()

        return jsonify(shippers_schema.dump(shippers).data)

    @app.route('/products/JSON')
    @login_required
    def showProductsJSON():
        """
        Return order data in JSON
        """
        products = Product.query.all()

        return jsonify(products_schema.dump(products).data)

    @app.route('/orders/JSON')
    @login_required
    def showOrdersJSON():
        """
        Return order data in JSON
        """
        orders = Order.query.all()

        return jsonify(orders_schema.dump(orders).data)

    @app.route('/orders/unfulfilled/JSON')
    @login_required
    def showUnfulfilledOrdersJSON():
        """
        Return unfulfilled order data in JSON
        """
        unful_orders = Order.query.filter_by(wasOrdered=False).all()

        return jsonify(orders_schema.dump(unful_orders).data)

    @app.route('/customers/JSON')
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

    @app.route('/orders')
    @login_required
    def showOrders():
        """
        Display the supplier-facing orders page. The supplier can check the
        next order in the list.
        """
        unaccepted_orders = Order.query.filter_by(wasAccepted=False).all()

        session['supplier'] = current_user.email
        return render_template('unassigned_orders.html', orders=unaccepted_orders)

    @app.route('/orders/<int:order_id>/accepted', methods=['GET', 'POST'])
    @login_required
    def showAcceptOrderPage(order_id):
        """
        Display the supplier-facing order accept page. The supplier can accept
        the job.
        """
        order = Order.query.filter_by(orderID=order_id).first()
        supplier = Supplier.query.filter_by(
            supplierEmail=session['supplier']).first()
        selected_order = Order.query.filter_by(orderID=order_id).first()
        selected_order_details = OrderDetails.query.filter_by(
            order_ID=order_id).first()
        supplier_id = supplier.supplierID

        order.wasAccepted = True
        selected_order.supplier_ID = supplier_id
        db.session.add(selected_order)
        db.session.commit()
        return render_template('selected_order.html', order=selected_order_details)

    @app.route('/')
    @app.route('/home')
    def showHome():
        """
        Display the landing page.
        """
        return render_template('home.html')

    @app.route('/about')
    def showAboutPage():
        """
        Display the About Us page.
        """
        return render_template('about.html')

    @app.route('/design', methods=['GET', 'POST'])
    def showDesignPage():
        """
        Display a kokeshi designing page that, when submitted, updates the shopping cart with the order and redirects to the order page.
        """
        if 'cart' not in session:
            session['cart'] = []

        if request.method == 'POST':

            customer = Customer(email="")
            db.session.add(customer)
            db.session.commit()

            order = Order(customer_ID=customer.customerID)
            db.session.add(order)
            db.session.commit()

            product = Product.query.filter_by(
                productName=request.form['item']).one()

            customer.order_ID = order.orderID

            if request.form.get('is-message', False) == 'on':
                order_details = OrderDetails(
                    item=request.form['item'],
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight'],
                    is_message=True,
                    message=request.form['message'],
                    order_ID=order.orderID,
                    customer_ID=customer.customerID,
                    product_ID=product.productID
                )

            else:
                order_details = OrderDetails(
                    item=request.form['item'],
                    name=request.form['name'],
                    dob=request.form['dob'],
                    height=request.form['height'],
                    weight=request.form['weight'],
                    is_message=False,
                    order_ID=order.orderID,
                    customer_ID=customer.customerID,
                    product_ID=product.productID
                )
            if request.form.get('is-message', False) == 'on':
                price = 250
            else:
                price = 200

            order.price = price

            db.session.add(customer)
            db.session.add(order)
            db.session.add(order_details)
            db.session.commit()

            session['cart'].append(
                {
                    'item': order_details.item,
                    'name': order_details.name,
                    'dob': order_details.dob,
                    'height': order_details.height,
                    'weight': order_details.weight,
                    'isMessage': order_details.is_message,
                    'message': order_details.message,
                    'product': product.productName,
                    'price': price
                }
            )

            session['customer_ID'] = customer.customerID

            flash("Success! Your order for '%s kokeshi' has been added to your cart." %
                  order_details.name)

            return redirect(url_for('showOrderPage'))

        else:
            return render_template('design.html')

    @app.route('/order')
    def showOrderPage():
        """
        Display the order page.
        """

        return render_template('order.html')

    @app.route('/checkout', methods=['GET', 'POST'])
    def showCheckoutPage():
        """
        Display the checkout page
        """
        amount = 0

        for item in session['cart']:
            amount += item['price']

        customer = Customer.query.filter_by(
            customerID=session['customer_ID']).one()
        if request.method == 'POST':
            customer.lastName = request.form['lastName']
            customer.firstName = request.form['firstName']
            customer.title = request.form['title']
            customer.email = request.form['email']

            db.session.add(customer)
            db.session.commit()

            flash("Thank you, %s %s. We will contact you within 48 hours. We appreciate your patience." %
                  (customer.title, customer.lastName))
            return redirect(url_for('showConfirmPage'))

        else:
            return render_template('index.html', key=stripe_keys['publishable_key'], amount=amount)

    @app.route('/charge', methods=['GET', 'POST'])
    def charge():
        db_customer = Customer.query.filter_by(
            customerID=session['customer_ID']).one()
        # Amount in cents
        amount = 0
        items = []
        for item in session['cart']:
            amount += item['price']
            items.append(item['item'])

        try:
            customer = stripe.Customer.create(
                email=db_customer.email,
                source=request.form['stripeToken']
            )

            charge = stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency='usd',
                description='KokeMama Charge'
            )

            session['cart'] = []

        except:
            None

        return render_template('charge.html', amount=amount, items=items)

    @app.route('/confirmation')
    def showConfirmPage():
        """
        Display the order confirmation page after an order is submitted
        """

        return render_template('confirmation.html')

    @app.route('/contact')
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
    mail.init_app(app)

    return None
