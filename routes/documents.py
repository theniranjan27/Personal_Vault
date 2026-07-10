from flask import Blueprint, request, jsonify, session, render_template, send_file
from app import db
from models.vault_file import VaultFile
from services.encryption import encryption_service
from services.audit import audit_service
from services.file_handler import file_handler_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime
import tempfile
import os

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/')
@login_required_redirect
def index():
    """Document vault page"""
    from models.user import User
    user = User.query.get(session['user_id'])
    return render_template('vaults/documents.html', active_page='documents', user=user)


@documents_bp.route('/list')
@login_required
def list_files():
    """List documents"""
    user_id = session['user_id']
    
    files = VaultFile.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).order_by(VaultFile.uploaded_at.desc()).all()
    
    return jsonify({
        'items': [{
            'id': file.id,
            'filename': file.filename,
            'file_size': file.file_size,
            'mime_type': file.mime_type,
            'is_favorite': file.is_favorite,
            'uploaded_at': file.uploaded_at.isoformat()
        } for file in files]
    })


@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload document"""
    user_id = session['user_id']
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file
    validation = file_handler_service.validate_file(file, file.filename)
    if not validation['valid']:
        return jsonify({'error': validation['errors']}), 400
    
    try:
        # Save file
        file_info = file_handler_service.save_file(file, file.filename, user_id)
        
        # Read file content
        with open(file_info['file_path'], 'rb') as f:
            file_content = f.read()
        
        # Encrypt content
        encrypted_content = encryption_service.encrypt_bytes(file_content)
        
        # Save to database
        vault_file = VaultFile(
            user_id=user_id,
            filename=file_info['filename'],
            encrypted_data=encrypted_content,
            file_size=file_info['file_size'],
            mime_type=file_info['mime_type'],
            original_filename=file_info['filename']
        )
        
        db.session.add(vault_file)
        db.session.commit()
        
        # Clean up temp file
        file_handler_service.delete_file(file_info['file_path'])
        
        audit_service.log_action(
            user_id=user_id,
            action='upload',
            details={'file_id': vault_file.id, 'filename': file_info['filename']}
        )
        
        return jsonify({
            'success': True,
            'filename': file_info['filename'],
            'size': file_info['file_size']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@documents_bp.route('/delete/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete document"""
    user_id = session['user_id']
    
    file = VaultFile.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    file.is_deleted = True
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='delete',
        details={'file_id': file_id, 'filename': file.filename}
    )
    
    return jsonify({'success': True})


@documents_bp.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    """Download and decrypt document"""
    user_id = session['user_id']
    
    file = VaultFile.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404
        
    try:
        # Decrypt binary content
        decrypted_data = encryption_service.decrypt_bytes(file.encrypted_data)
        
        audit_service.log_action(
            user_id=user_id,
            action='download',
            details={'file_id': file_id, 'filename': file.filename}
        )
        
        # Send decrypted data back
        import io
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype=file.mime_type or 'application/octet-stream',
            as_attachment=True,
            download_name=file.filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500