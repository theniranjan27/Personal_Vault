from flask import Blueprint, request, jsonify, session, render_template, Response
from services.backup import backup_service
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from services.hashing import password_service
from models.user import User
from models.backup_log import BackupLog
from app import db
import json
import glob
import os
import hashlib
from datetime import datetime

backup_bp = Blueprint('backup', __name__)

def verify_backup_credentials(user_id, master_password, pin):
    """Verify master password and 6-digit PIN"""
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    
    # 1. Verify master password
    if not master_password or not password_service.verify_password(master_password, user.master_password_hash):
        return False, "Invalid master password"
        
    # 2. Verify PIN
    if not pin or not password_service.verify_pin(pin, user.pin_hash):
        return False, "Invalid PIN"
        
    return True, ""


@backup_bp.route('/')
@login_required_redirect
def index():
    """Backup center page"""
    user = User.query.get(session['user_id'])
    return render_template('backup/index.html', active_page='backup', user=user)


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
    data = request.get_json(silent=True) or {}
    master_password = data.get('master_password')
    pin = data.get('pin')
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    try:
        result = backup_service.create_backup(
            user_id=user_id,
            password='system_default_key',
            include_files=True,
            include_settings=True
        )
        
        # Log backup creation action to audit logs
        audit_service.log_action(
            user_id=user_id,
            action='backup_create',
            details={'file_name': result['file_name']}
        )
        
        return jsonify({
            'success': True,
            'backup_id': result['file_name'],
            'filename': result['file_name'],
            'file_path': result['file_path'],
            'items': result['items'],
            'size': result['size']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/download/<path:file_name>', methods=['GET'])
@login_required
def download_backup(file_name):
    """Download an existing backup file"""
    user_id = session['user_id']
    master_password = request.args.get('master_password')
    pin = request.args.get('pin')
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    try:
        log_entry = BackupLog.query.filter_by(user_id=user_id, file_name=file_name).first()
        if not log_entry:
            return jsonify({'error': 'Backup not found'}), 404
            
        filepath = log_entry.file_path
        if not os.path.exists(filepath):
            return jsonify({'error': 'Backup file not found'}), 404
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Verify file integrity and decryption without exposing plaintext secrets
        decrypted = encryption_service.decrypt(content)
        if not decrypted:
            log_entry.status = 'Corrupted'
            db.session.commit()
            return jsonify({'error': 'Backup file is corrupted or unauthorized'}), 400
            
        # Verify record integrity checksum
        backup_data = json.loads(decrypted)
        metadata_block = backup_data.get('metadata', {})
        if 'integrity_checksum' in metadata_block:
            records_str = json.dumps({
                'items': backup_data.get('items', []),
                'notes': backup_data.get('notes', [])
            }, default=str)
            calculated_checksum = hashlib.sha256(records_str.encode('utf-8')).hexdigest()
            if calculated_checksum != metadata_block['integrity_checksum']:
                log_entry.status = 'Corrupted'
                db.session.commit()
                return jsonify({'error': 'Integrity checksum mismatch! File content is corrupted.'}), 400
        
        # Increment download counter and verify date
        log_entry.download_count += 1
        log_entry.last_verified_at = datetime.utcnow()
        db.session.commit()
        
        # Formulate filename
        date_str = log_entry.created_at.strftime('%Y-%m-%d')
        download_name = f"personal_vault_backup_{date_str}.vault"
        
        # Log download action in audit log
        audit_service.log_action(
            user_id=user_id,
            action='backup_download',
            details={'file_name': file_name, 'download_name': download_name}
        )
        
        return Response(
            content,
            mimetype='application/octet-stream',
            headers={'Content-Disposition': f'attachment;filename={download_name}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/import', methods=['POST'])
@login_required
def import_backup():
    """Restore from uploaded backup file"""
    user_id = session['user_id']
    master_password = request.form.get('master_password')
    pin = request.form.get('pin')
    mode = request.form.get('mode', 'merge')  # 'merge' or 'replace'
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    content = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            content = file.read()
            
    if content is None:
        return jsonify({'error': 'No file uploaded or found'}), 400
    
    try:
        try:
            text_content = content.decode('utf-8')
        except Exception:
            text_content = None
        
        # Decrypt uploaded backup file
        if text_content and text_content.strip().startswith('{'):
            json_data = text_content
        else:
            try:
                if text_content:
                    decrypted = encryption_service.decrypt(text_content)
                else:
                    decrypted = encryption_service.decrypt_bytes(content).decode('utf-8')
            except Exception:
                decrypted = encryption_service.decrypt(content.decode('utf-8', errors='ignore'))
            json_data = decrypted

        backup_data = json.loads(json_data)
        if backup_data.get('type') != 'vault_backup':
            return jsonify({'error': 'Invalid backup format'}), 400
            
        # Verify integrity checksum of restored records
        metadata_block = backup_data.get('metadata', {})
        if 'integrity_checksum' in metadata_block:
            records_str = json.dumps({
                'items': backup_data.get('items', []),
                'notes': backup_data.get('notes', [])
            }, default=str)
            calculated_checksum = hashlib.sha256(records_str.encode('utf-8')).hexdigest()
            if calculated_checksum != metadata_block['integrity_checksum']:
                return jsonify({'error': 'Plaintext integrity checksum mismatch! File content is corrupted.'}), 400
            
        # Automatically create a safety backup before replacing
        if mode == 'replace':
            backup_service.create_backup(user_id=user_id)
            
            from models.vault_item import VaultItem
            from models.vault_file import VaultFile
            from models.note import Note
            VaultItem.query.filter_by(user_id=user_id).delete()
            VaultFile.query.filter_by(user_id=user_id).delete()
            Note.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            
        restored_items = backup_service._restore_items(user_id, backup_data.get('items', []))
        restored_notes = backup_service._restore_notes(user_id, backup_data.get('notes', []))
        
        # Log restore action to audit logs
        audit_service.log_action(
            user_id=user_id,
            action='backup_restore',
            details={'source': 'uploaded_backup', 'mode': mode}
        )
        
        return jsonify({
            'success': True,
            'items': len(restored_items),
            'notes': len(restored_notes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/restore/<path:file_name>', methods=['POST'])
@login_required
def restore_saved_backup(file_name):
    """Restore database from a saved backup file name"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    master_password = data.get('master_password')
    pin = data.get('pin')
    mode = data.get('mode', 'merge')
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    try:
        # Automatically create a safety backup before replacing
        if mode == 'replace':
            backup_service.create_backup(user_id=user_id)
            
            from models.vault_item import VaultItem
            from models.vault_file import VaultFile
            from models.note import Note
            VaultItem.query.filter_by(user_id=user_id).delete()
            VaultFile.query.filter_by(user_id=user_id).delete()
            Note.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            
        result = backup_service.restore_backup(
            user_id=user_id,
            file_name=file_name,
            password='system_default_key'
        )
        
        # Log restore action to audit logs
        audit_service.log_action(
            user_id=user_id,
            action='backup_restore',
            details={'file_name': file_name, 'mode': mode}
        )
        
        return jsonify({
            'success': True,
            'items': result['items'],
            'notes': result['notes']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@backup_bp.route('/verify/<path:file_name>', methods=['POST'])
@login_required
def verify_backup(file_name):
    """Verify a backup file and update its status"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    master_password = data.get('master_password')
    pin = data.get('pin')
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    log_entry = BackupLog.query.filter_by(user_id=user_id, file_name=file_name).first()
    if not log_entry:
        return jsonify({'error': 'Backup log not found'}), 404
        
    filepath = log_entry.file_path
    if not os.path.exists(filepath):
        log_entry.status = 'Failed'
        db.session.commit()
        
        # Log verification failure in activity log
        audit_service.log_action(
            user_id=user_id,
            action='backup_verify',
            details={'file_name': file_name, 'status': 'Failed', 'message': 'File not found'}
        )
        return jsonify({'success': True, 'status': 'Failed', 'message': 'Backup file does not exist'})
        
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Verify checksum matches DB
        current_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if current_checksum != log_entry.checksum:
            raise ValueError("Checksum mismatch on file")
            
        # Try to decrypt
        decrypted = encryption_service.decrypt(content)
        if not decrypted:
            raise ValueError("Decryption returned empty string")
            
        backup_data = json.loads(decrypted)
        if backup_data.get('type') != 'vault_backup':
            raise ValueError("Invalid backup type descriptor")
            
        # Verify integrity checksum
        metadata_block = backup_data.get('metadata', {})
        if 'integrity_checksum' in metadata_block:
            records_str = json.dumps({
                'items': backup_data.get('items', []),
                'notes': backup_data.get('notes', [])
            }, default=str)
            calculated_checksum = hashlib.sha256(records_str.encode('utf-8')).hexdigest()
            if calculated_checksum != metadata_block['integrity_checksum']:
                raise ValueError("Plaintext integrity checksum mismatch")
            
        log_entry.status = 'Verified'
        log_entry.last_verified_at = datetime.utcnow()
        db.session.commit()
        
        # Log verification action in activity log
        audit_service.log_action(
            user_id=user_id,
            action='backup_verify',
            details={'file_name': file_name, 'status': 'Verified'}
        )
        return jsonify({'success': True, 'status': 'Verified', 'message': 'Backup verified successfully'})
    except Exception as e:
        log_entry.status = 'Corrupted'
        log_entry.last_verified_at = datetime.utcnow()
        db.session.commit()
        
        # Log verification corruption in activity log
        audit_service.log_action(
            user_id=user_id,
            action='backup_verify',
            details={'file_name': file_name, 'status': 'Corrupted', 'error': str(e)}
        )
        return jsonify({'success': True, 'status': 'Corrupted', 'message': f'Backup is corrupted: {str(e)}'})


@backup_bp.route('/delete/<path:file_name>', methods=['POST'])
@login_required
def delete_backup(file_name):
    """Delete a backup file"""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    master_password = data.get('master_password')
    pin = data.get('pin')
    
    # Verify credentials first
    success, err_msg = verify_backup_credentials(user_id, master_password, pin)
    if not success:
        return jsonify({'error': err_msg}), 401
        
    try:
        res = backup_service.delete_backup(user_id, file_name)
        if res:
            # Log backup deletion action to audit logs
            audit_service.log_action(
                user_id=user_id,
                action='backup_delete',
                details={'file_name': file_name}
            )
            return jsonify({'success': True})
        return jsonify({'error': 'Delete failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/stats')
@login_required
def get_stats():
    """Get backup stats"""
    user_id = session['user_id']
    logs = BackupLog.query.filter_by(user_id=user_id).all()
    
    total = len(logs)
    last_backup = 'Never'
    if logs:
        latest = max(logs, key=lambda l: l.created_at)
        last_backup = latest.created_at.strftime('%b %d, %Y %H:%M')
        
    storage = sum(log.file_size for log in logs) if logs else 0
    
    return jsonify({
        'total': total,
        'last': last_backup,
        'storage': storage
    })