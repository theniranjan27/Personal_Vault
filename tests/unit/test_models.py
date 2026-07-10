import pytest
from app import db
from models.user import User
from models.vault_item import VaultItem
from models.vault_file import VaultFile
from models.note import Note
from models.activity_log import ActivityLog
from models.security_setting import SecuritySetting
from services.hashing import PasswordService
from datetime import datetime, timedelta

@pytest.fixture
def password_service():
    return PasswordService()

def test_create_user(app, password_service):
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456'),
        is_admin=True,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.is_admin is True
    assert user.is_active is True
    assert user.created_at is not None

def test_user_relationships(app, password_service):
    user = User(
        username='testuser2',
        email='test2@example.com',
        full_name='Test User 2',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456')
    )
    db.session.add(user)
    db.session.commit()
    
    item = VaultItem(
        user_id=user.id,
        category='identity',
        label='Aadhaar',
        encrypted_value='encrypted_data'
    )
    db.session.add(item)
    db.session.commit()
    
    assert len(user.vault_items) == 1
    assert user.vault_items[0].label == 'Aadhaar'

def test_vault_item_encryption(app):
    item = VaultItem(
        user_id=1,
        category='identity',
        label='PAN',
        encrypted_value='encrypted_pan_data'
    )
    db.session.add(item)
    db.session.commit()
    assert item.encrypted_value == 'encrypted_pan_data'
    assert item.created_at is not None

def test_vault_file(app):
    file = VaultFile(
        user_id=1,
        filename='test.pdf',
        encrypted_data=b'encrypted_binary',
        file_size=1024,
        mime_type='application/pdf',
        original_filename='document.pdf'
    )
    db.session.add(file)
    db.session.commit()
    assert file.filename == 'test.pdf'
    assert file.file_size == 1024
    assert not file.is_deleted

def test_note(app):
    note = Note(
        user_id=1,
        title='Test Note',
        content='encrypted_note_content',
        category='Personal'
    )
    db.session.add(note)
    db.session.commit()
    assert note.title == 'Test Note'
    assert note.category == 'Personal'
    assert note.is_archived is False

def test_activity_log(app):
    log = ActivityLog(
        user_id=1,
        action='login',
        details='User logged in',
        ip_address='127.0.0.1',
        user_agent='Test Agent'
    )
    db.session.add(log)
    db.session.commit()
    assert log.action == 'login'
    assert log.ip_address == '127.0.0.1'
    assert log.timestamp is not None

def test_security_setting(app):
    setting = SecuritySetting(
        user_id=1,
        session_timeout_minutes=15,
        max_login_attempts=5,
        lockout_duration_minutes=30
    )
    db.session.add(setting)
    db.session.commit()
    assert setting.session_timeout_minutes == 15
    assert setting.max_login_attempts == 5
    assert setting.two_factor_enabled is False

def test_user_login_attempts(app, password_service):
    user = User(
        username='testuser3',
        email='test3@example.com',
        full_name='Test User 3',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456'),
        failed_attempts=3
    )
    db.session.add(user)
    db.session.commit()
    
    assert user.failed_attempts == 3
    assert user.is_locked() is False

def test_user_lockout(app, password_service):
    user = User(
        username='testuser4',
        email='test4@example.com',
        full_name='Test User 4',
        master_password_hash=password_service.hash_password('SecurePass123!'),
        pin_hash=password_service.hash_pin('123456'),
        failed_attempts=5,
        locked_until=datetime.utcnow() + timedelta(minutes=30)
    )
    db.session.add(user)
    db.session.commit()
    
    assert user.is_locked() is True

def test_vault_item_last_accessed(app):
    item = VaultItem(
        user_id=1,
        category='identity',
        label='Passport',
        encrypted_value='encrypted_data'
    )
    db.session.add(item)
    db.session.commit()
    
    assert item.last_accessed is None
    
    # Update last accessed
    item.update_last_accessed()
    assert item.last_accessed is not None