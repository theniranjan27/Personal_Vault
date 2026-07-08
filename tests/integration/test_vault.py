import pytest
from app import db
from models.vault_item import VaultItem
from services.encryption import EncryptionService

@pytest.fixture
def encryption_service():
    return EncryptionService()

def test_create_vault_item(auth_client, encryption_service):
    response = auth_client.post('/identity/add', json={
        'label': 'Aadhaar',
        'value': '123456789012',
        'category': 'identity'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_get_vault_items(auth_client):
    response = auth_client.get('/identity')
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data

def test_edit_vault_item(auth_client):
    # First create an item
    response = auth_client.post('/identity/add', json={
        'label': 'PAN',
        'value': 'ABCDE1234F',
        'category': 'identity'
    })
    item_id = response.get_json()['id']
    
    # Edit the item
    response = auth_client.put(f'/identity/edit/{item_id}', json={
        'label': 'PAN Updated',
        'value': 'FGHIJ5678K'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_delete_vault_item(auth_client):
    # First create an item
    response = auth_client.post('/identity/add', json={
        'label': 'Passport',
        'value': 'P1234567',
        'category': 'identity'
    })
    item_id = response.get_json()['id']
    
    # Delete the item
    response = auth_client.delete(f'/identity/delete/{item_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_search_vault_items(auth_client):
    # Create some items
    auth_client.post('/identity/add', json={
        'label': 'Aadhaar',
        'value': '123456789012',
        'category': 'identity'
    })
    auth_client.post('/banking/add', json={
        'label': 'SBI Account',
        'value': '1234567890',
        'category': 'banking'
    })
    
    response = auth_client.get('/dashboard/search?q=Aadhaar')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) >= 1

def test_get_recent_items(auth_client):
    response = auth_client.get('/dashboard/recent')
    assert response.status_code == 200
    data = response.get_json()
    assert 'recent' in data

def test_get_favorite_items(auth_client):
    response = auth_client.get('/dashboard/favorites')
    assert response.status_code == 200
    data = response.get_json()
    assert 'favorites' in data

def test_toggle_favorite(auth_client):
    # Create an item
    response = auth_client.post('/identity/add', json={
        'label': 'Test Item',
        'value': 'Test Value',
        'category': 'identity'
    })
    item_id = response.get_json()['id']
    
    # Toggle favorite
    response = auth_client.post(f'/identity/favorite/{item_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_copy_vault_item(auth_client):
    # Create an item
    response = auth_client.post('/identity/add', json={
        'label': 'Copy Test',
        'value': 'CopyValue123',
        'category': 'identity'
    })
    item_id = response.get_json()['id']
    
    response = auth_client.get(f'/identity/copy/{item_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'value' in data
    assert data['value'] == 'CopyValue123'

def test_sensitive_value_hidden(auth_client):
    response = auth_client.post('/identity/add', json={
        'label': 'Sensitive Test',
        'value': '123456789012',
        'category': 'identity'
    })
    
    response = auth_client.get('/identity')
    data = response.get_json()
    for item in data['items']:
        if item['label'] == 'Sensitive Test':
            assert 'encrypted_value' in item
            assert item['value'] != '123456789012'  # Should be masked