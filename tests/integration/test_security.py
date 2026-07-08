import pytest
from app import db
from models.security_setting import SecuritySetting

def test_get_security_settings(auth_client):
    response = auth_client.get('/security/settings')
    assert response.status_code == 200
    data = response.get_json()
    assert 'settings' in data
    assert 'master_password' in data['settings']
    assert 'pin' in data['settings']

def test_update_security_settings(auth_client):
    response = auth_client.put('/security/settings', json={
        'session_timeout_minutes': 30,
        'max_login_attempts': 3,
        'lockout_duration_minutes': 60
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_activity_log_view(auth_client):
    response = auth_client.get('/activity')
    assert response.status_code == 200
    data = response.get_json()
    assert 'logs' in data

def test_get_activity_details(auth_client):
    response = auth_client.get('/activity/1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'log' in data

def test_update_security_method(auth_client):
    response = auth_client.post('/security/method/toggle', json={
        'method': 'email_otp',
        'enabled': True
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_get_security_methods(auth_client):
    response = auth_client.get('/security/methods')
    assert response.status_code == 200
    data = response.get_json()
    assert 'methods' in data
    assert 'master_password' in data['methods']
    assert 'pin' in data['methods']

def test_device_management(auth_client):
    response = auth_client.get('/security/devices')
    assert response.status_code == 200
    data = response.get_json()
    assert 'devices' in data

def test_get_login_history(auth_client):
    response = auth_client.get('/activity/login-history')
    assert response.status_code == 200
    data = response.get_json()
    assert 'history' in data

def test_get_security_score(auth_client):
    response = auth_client.get('/security/score')
    assert response.status_code == 200
    data = response.get_json()
    assert 'score' in data
    assert 'details' in data