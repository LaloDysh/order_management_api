import json
import pytest
from app.models import User


def test_create_user(client):
    """Test creating a new user"""
    data = {
        'email': 'newuser@example.com',
        'name': 'New User'
    }
    
    response = client.post('/api/users', json=data)
    assert response.status_code == 201
    
    response_data = json.loads(response.data)
    assert 'user' in response_data
    assert response_data['user']['email'] == data['email']
    assert response_data['user']['name'] == data['name']


def test_create_user_duplicate_email(client, test_user):
    """Test creating a user with a duplicate email"""
    data = {
        'email': test_user.email,  # Using the email from test_user fixture
        'name': 'Another User'
    }
    
    response = client.post('/api/users', json=data)
    assert response.status_code == 409  # Conflict


def test_create_user_missing_fields(client):
    """Test creating a user with missing required fields"""
    # Missing email
    data = {'name': 'New User'}
    response = client.post('/api/users', json=data)
    assert response.status_code == 400
    
    # Missing name
    data = {'email': 'newuser@example.com'}
    response = client.post('/api/users', json=data)
    assert response.status_code == 400


def test_get_users(client, test_user, auth_headers):
    """Test getting all users"""
    response = client.get('/api/users', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'users' in response_data
    assert len(response_data['users']) > 0
    assert any(user['id'] == test_user.id for user in response_data['users'])


def test_get_user_by_id(client, test_user, auth_headers):
    """Test getting a specific user by ID"""
    response = client.get(f'/api/users/{test_user.id}', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'user' in response_data
    assert response_data['user']['id'] == test_user.id
    assert response_data['user']['email'] == test_user.email


def test_get_user_not_found(client, auth_headers):
    """Test getting a non-existent user"""
    response = client.get('/api/users/nonexistent-id', headers=auth_headers)
    assert response.status_code == 404