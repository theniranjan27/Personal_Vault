from flask import Blueprint, request, jsonify, session, render_template
from models.vault_item import VaultItem
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required
from datetime import datetime
import json

digital_assets_bp = Blueprint('digital_assets', __name__)

@digital_assets_bp.route('/digital-assets')
@login_required
def index():
    """Digital assets page"""
    return render_template('vaults/digital_assets.html')

@digital_assets_bp.route('/digital-assets/list')
@login_required
def list_items():
    """List digital assets"""
    user_id = session['user_id']
    
    items = VaultItem.query.filter_by(
        user_id=user_id,
        category='digital_assets'
    ).order_by(VaultItem.updated_at.desc()).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'notes': item.notes,
            'extra': json.loads(item.extra) if item.extra else {},
            'is_favorite': item.is_favorite,
            'is_sensitive': item.is_sensitive,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    })

@digital_assets_bp.route('/digital-assets/add', methods=['POST'])
@login_required
def add_item():
    """Add digital asset"""
    user_id = session['user_id']
    data = request.get_json()
    
    label = data.get('label')
    value = data.get('value')
    notes = data.get('notes')
    extra = data.get('extra', {})
    is_sensitive = data.get('is_sensitive', True)
    is_favorite = data.get('is_favorite', False)
    
    if not label or not value:
        return jsonify({'error': 'Label and value are required'}), 400
    
    item = VaultItem(
        user_id=user_id,
        category='digital_assets',
        label=label,
        encrypted_value=encryption_service.encrypt(value),
        notes=notes,
        extra=json.dumps(extra) if extra else None,
        is_sensitive=is_sensitive,
        is_favorite=is_favorite
    )
    
    db.session.add(item)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='add_item',
        details={'item_id': item.id, 'category': 'digital_assets'}
    )
    
    return jsonify({'success': True, 'id': item.id})

@digital_assets_bp.route('/digital-assets/update/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update digital asset"""
    user_id = session['user_id']
    data = request.get_json()
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='digital_assets').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    if 'label' in data:
        item.label = data['label']
    if 'value' in data:
        item.encrypted_value = encryption_service.encrypt(data['value'])
    if 'notes' in data:
        item.notes = data['notes']
    if 'extra' in data:
        item.extra = json.dumps(data['extra']) if data['extra'] else None
    if 'is_sensitive' in data:
        item.is_sensitive = data['is_sensitive']
    if 'is_favorite' in data:
        item.is_favorite = data['is_favorite']
    
    item.updated_at = datetime.utcnow()
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='edit_item',
        details={'item_id': item_id, 'category': 'digital_assets'}
    )
    
    return jsonify({'success': True})

@digital_assets_bp.route('/digital-assets/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete digital asset"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='digital_assets').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='delete_item',
        details={'item_id': item_id, 'category': 'digital_assets'}
    )
    
    return jsonify({'success': True})

@digital_assets_bp.route('/digital-assets/favorite/<int:item_id>', methods=['POST'])
@login_required
def toggle_favorite(item_id):
    """Toggle favorite status"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='digital_assets').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item.is_favorite = not item.is_favorite
    db.session.commit()
    
    return jsonify({'success': True})

@digital_assets_bp.route('/digital-assets/export')
@login_required
def export_items():
    """Export digital assets"""
    user_id = session['user_id']
    import json
    
    items = VaultItem.query.filter_by(user_id=user_id, category='digital_assets').all()
    
    data = [{
        'label': item.label,
        'value': encryption_service.decrypt(item.encrypted_value),
        'notes': item.notes,
        'extra': json.loads(item.extra) if item.extra else {},
        'is_favorite': item.is_favorite,
        'is_sensitive': item.is_sensitive,
        'created_at': item.created_at.isoformat()
    } for item in items]
    
    return jsonify(data)