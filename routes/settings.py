from flask import Blueprint, request, jsonify, session, render_template
from app import db
from models.user import User
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required_redirect
def index():
    """General settings page"""
    return render_template('settings/general.html')


@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user_id = session['user_id']
    data = request.get_json() or {}
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({'success': True})