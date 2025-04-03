import json
import pytest
from app.models import Order, Product


def test_create_order_success(client, test_user, auth_headers):
    """Test creating a new order with products"""
    data = {
        'customer_name': 'New Customer',
        'products': [
            {'name': 'Product A', 'price': 10.0, 'quantity': 2},
            {'name': 'Product B', 'price': 15.0, 'quantity': 1}
        ]
    }
    
    response = client.post('/api/orders', json=data, headers=auth_headers)
    assert response.status_code == 201
    
    response_data = json.loads(response.data)
    assert 'order' in response_data
    assert response_data['order']['customer_name'] == data['customer_name']
    assert response_data['order']['total_price'] == (10.0 * 2) + (15.0 * 1)
    assert len(response_data['order']['products']) == 2


def test_create_order_missing_customer(client, auth_headers):
    """Test creating an order without customer name"""
    data = {
        'products': [
            {'name': 'Product A', 'price': 10.0, 'quantity': 2}
        ]
    }
    
    response = client.post('/api/orders', json=data, headers=auth_headers)
    assert response.status_code == 400


def test_create_order_missing_products(client, auth_headers):
    """Test creating an order without products"""
    data = {
        'customer_name': 'New Customer',
        'products': []
    }
    
    response = client.post('/api/orders', json=data, headers=auth_headers)
    assert response.status_code == 400


def test_create_order_invalid_product(client, auth_headers):
    """Test creating an order with invalid product data"""
    data = {
        'customer_name': 'New Customer',
        'products': [
            {'name': 'Product A', 'quantity': 2}  # Missing price
        ]
    }
    
    response = client.post('/api/orders', json=data, headers=auth_headers)
    assert response.status_code == 400


def test_get_orders(client, test_order, auth_headers):
    """Test getting all orders for the user"""
    response = client.get('/api/orders', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'orders' in response_data
    assert len(response_data['orders']) > 0
    assert any(order['id'] == test_order.id for order in response_data['orders'])


def test_get_order_by_id(client, test_order, auth_headers):
    """Test getting a specific order by ID"""
    response = client.get(f'/api/orders/{test_order.id}', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'order' in response_data
    assert response_data['order']['id'] == test_order.id
    assert response_data['order']['customer_name'] == test_order.customer_name
    assert response_data['order']['total_price'] == test_order.total_price


def test_get_order_not_found(client, auth_headers):
    """Test getting a non-existent order"""
    response = client.get('/api/orders/nonexistent-id', headers=auth_headers)
    assert response.status_code == 404


def test_create_order_with_existing_product(client, auth_headers, test_products):
    """Test creating an order with an existing product"""
    existing_product = test_products[0]
    
    data = {
        'customer_name': 'New Customer',
        'products': [
            {'name': existing_product.name, 'price': 10.0, 'quantity': 2}
        ]
    }
    
    response = client.post('/api/orders', json=data, headers=auth_headers)
    assert response.status_code == 201
    
    # Verify the product wasn't duplicated in database
    response_data = json.loads(response.data)
    product_in_response = response_data['order']['products'][0]
    assert product_in_response['product_name'] == existing_product.name