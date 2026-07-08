from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app import db, csrf  # Add csrf here
from models.vault_item import VaultItem
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime
import json

banking_bp = Blueprint('banking', __name__)


@banking_bp.route('/')
@login_required_redirect
def index():
    return render_template('vaults/banking.html')


@banking_bp.route('/list')
@login_required
def list_items():
    user_id = session['user_id']
    items = VaultItem.query.filter_by(user_id=user_id, category='banking').order_by(VaultItem.updated_at.desc()).all()
    
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


@banking_bp.route('/add', methods=['POST'])
@csrf.exempt
@login_required
def add_item():
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        label = data.get('label')
        value = data.get('value')
        notes = data.get('notes', '')
        extra = data.get('extra', {})
        is_sensitive = data.get('is_sensitive', True)
        is_favorite = data.get('is_favorite', False)
        
        if not label or not value:
            return jsonify({'error': 'Label and value are required'}), 400
        
        item = VaultItem(
            user_id=user_id,
            category='banking',
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
            details={'item_id': item.id, 'category': 'banking'}
        )
        
        return jsonify({'success': True, 'id': item.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@banking_bp.route('/update/<int:item_id>', methods=['PUT'])
@csrf.exempt
@login_required
def update_item(item_id):
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='banking').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        if 'label' in data:
            item.label = data['label']
        if 'value' in data:
            item.encrypted_value = encryption_service.encrypt(data['value'])
        if 'notes' in data:
            item.notes = data['notes']
        if 'extra' in data:
            item.extra = json.dumps(data['extra']) if data['extra'] else None
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@banking_bp.route('/delete/<int:item_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_item(item_id):
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='banking').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@banking_bp.route('/favorite/<int:item_id>', methods=['POST'])
@csrf.exempt
@login_required
def toggle_favorite(item_id):
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='banking').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        item.is_favorite = not item.is_favorite
        db.session.commit()
        
        return jsonify({'success': True, 'is_favorite': item.is_favorite})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500