from flask import Blueprint, request, jsonify, session, render_template
from services.security import security_service
from utils.decorators import login_required_redirect, login_required

security_bp = Blueprint('security', __name__)


@security_bp.route('/')
@login_required_redirect
def index():
    """Security settings page"""
    return render_template('settings/security.html')


@security_bp.route('/settings')
@login_required
def get_settings():
    """Get security settings"""
    user_id = session['user_id']
    
    settings = security_service.get_security_settings(user_id)
    methods = security_service.get_security_methods(user_id)
    
    return jsonify({
        'settings': settings,
        'methods': methods
    })