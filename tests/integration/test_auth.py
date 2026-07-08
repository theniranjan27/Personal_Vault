import pytest
from app import db
from models.user import User
from services.hashing import PasswordService
from datetime import datetime, timedelta

@pytest.fixture
def password_service():
    return PasswordService()

def test_login_success(client, password_service):
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456'),
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/auth/login', json={
        'master_password': 'SecurePass123!',
        'pin': '123456'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_login_wrong_password(client, password_service):
    user = User(
        username='testuser2',
        email='test2@example.com',
        full_name='Test User 2',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456')
    )
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/auth/login', json={
        'master_password': 'WrongPassword',
        'pin': '123456'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Invalid credentials' in data['error']

def test_login_wrong_pin(client, password_service):
    user = User(
        username='testuser3',
        email='test3@example.com',
        full_name='Test User 3',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456')
    )
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/auth/login', json={
        'master_password': 'SecurePass123!',
        'pin': '654321'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Invalid credentials' in data['error']

def test_login_attempt_limit(client, password_service):
    user = User(
        username='testuser4',
        email='test4@example.com',
        full_name='Test User 4',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456')
    )
    db.session.add(user)
    db.session.commit()
    
    for _ in range(5):
        response = client.post('/auth/login', json={
            'master_password': 'WrongPassword',
            'pin': '123456'
        })
        assert response.status_code == 401
    
    # Sixth attempt should show lock message
    response = client.post('/auth/login', json={
        'master_password': 'WrongPassword',
        'pin': '123456'
    })
    assert response.status_code == 403
    data = response.get_json()
    assert 'locked' in data['error'].lower()

def test_logout(client, auth_client):
    response = auth_client.post('/auth/logout')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_session_check(client):
    response = client.get('/auth/check_session')
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is False

def test_protected_route_without_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 401

def test_protected_route_with_login(auth_client):
    response = auth_client.get('/dashboard')
    assert response.status_code == 200