import pytest
from app import create_app, db
from models.user import User
from services.hashing import PasswordService
import tempfile
import os

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(app, client):
    with app.app_context():
        password_service = PasswordService()
        admin = User(
            username='admin',
            email='admin@test.com',
            full_name='Test Admin',
            master_password_hash=password_service.hash_password('SecurePass123!'),
            pin_hash=password_service.hash_pin('123456'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        
        # Login
        response = client.post('/auth/login', json={
            'master_password': 'SecurePass123!',
            'pin': '123456'
        })
        assert response.status_code == 200
        
        yield client
        
        # Cleanup
        db.session.delete(admin)
        db.session.commit()

@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(b'Test file content')
        return f.name

@pytest.fixture
def sample_vault_item():
    return {
        'category': 'identity',
        'label': 'Aadhaar',
        'value': '123456789012',
        'notes': 'Test notes'
    }

@pytest.fixture
def sample_bank_item():
    return {
        'category': 'banking',
        'label': 'SBI Account',
        'value': '1234567890',
        'bank_name': 'SBI',
        'ifsc': 'SBIN0001234',
        'upi': 'user@upi'
    }

@pytest.fixture
def sample_password_item():
    return {
        'category': 'passwords',
        'label': 'Gmail',
        'value': 'password123',
        'username': 'user@gmail.com',
        'url': 'https://gmail.com'
    }