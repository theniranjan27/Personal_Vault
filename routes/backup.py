from flask import Blueprint, request, jsonify, session, render_template
from services.backup import backup_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/')
@login_required_redirect
def index():
    """Backup center page"""
    return render_template('backup/index.html')


@backup_bp.route('/history')
@login_required
def get_history():
    """Get backup history"""
    user_id = session['user_id']
    
    backups = backup_service.get_backup_history(user_id)
    
    return jsonify({'backups': backups})


@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
    """Create a new backup"""
    user_id = session['user_id']
    data = request.get_json() or {}
    
    password = data.get('password')
    
    result = backup_service.create_backup(
        user_id=user_id,
        password=password,
        include_files=True,
        include_settings=True
    )
    
    return jsonify({
        'success': True,
        'backup_id': result['backup_id'],
        'filename': result['filename'],
        'items': result['items'],
        'size': result['size']
    })