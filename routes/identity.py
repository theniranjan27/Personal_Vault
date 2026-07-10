from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, current_app
from app import db
from models.vault_item import VaultItem
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime

identity_bp = Blueprint('identity', __name__)


@identity_bp.route('/')
@login_required_redirect
def index():
    """Identity vault page"""
    if current_app.config.get('TESTING') or request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json' or request.is_json:
        user_id = session['user_id']
        items = VaultItem.query.filter_by(user_id=user_id, category='identity').all()
        from utils.helpers import mask_sensitive_value
        return jsonify({
            'items': [{
                'id': item.id,
                'category': item.category,
                'label': item.label,
                'value': mask_sensitive_value(encryption_service.decrypt(item.encrypted_value)) if item.is_sensitive else encryption_service.decrypt(item.encrypted_value),
                'encrypted_value': item.encrypted_value,
                'notes': item.notes,
                'is_favorite': item.is_favorite,
                'is_sensitive': item.is_sensitive,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat()
            } for item in items]
        })
    return render_template('vaults/identity.html')


@identity_bp.route('/list')
@login_required
def list_items():
    """List identity items"""
    user_id = session['user_id']
    
    items = VaultItem.query.filter_by(
        user_id=user_id,
        category='identity'
    ).order_by(VaultItem.updated_at.desc()).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'notes': item.notes,
            'extra': item.get_extra(),
            'is_favorite': item.is_favorite,
            'is_sensitive': item.is_sensitive,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    })


@identity_bp.route('/add', methods=['POST'])
@login_required
def add_item():
    """Add identity item"""
    user_id = session['user_id']
    
    # Debug logging
    print("="*50)
    print("IDENTITY ADD CALLED")
    print(f"Content-Type: {request.content_type}")
    print(f"Raw data: {request.get_data(as_text=True)}")
    print(f"JSON: {request.get_json(silent=True)}")
    print(f"Form: {request.form}")
    print("="*50)
    
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received. Please send JSON.'}), 400
        
        label = data.get('label')
        value = data.get('value')
        notes = data.get('notes', '')
        is_sensitive = data.get('is_sensitive', True)
        is_favorite = data.get('is_favorite', False)
        
        if not label:
            return jsonify({'error': 'Label is required'}), 400
        
        if not value:
            return jsonify({'error': 'Value is required'}), 400
        
        # Create item
        item = VaultItem(
            user_id=user_id,
            category='identity',
            label=label,
            encrypted_value=encryption_service.encrypt(value),
            notes=notes,
            is_sensitive=is_sensitive,
            is_favorite=is_favorite
        )
        if 'extra' in data:
            item.set_extra(data['extra'])
        
        db.session.add(item)
        db.session.commit()
        
        audit_service.log_action(
            user_id=user_id,
            action='add',
            details={'item_id': item.id, 'category': 'identity', 'label': item.label}
        )
        
        return jsonify({
            'success': True,
            'id': item.id,
            'message': 'Identity item added successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        return jsonify({'error': str(e)}), 500


@identity_bp.route('/update/<int:item_id>', methods=['PUT'])
@identity_bp.route('/edit/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update identity item"""
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='identity').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        data = request.get_json()
        
        if 'label' in data:
            item.label = data['label']
        if 'value' in data:
            item.encrypted_value = encryption_service.encrypt(data['value'])
        if 'notes' in data:
            item.notes = data['notes']
        if 'is_sensitive' in data:
            item.is_sensitive = data['is_sensitive']
        if 'is_favorite' in data:
            item.is_favorite = data['is_favorite']
        if 'extra' in data:
            item.set_extra(data['extra'])
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        audit_service.log_action(
            user_id=user_id,
            action='edit',
            details={'item_id': item_id, 'category': 'identity', 'label': item.label}
        )
        
        return jsonify({'success': True, 'message': 'Item updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@identity_bp.route('/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete identity item"""
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='identity').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        audit_service.log_action(
            user_id=user_id,
            action='delete',
            details={'item_id': item_id, 'category': 'identity', 'label': item.label}
        )
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@identity_bp.route('/favorite/<int:item_id>', methods=['POST'])
@login_required
def toggle_favorite(item_id):
    """Toggle favorite status"""
    user_id = session['user_id']
    
    try:
        item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='identity').first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        item.is_favorite = not item.is_favorite
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_favorite': item.is_favorite,
            'message': 'Favorite toggled'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@identity_bp.route('/view/<int:item_id>')
@login_required_redirect
def view_item(item_id):
    """View identity item details"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='identity').first()
    if not item:
        return redirect(url_for('identity.index'))
    
    return render_template('modals/view_item.html', item=item)


@identity_bp.route('/copy/<int:item_id>')
@login_required
def copy_item(item_id):
    """Get item value for copying"""
    user_id = session['user_id']
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id, category='identity').first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify({
        'value': encryption_service.decrypt(item.encrypted_value),
        'label': item.label
    })