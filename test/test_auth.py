import json
import pytest


def test_login_success(client, test_user):
    """Test successful login with email"""
    data = {'email': test_user.email}
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'access_token' in response_data
    assert 'user' in response_data
    assert response_data['user']['id'] == test_user.id


def test_login_missing_email(client):
    """Test login with missing email"""
    data = {}
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 400


def test_login_nonexistent_user(client):
    """Test login with email of non-existent user"""
    data = {'email': 'nonexistent@example.com'}
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 404


def test_verify_token_success(client, auth_headers):
    """Test verifying a valid token"""
    response = client.get('/api/auth/verify', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'user' in response_data
    assert response_data['message'] == 'Token is valid'


def test_verify_token_invalid(client):
    """Test verifying an invalid token"""
    headers = {'Authorization': 'Bearer invalid-token', 'Content-Type': 'application/json'}
    response = client.get('/api/auth/verify', headers=headers)
    assert response.status_code == 401
    
    response_data = json.loads(response.data)
    assert 'error' in response_data


def test_verify_token_missing(client):
    """Test verifying with missing token"""
    headers = {'Content-Type': 'application/json'}
    response = client.get('/api/auth/verify', headers=headers)
    assert response.status_code == 401
    
    response_data = json.loads(response.data)
    assert 'error' in response_data