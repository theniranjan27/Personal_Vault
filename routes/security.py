from flask import Blueprint, request, jsonify, session, render_template
from app import db
from services.security import security_service
from utils.decorators import login_required_redirect, login_required

security_bp = Blueprint('security', __name__)


@security_bp.route('/')
@login_required_redirect
def index():
    """Security settings page"""
    from models.user import User
    user = User.query.get(session['user_id'])
    return render_template('settings/security.html', active_page='security', user=user)


@security_bp.route('/settings', methods=['GET', 'PUT'])
@login_required
def handle_settings():
    """Get or update security settings"""
    user_id = session['user_id']
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        result = security_service.update_security_settings(user_id, data)
        return jsonify({'success': result})
    
    settings = security_service.get_security_settings(user_id)
    settings['master_password'] = {'enabled': True}
    settings['pin'] = {'enabled': True}
    return jsonify({'settings': settings})


@security_bp.route('/methods', methods=['GET'])
@login_required
def get_methods():
    """Get security methods"""
    user_id = session['user_id']
    methods_list = security_service.get_security_methods(user_id)
    methods_dict = {m['type']: m for m in methods_list}
    if 'password' in methods_dict:
        methods_dict['master_password'] = methods_dict['password']
    else:
        methods_dict['master_password'] = {'enabled': True}
    if 'pin' not in methods_dict:
        methods_dict['pin'] = {'enabled': True}
    return jsonify({'methods': methods_dict})


@security_bp.route('/method/toggle', methods=['POST'])
@login_required
def toggle_method():
    """Toggle a security method"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    method_type = data.get('method')
    enabled = data.get('enabled', False)
    
    type_map = {
        'email_otp': 'otp',
        'authenticator_app_otp': 'totp'
    }
    db_type = type_map.get(method_type, method_type)
    
    from models.security_method import SecurityMethod
    method = SecurityMethod.query.filter_by(user_id=user_id, type=db_type).first()
    if not method:
        security_service.get_security_methods(user_id)
        method = SecurityMethod.query.filter_by(user_id=user_id, type=db_type).first()
        
    if method:
        method.enabled = enabled
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Method not found'}), 404


@security_bp.route('/score', methods=['GET'])
@login_required
def get_score():
    """Get security score"""
    return jsonify({
        'score': 85,
        'details': {
            'master_password': 'Strong',
            'pin': 'Enabled',
            'two_factor': 'Disabled'
        }
    })


@security_bp.route('/devices', methods=['GET'])
@login_required
def get_devices():
    """Get user devices"""
    return jsonify({'devices': []})