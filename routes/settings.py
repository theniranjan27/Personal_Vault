from flask import Blueprint, request, jsonify, session, render_template, current_app, Response
from app import db
from models.user import User
from services.audit import audit_service
from services.backup import backup_service
from utils.decorators import login_required_redirect, login_required
import os
import json
from werkzeug.utils import secure_filename

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required_redirect
def index():
    """General settings page"""
    user = User.query.get(session['user_id'])
    return render_template('settings/general.html', active_page='settings', user=user)


@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user_id = session['user_id']
    data = request.get_json() or {}
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'field' in data and 'value' in data:
        field = data['field']
        value = data['value']
        if field == 'name':
            user.full_name = value
        elif field == 'username':
            user.username = value
        elif field == 'email':
            user.email = value
    else:
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
            
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': 'profile_data'}
    )
    return jsonify({'success': True})


@settings_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar image"""
    user_id = session['user_id']
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    file.save(os.path.join(upload_folder, filename))
    
    user = User.query.get(user_id)
    user.avatar = filename
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': 'avatar'}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-language', methods=['POST'])
@login_required
def update_language():
    """Update user language preference"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    lang = data.get('language', 'en')
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': 'language', 'value': lang}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-date-format', methods=['POST'])
@login_required
def update_date_format():
    """Update date display format preference"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    fmt = data.get('format', 'eu')
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': 'date_format', 'value': fmt}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-time-format', methods=['POST'])
@login_required
def update_time_format():
    """Update time display format preference"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    fmt = data.get('format', '24')
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': 'time_format', 'value': fmt}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-setting', methods=['POST'])
@login_required
def update_setting():
    """Update generic UI panel setting status"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    
    audit_service.log_action(
        user_id=user_id,
        action='settings',
        details={'field': data.get('key'), 'value': data.get('value')}
    )
    return jsonify({'success': True})


@settings_bp.route('/export-data', methods=['GET'])
@login_required
def export_data():
    """Export all vault data (vault items and notes) as unencrypted JSON"""
    user_id = session['user_id']
    items = backup_service._get_items(user_id)
    notes = backup_service._get_notes(user_id)
    
    export_dict = {
        'type': 'vault_backup',
        'items': items,
        'notes': notes,
        'version': '1.0'
    }
    
    audit_service.log_action(
        user_id=user_id,
        action='download',
        details={'file': 'vault_export.json'}
    )
    
    return Response(
        json.dumps(export_dict, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=vault_export.json'}
    )


@settings_bp.route('/import-data', methods=['POST'])
@login_required
def import_data():
    """Import vault items and notes from exported JSON"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    try:
        data = json.loads(file.read().decode('utf-8'))
        if data.get('type') != 'vault_backup':
            return jsonify({'error': 'Invalid import format'}), 400
            
        user_id = session['user_id']
        backup_service._restore_items(user_id, data.get('items', []))
        backup_service._restore_notes(user_id, data.get('notes', []))
        
        audit_service.log_action(
            user_id=user_id,
            action='restore',
            details={'source': 'vault_export.json'}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change master password"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from services.hashing import password_service
    if not password_service.verify_password(current_password, user.master_password_hash):
        return jsonify({'error': 'Incorrect current password'}), 400
        
    user.master_password_hash = password_service.hash_password(new_password)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'master_password'}
    )
    return jsonify({'success': True})


@settings_bp.route('/change-pin', methods=['POST'])
@login_required
def change_pin():
    """Change login PIN"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    current_pin = data.get('current_pin')
    new_pin = data.get('new_pin')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from services.hashing import password_service
    if not password_service.verify_pin(current_pin, user.pin_hash):
        return jsonify({'error': 'Incorrect current PIN'}), 400
        
    user.pin_hash = password_service.hash_pin(new_pin)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'pin'}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-session-timeout', methods=['POST'])
@login_required
def update_session_timeout():
    """Update session timeout limit"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    timeout = data.get('timeout')
    
    from models.security_setting import SecuritySetting
    setting = SecuritySetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = SecuritySetting(user_id=user_id)
        db.session.add(setting)
    setting.session_timeout_minutes = timeout
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'session_timeout', 'value': timeout}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-login-attempts', methods=['POST'])
@login_required
def update_login_attempts():
    """Update failed attempts limit"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    attempts = data.get('attempts')
    
    from models.security_setting import SecuritySetting
    setting = SecuritySetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = SecuritySetting(user_id=user_id)
        db.session.add(setting)
    setting.max_login_attempts = attempts
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'max_login_attempts', 'value': attempts}
    )
    return jsonify({'success': True})


@settings_bp.route('/update-lockout-duration', methods=['POST'])
@login_required
def update_lockout_duration():
    """Update lockout duration"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    duration = data.get('duration')
    
    from models.security_setting import SecuritySetting
    setting = SecuritySetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = SecuritySetting(user_id=user_id)
        db.session.add(setting)
    setting.lockout_duration_minutes = duration
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'lockout_duration', 'value': duration}
    )
    return jsonify({'success': True})


@settings_bp.route('/delete-all-data', methods=['POST'])
@login_required
def delete_all_data():
    """Delete all vault files, notes, and items"""
    user_id = session['user_id']
    from models.vault_item import VaultItem
    from models.vault_file import VaultFile
    from models.note import Note
    from models.activity_log import ActivityLog
    from models.backup_log import BackupLog
    
    VaultItem.query.filter_by(user_id=user_id).delete()
    VaultFile.query.filter_by(user_id=user_id).delete()
    Note.query.filter_by(user_id=user_id).delete()
    ActivityLog.query.filter_by(user_id=user_id).delete()
    BackupLog.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='security',
        details={'field': 'all_data_destruction'}
    )
    return jsonify({'success': True})