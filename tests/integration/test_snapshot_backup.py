import pytest
import json
import os
import hashlib
from app import db
from models.user import User
from models.backup_log import BackupLog
from models.vault_item import VaultItem
from models.note import Note
from services.backup import backup_service
from services.hashing import password_service

@pytest.fixture
def logged_in_session(app, client):
    """Setup admin user and simulate session verification"""
    with app.app_context():
        # Clean users/backups
        User.query.delete()
        BackupLog.query.delete()
        VaultItem.query.delete()
        Note.query.delete()
        db.session.commit()
        
        user = User(
            username='admin',
            email='admin@test.com',
            full_name='Test Admin',
            master_password_hash=password_service.hash_password('SecurePass123!'),
            pin_hash=password_service.hash_pin('123456'),
            is_admin=True,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Mock session variables
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['master_verified'] = False
            sess['pin_verified'] = True
            
        yield client
        
        with app.app_context():
            User.query.delete()
            BackupLog.query.delete()
            db.session.commit()

def test_snapshot_backup_lifecycle(logged_in_session, app):
    """Test full backup lifecycle with 2FA, checksum, status, safety backup"""
    with app.app_context():
        user = User.query.first()
        user_id = user.id
        
        # 1. Create dummy vault items
        item = VaultItem(
            user_id=user_id,
            category='passwords',
            label='Google Password',
            encrypted_value='EncryptedPassWord123'
        )
        db.session.add(item)
        db.session.commit()
        
    # 2. Trigger Backup Creation with invalid credentials (must reject 401)
    response = logged_in_session.post('/backup/create', json={
        'master_password': 'WrongPassword',
        'pin': '123456'
    })
    assert response.status_code == 401
    
    # 3. Trigger Backup Creation with valid credentials (must pass 200)
    response = logged_in_session.post('/backup/create', json={
        'master_password': 'SecurePass123!',
        'pin': '123456'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    file_name = data['filename']
    assert 'personal_vault_backup_' in file_name
    
    # Check database values
    with app.app_context():
        log = BackupLog.query.filter_by(file_name=file_name).first()
        assert log is not None
        assert log.status == 'Not Verified'
        assert log.checksum is not None
        assert log.download_count == 0
        
        # Verify file path is in the backups folder
        assert 'backups/user_' in log.file_path.replace('\\', '/')
        assert os.path.exists(log.file_path)
        
    # 4. Verify Backup (2FA checked)
    response = logged_in_session.post(f'/backup/verify/{file_name}', json={
        'master_password': 'SecurePass123!',
        'pin': '123456'
    })
    assert response.status_code == 200
    verify_data = response.get_json()
    assert verify_data['status'] == 'Verified'
    
    with app.app_context():
        log = BackupLog.query.filter_by(file_name=file_name).first()
        assert log.status == 'Verified'
        assert log.last_verified_at is not None

    # 5. Download Backup (2FA verified from query parameters)
    response = logged_in_session.get(f'/backup/download/{file_name}?master_password=SecurePass123!&pin=123456')
    assert response.status_code == 200
    assert response.headers['Content-Disposition'].startswith('attachment;filename=personal_vault_backup_')
    assert response.headers['Content-Disposition'].endswith('.vault')
    
    with app.app_context():
        log = BackupLog.query.filter_by(file_name=file_name).first()
        assert log.download_count == 1

    # 6. Delete live records, then restore with 'replace' mode
    with app.app_context():
        # Add another item first
        another_item = VaultItem(
            user_id=user_id,
            category='passwords',
            label='Temporary Password',
            encrypted_value='Temp123'
        )
        db.session.add(another_item)
        db.session.commit()
        assert VaultItem.query.filter_by(user_id=user_id).count() == 2
        
    # Restore (replace mode) -> must automatically create safety backup first!
    response = logged_in_session.post(f'/backup/restore/{file_name}', json={
        'master_password': 'SecurePass123!',
        'pin': '123456',
        'mode': 'replace'
    })
    assert response.status_code == 200
    
    with app.app_context():
        # Check that the safety backup log was created
        all_logs = BackupLog.query.filter_by(user_id=user_id).all()
        # There should be 2 backups now (original + safety backup)
        assert len(all_logs) == 2
        
        # Check that database records are replaced by the backup snapshot (which only had 1 password)
        live_items = VaultItem.query.filter_by(user_id=user_id).all()
        assert len(live_items) == 1
        assert live_items[0].label == 'Google Password'
