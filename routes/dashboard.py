from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from app import db
from models.user import User
from models.vault_item import VaultItem
from models.vault_file import VaultFile
from services.encryption import encryption_service

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session or not session.get('pin_verified'):
        if request.path == '/dashboard':
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('auth.login_page'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        if request.path == '/dashboard':
            return jsonify({'error': 'User not found'}), 401
        return redirect(url_for('auth.login_page'))
    
    return render_template('dashboard/index.html', user=user)


@dashboard_bp.route('/dashboard/counts')
def get_counts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    from models.note import Note
    from models.backup_log import BackupLog
    
    counts = {
        'identity': VaultItem.query.filter_by(user_id=user_id, category='identity').count(),
        'banking': VaultItem.query.filter_by(user_id=user_id, category='banking').count(),
        'passwords': VaultItem.query.filter_by(user_id=user_id, category='passwords').count(),
        'notes': Note.query.filter_by(user_id=user_id).count(),
        'documents': VaultFile.query.filter_by(user_id=user_id).count(),
        'backups': BackupLog.query.filter_by(user_id=user_id).count(),
        'assets': VaultItem.query.filter_by(user_id=user_id, category='digital_assets').count()
    }
    return jsonify(counts)


@dashboard_bp.route('/dashboard/recent')
def get_recent():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    from models.note import Note
    
    vault_items = VaultItem.query.filter_by(user_id=user_id).order_by(VaultItem.updated_at.desc()).limit(10).all()
    notes = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).limit(10).all()
    
    recent_items = []
    for item in vault_items:
        recent_items.append({
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'updated_at': item.updated_at
        })
    for note in notes:
        recent_items.append({
            'id': note.id,
            'category': 'notes',
            'label': note.title,
            'value': encryption_service.decrypt(note.content),
            'updated_at': note.updated_at
        })
        
    recent_items.sort(key=lambda x: x['updated_at'], reverse=True)
    recent_items = recent_items[:10]
    
    for item in recent_items:
        item['updated_at'] = item['updated_at'].isoformat() + 'Z'
        
    return jsonify({
        'items': recent_items,
        'recent': recent_items
    })


@dashboard_bp.route('/dashboard/favorites')
def get_favorites():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    items = VaultItem.query.filter_by(user_id=user_id, is_favorite=True).order_by(VaultItem.updated_at.desc()).limit(10).all()
    
    favorites_list = [{
        'id': item.id,
        'category': item.category,
        'label': item.label,
        'value': encryption_service.decrypt(item.encrypted_value),
        'is_favorite': item.is_favorite
    } for item in items]
    
    return jsonify({
        'items': favorites_list,
        'favorites': favorites_list
    })


@dashboard_bp.route('/dashboard/search')
def search():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query_str = request.args.get('q', '')
    user_id = session['user_id']
    
    items = VaultItem.query.filter(
        VaultItem.user_id == user_id,
        (VaultItem.label.ilike(f'%{query_str}%')) | (VaultItem.category.ilike(f'%{query_str}%'))
    ).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    })