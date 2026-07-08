from flask import Blueprint, request, jsonify, session, render_template
from app import db
from models.note import Note
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/')
@login_required_redirect
def index():
    """Notes vault page"""
    return render_template('vaults/notes.html')


@notes_bp.route('/list')
@login_required
def list_notes():
    """List notes"""
    user_id = session['user_id']
    
    notes = Note.query.filter_by(
        user_id=user_id
    ).order_by(Note.updated_at.desc()).all()
    
    return jsonify({
        'items': [{
            'id': note.id,
            'title': note.title,
            'content': encryption_service.decrypt(note.content),
            'category': note.category,
            'tags': note.tags,
            'is_archived': note.is_archived,
            'is_favorite': note.is_favorite,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat()
        } for note in notes]
    })


@notes_bp.route('/add', methods=['POST'])
@login_required
def add_note():
    """Add note"""
    user_id = session['user_id']
    data = request.get_json() or {}
    
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')
    tags = data.get('tags')
    is_favorite = data.get('is_favorite', False)
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    note = Note(
        user_id=user_id,
        title=title,
        content=encryption_service.encrypt(content),
        category=category,
        tags=tags,
        is_favorite=is_favorite
    )
    
    db.session.add(note)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='add_note',
        details={'note_id': note.id}
    )
    
    return jsonify({'success': True, 'id': note.id})


@notes_bp.route('/delete/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete note"""
    user_id = session['user_id']
    
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    db.session.delete(note)
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='delete_note',
        details={'note_id': note_id}
    )
    
    return jsonify({'success': True})


@notes_bp.route('/favorite/<int:note_id>', methods=['POST'])
@login_required
def toggle_favorite(note_id):
    """Toggle favorite status"""
    user_id = session['user_id']
    
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    note.is_favorite = not note.is_favorite
    db.session.commit()
    
    return jsonify({'success': True})