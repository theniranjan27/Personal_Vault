import pytest
import json
import tempfile
import os
from app import db
from models.vault_item import VaultItem
from services.backup import BackupService
from services.encryption import EncryptionService

@pytest.fixture
def backup_service():
    return BackupService()

@pytest.fixture
def encryption_service():
    return EncryptionService()

def test_create_backup(auth_client, backup_service):
    response = auth_client.post('/backup/create')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'backup_id' in data
    assert 'file_path' in data

def test_get_backup_history(auth_client):
    response = auth_client.get('/backup/history')
    assert response.status_code == 200
    data = response.get_json()
    assert 'backups' in data

def test_export_encrypted_backup(auth_client):
    response = auth_client.post('/backup/export')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'download_url' in data

def test_import_backup(auth_client, backup_service):
    # First create a backup
    response = auth_client.post('/backup/create')
    backup_file = response.get_json()['file_path']
    
    with open(backup_file, 'rb') as f:
        backup_data = f.read()
    
    response = auth_client.post('/backup/import', data={
        'file': (backup_data, 'backup.json')
    }, content_type='multipart/form-data')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_backup_restore(auth_client):
    # Create some data
    auth_client.post('/identity/add', json={
        'label': 'Backup Test',
        'value': 'Test Value 123',
        'category': 'identity'
    })
    
    # Create backup
    response = auth_client.post('/backup/create')
    backup_id = response.get_json()['backup_id']
    
    # Restore
    response = auth_client.post(f'/backup/restore/{backup_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_backup_encryption(backup_service, encryption_service):
    test_data = {'test': 'data', 'sensitive': '1234567890'}
    encrypted = backup_service.encrypt_backup(test_data)
    assert encrypted != test_data
    decrypted = backup_service.decrypt_backup(encrypted)
    assert decrypted == test_data

def test_backup_contains_all_data(auth_client):
    # Create multiple items
    auth_client.post('/identity/add', json={
        'label': 'Aadhaar',
        'value': '123456789012',
        'category': 'identity'
    })
    auth_client.post('/banking/add', json={
        'label': 'Bank Account',
        'value': '9876543210',
        'category': 'banking'
    })
    
    response = auth_client.post('/backup/create')
    backup_file = response.get_json()['file_path']
    
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    assert 'items' in backup_data
    assert len(backup_data['items']) >= 2
    assert 'metadata' in backup_data
    assert 'timestamp' in backup_data
    assert 'user' in backup_data