from extensions import db, migrate, csrf, ma, heroku, login_manager, mail


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
    from flask import render_template, request, redirect, jsonify, url_for, flash, session
    from sqlalchemy.orm import relationship, sessionmaker
    from models import User, Order, Customer, Role, OrderDetails, Product, Supplier, Payment, Shipper, users_schema, orders_schema, products_schema, customers_schema, order_details_schema, suppliers_schema, payments_schema, shippers_schema, MyAdminIndexView, UserAdmin, RoleAdmin
    from flask_admin import Admin
    from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
    from flask_security import SQLAlchemyUserDatastore, Security, utils, login_required
    from wtforms.fields import PasswordField
    from passlib.hash import pbkdf2_sha256
    from flask_marshmallow import Marshmallow
    import stripe
    import datetime
    from flask_mail import Mail, Message
    from decimal import Decimal

    APPLICATION_NAME = "Kokeshi"

    app = Flask(__name__)
    csrf.init_app(app)
    app.config.from_pyfile('config_default.cfg')

    try:
        app.config.from_envvar('KOKESHI_SETTINGS')
    except:
        pass

    # Flask Security Config
    app.config['SECURITY_REGISTERABLE'] = True

    # Flask-Mail Config
    app.config.update(dict(
        MAIL_SERVER='mail.peraperaexchange.com',
        MAIL_PORT=465,
        MAIL_USERNAME='administrator@peraperaexchange.com',
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
        MAIL_PASSWORD=os.environ['MAIL_PASSWORD'],
        SECURITY_PASSWORD_HASH='pbkdf2_sha512',
        SECURITY_PASSWORD_SALT=os.environ['SECURITY_PASSWORD_SALT']
    ))

    # Initialize the SQLAlchemy data store and Flask-Security.
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Create admin views.
    admin = Admin(app, index_view=MyAdminIndexView())
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))

    # Stripe payments implementation.
    STRIPE_PUBLISHABLE_KEY = 'pk_test_GM1d2F2DgrIl6jnkIwSaZ8Dd'
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

    # Populate the db with products and placeholder data
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
                name="Zao Kokeshi",
                description="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                name="Yonezawa Kokeshi",
                description="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                name="Sagae Kokeshi",
                description="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                name="Tendo Kokeshi",
                description="A traditional handcrafted Japanese Kokeshi doll, made with care to the height of the newborn child",
                price=200,
                is_available=True
            ),
            Product(
                name="Message",
                description="A handwritten message on the back of the kokeshi doll",
                price=50,
                is_available=True
            ),
            Supplier(
                name="Sato",
                phone="08011112222",
                email="admin@example.com"
            ),
            Supplier(
                name="Suzuki",
                phone="08011199002",
                email="super@example.com"
            ),
            Supplier(
                name="Miyagi",
                phone="090000009999",
                email="artisan@example.com"
            ),
            Shipper(
                companyName="Kuro Neko",
                phone="08051516161",
                email="blackCat@example.com",
                contactName="Kurosawa"
            )
        ]

        for item in db_items:
            db.session.add(item)

        db.session.commit()"""

    @app.route('/login', methods=['GET', 'POST'])
    def showLogin():
        """
        Use a custom LoginForm to validate with WTForms
        """
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of the `User` class
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
        """
        Redirect from http to https
        """
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
        Display the supplier - facing orders page. The supplier can accept
        the job, then is directed to the showAcceptOrder
        """
        unaccepted_orders = Order.query.filter_by(wasAccepted=False).all()

        session['supplier'] = current_user.email

        return render_template('unassigned_orders.html', orders=unaccepted_orders)

    @app.route('/orders/<int:order_id>/accepted', methods=['GET', 'POST'])
    @login_required
    def showAcceptOrder(order_id):
        """
        Display the supplier-facing order accepted page.
        """
        order = Order.query.filter_by(orderID=order_id).first()
        supplier = Supplier.query.filter_by(
            email=session['supplier']).first()
        selected_order = Order.query.filter_by(orderID=order_id).first()
        selected_order_details = OrderDetails.query.filter_by(
            order_ID=order_id).first()
        supplier_id = supplier.supplierID

        order.wasAccepted = True
        selected_order.supplier_ID = supplier_id
        db.session.add(selected_order)
        db.session.commit()
        return render_template('selected_order.html', order=selected_order_details)

    @app.route('/', methods=["GET", "POST"])
    @app.route('/home')
    def showHome():
        """
        Display the landing page.
        """
        return render_template('home.html')

    @app.route('/about')
    def showAbout():
        """
        Display the About Us page.
        """
        return render_template('about.html')

    @app.route('/design', methods=['GET', 'POST'])
    def showDesign():
        """
        Display a kokeshi designing page that, when submitted, updates the shopping cart with the order and redirects to the order page.
        """
        # Create a new cart list.
        if 'cart' not in session:
            session['cart'] = []

        if request.method == 'POST':
            # Create a customer object without an email, to attach to the cart
            # items in the session.
            customer = Customer(email="")
            db.session.add(customer)
            db.session.commit()

            # Create an order object and tie it to the customer.
            order = Order(customer_ID=customer.customerID)
            db.session.add(order)
            db.session.commit()

            product = Product.query.filter_by(
                name=request.form['item']).one()

            # Assign the order to the customer using the orderID
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

            # Set the price of the item, dependent on the presence or absence of a message.
            if request.form.get('is-message', False) == 'on':
                price = 250
            else:
                price = 200

            order.price = price

            db.session.add(customer)
            db.session.add(order)
            db.session.add(order_details)
            db.session.commit()

            # Append the item to the cart.
            session['cart'].append(
                {
                    'itemID': order_details.orderDetailsID,
                    'item': order_details.item,
                    'name': order_details.name,
                    'dob': order_details.dob,
                    'height': order_details.height,
                    'weight': order_details.weight,
                    'isMessage': order_details.is_message,
                    'message': order_details.message,
                    'product': product.name,
                    'price': price,
                    'orderID': order_details.order_ID
                }
            )

            # Create a session variable to select the customer in order to append information.
            session['customer_ID'] = customer.customerID

            flash("Success! Your order for '%s kokeshi' has been added to your cart." %
                  order_details.name)

            return redirect(url_for('showOrder'))

        else:
            return render_template('design.html')

    @app.route('/setCart')
    def setCart():
        cartObj = session['cart']
        cartJSON = jsonify(cartObj)
        return cartJSON

    @app.route('/removeItem/<int:item_id>/', methods=["GET", "POST"])
    def removeItem(item_id):
        """
        Remove the selected item from the cart.
        """
        # Check for the existence of an item, then convert it to an int
        if item_id is not None:
            item_id = int(item_id)

        try:
            session['cart'][:] = [d for d in session['cart']
                                  if d.get('itemID') != item_id]
        except:
            msg = "YO"
            print(msg)
        return redirect(url_for('showOrder'))

    @app.route('/order', methods=["GET", "POST"])
    def showOrder():
        """
        Display the order page - - a list of all the items in the cart.
        """

        return render_template('order.html')

    @app.route('/checkout', methods=['GET', 'POST'])
    def showCheckout():
        """
        Display the checkout page, which displays the total, and a Stripe payments button.
        """
        amount_usd = 0

        # Add up the total of all the items in the cart
        for item in session['cart']:
            amount_usd += item['price']

        # Calculate the amount in US cents for Stripe
        amount_cents = amount_usd * 100

        return render_template(
            'index.html',
            key=stripe_keys['publishable_key'],
            amount_usd=amount_usd,
            amount_cents=amount_cents,
            cart=session['cart']
        )

    @app.route('/charge', methods=['GET', 'POST'])
    def charge():
        db_customer = Customer.query.filter_by(
            customerID=session['customer_ID']).one()
        # Amount in cents
        amount = 0
        items = []
        for item in session['cart']:
            # Add the item prices in cents.
            amount += item['price'] * 100
            items.append(item['item'])

        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )

        # Create a session variable with the customer's email for sending a
        # confirmation email.
        session['customer_email'] = request.form['stripeEmail']

        # Create a Stripe charge object which sends a confirmation email.
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='KokeMama Charge',
            receipt_email=session['customer_email']
        )

        # Attempt to add customer data from the stripe input to the customer
        # object
        try:
            db_customer.email = request.form['stripeEmail']
        except:
            print("There is no 'stripeEmail' key")
        try:
            db_customer.name = charge.source.name
        except:
            print("There is no 'stripeName' key")
        try:
            db_customer.address1 = charge.source.address_line1
        except:
            print("There is no 'stripeShippingAddressLine1' key")
        try:
            db_customer.zipCode = charge.source.address_zip
        except:
            print("There is no 'stripeShippingAddressZip' key")
        try:
            db_customer.state = charge.source.address_state
        except:
            print("There is no 'stripeShippingAddressState' key")
        try:
            db_customer.city = charge.source.address_city
        except:
            print("There is no 'stripeShippingAddressCity' key")
        try:
            db_customer.country = charge.source.address_country
        except:
            print("There is no 'stripeShippingAddressCountry' key")

        db.session.add(db_customer)
        db.session.commit()

        return redirect(url_for('showConfirm'))

    @app.route('/confirmation')
    def showConfirm():
        """
        Display the order confirmation page after an order is submitted.
        """
        # Get the customer from the db using the 'customer_ID' session variable
        db_customer = Customer.query.filter_by(
            customerID=session['customer_ID']).one()

        # Create a list of the cart items for use in the email's message body
        items = [dic['item'] for dic in session['cart'] if 'item' in dic]

        # Use the first item in the cart to obtain the 'orderID'
        firstItem = session['cart'][0]
        orderID = firstItem['orderID']

        msg = Message(
            'Confirmation', sender='administrator@peraperaexchange.com', recipients=[session['customer_email']])
        msg.body = "Thank you for your order of: %s. Your order number is: %d." % (
            items, orderID)
        mail.send(msg)

        # Clear the cart after payment is received and confirmation is sent.
        session['cart'] = []

        return render_template('confirmation.html')

    @app.route('/contact/', methods=['GET', 'POST'])
    def showContact():
        """
        Display the contact information page.
        """
        if request.method == 'POST':
            msg = Message(
                'Contact', sender='mileswhitman01@gmail.com', recipients=['administrator@peraperaexchange.com'])
            msg.body = "Customer name: %s" % (
                request.form['customer-name'])
            msg.body += "Customer email: %s" % (request.form['customer-email'])
            msg.body += "Message: %s" % (request.form['customer-message'])
            mail.send(msg)

            customer = Customer(
                name=request.form['customer-name']
                email=request.form['customer-email']
            )
            db.session.add(customer)
            db.session.commit()
            return redirect(url_for('showContactComplete'))

        else:
            return render_template('contact.html')

    @app.route('/contact/complete/')
    def showContactComplete():
        """
        Show a success message for the contact form.
        """
        return render_template('contact_complete.html')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    heroku.init_app(app)
    mail.init_app(app)

    # Load the current logged in user.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app
