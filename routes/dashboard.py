from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from app import db
from models.user import User
from models.vault_item import VaultItem
from models.vault_file import VaultFile
from services.encryption import encryption_service

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')  # This is the root URL
def index():
    if 'user_id' not in session or not session.get('pin_verified'):
        return redirect(url_for('auth.login_page'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login_page'))
    
    return render_template('dashboard/index.html', user=user)

@dashboard_bp.route('/dashboard')  # Also works with /dashboard
def dashboard_redirect():
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard/counts')
def get_counts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    counts = {
        'identity': VaultItem.query.filter_by(user_id=user_id, category='identity').count(),
        'banking': VaultItem.query.filter_by(user_id=user_id, category='banking').count(),
        'passwords': VaultItem.query.filter_by(user_id=user_id, category='passwords').count(),
        'notes': VaultItem.query.filter_by(user_id=user_id, category='notes').count(),
        'documents': VaultFile.query.filter_by(user_id=user_id).count(),
        'assets': VaultItem.query.filter_by(user_id=user_id, category='digital_assets').count()
    }
    return jsonify(counts)

@dashboard_bp.route('/dashboard/recent')
def get_recent():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    items = VaultItem.query.filter_by(user_id=user_id).order_by(VaultItem.updated_at.desc()).limit(10).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    })

@dashboard_bp.route('/dashboard/favorites')
def get_favorites():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    items = VaultItem.query.filter_by(user_id=user_id, is_favorite=True).order_by(VaultItem.updated_at.desc()).limit(10).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'value': encryption_service.decrypt(item.encrypted_value),
            'is_favorite': item.is_favorite
        } for item in items]
    })