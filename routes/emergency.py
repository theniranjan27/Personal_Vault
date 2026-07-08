from flask import Blueprint, request, jsonify, session, render_template
from models.vault_item import VaultItem
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required
from datetime import datetime
import json

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/emergency')
@login_required
def index():
    """Emergency information page"""
    return render_template('vaults/emergency.html')

@emergency_bp.route('/emergency/list')
@login_required
def list_items():
    """List emergency contacts"""
    user_id = session['user_id']
    
    items = VaultItem.query.filter_by(
        user_id=user_id,
        category='emergency'
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

@emergency_bp.route('/emergency/add', methods=['POST'])
@login_required
def add_item():
    """Add emergency contact"""
    user_id = session['user_id']
    data = request.get_json()
    
    label = data.get('label')
    value = data.get('value')
    notes = data.get('notes')
    extra = data.get('extra', {})
    is_favorite = data.get('is_favorite', False)
    
    if not label or not value:
        return jsonify({'error': 'Label and value are required'}), 400
    
    item = VaultItem(
        user_id=user_id,
        category='emergency',
        label=label,
        encrypted_value=encryption_service.encrypt(value),
        notes=notes,
        extra=json.dumps(extra) if extra else None,
        is_sensitive=False,
        is_favorite=is_favorite
    )
    
    db.session.add(item)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='add_item',
        details={'item_id': item.id, 'category': 'emergency'}
    )
    
    return jsonify({'success': True, 'id': item.id})

@emergency_bp.route('/emergency/update/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update emergency contact"""
    user_id = session['user_id']
    data = request.get_json()
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='emergency').first()
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
    if 'is_favorite' in data:
        item.is_favorite = data['is_favorite']
    
    item.updated_at = datetime.utcnow()
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='edit_item',
        details={'item_id': item_id, 'category': 'emergency'}
    )
    
    return jsonify({'success': True})

@emergency_bp.route('/emergency/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete emergency contact"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='emergency').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='delete_item',
        details={'item_id': item_id, 'category': 'emergency'}
    )
    
    return jsonify({'success': True})

@emergency_bp.route('/emergency/favorite/<int:item_id>', methods=['POST'])
@login_required
def toggle_favorite(item_id):
    """Toggle favorite status"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='emergency').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item.is_favorite = not item.is_favorite
    db.session.commit()
    
    return jsonify({'success': True})

@emergency_bp.route('/emergency/export')
@login_required
def export_items():
    """Export emergency contacts"""
    user_id = session['user_id']
    import json
    
    items = VaultItem.query.filter_by(user_id=user_id, category='emergency').all()
    
    data = [{
        'label': item.label,
        'value': encryption_service.decrypt(item.encrypted_value),
        'notes': item.notes,
        'extra': json.loads(item.extra) if item.extra else {},
        'is_favorite': item.is_favorite,
        'created_at': item.created_at.isoformat()
    } for item in items]
    
    return jsonify(data)