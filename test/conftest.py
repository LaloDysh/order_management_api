import pytest
from app import create_app
from app.extensions import db
from app.models import User, Product, Order, OrderProduct
import os


@pytest.fixture(scope='function')
def app():
    """Create and configure a Flask app for testing"""
    # Use an in-memory SQLite database for testing
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-key',
    })

    # Create the database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def test_db(app):
    """Create and configure database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_user(test_db):
    """Create a test user"""
    user = User(email='test@example.com', name='Test User')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def auth_headers(app, test_user):
    """Get authorization headers for the test user"""
    from flask_jwt_extended import create_access_token
    
    with app.app_context():
        access_token = create_access_token(identity=test_user.id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return headers


@pytest.fixture(scope='function')
def test_products(test_db):
    """Create test products"""
    products = [
        Product(name='Product 1', price=10.0),
        Product(name='Product 2', price=15.0),
        Product(name='Product 3', price=20.0)
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()
    return products


@pytest.fixture(scope='function')
def test_order(test_db, test_user, test_products):
    """Create a test order with products"""
    order = Order(
        user_id=test_user.id,
        customer_name='Test Customer',
        total_price=55.0  # 10*2 + 15*1 + 20*1
    )
    db.session.add(order)
    db.session.flush()
    
    # Add order products
    order_products = [
        OrderProduct(product_id=test_products[0].id, quantity=2, unit_price=10.0),
        OrderProduct(product_id=test_products[1].id, quantity=1, unit_price=15.0),
        OrderProduct(product_id=test_products[2].id, quantity=1, unit_price=20.0)
    ]
    
    for op in order_products:
        op.order_id = order.id
        db.session.add(op)
    
    db.session.commit()
    return order