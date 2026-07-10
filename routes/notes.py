from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app import db, csrf
from models.note import Note
from services.encryption import encryption_service
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime
import json

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/')
@login_required_redirect
def index():
    return render_template('vaults/notes.html')


@notes_bp.route('/list')
@login_required
def list_notes():
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
            'is_favorite': note.is_favorite,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat() + 'Z',
            'updated_at': note.updated_at.isoformat() + 'Z'
        } for note in notes]
    })


@notes_bp.route('/add', methods=['POST'])
@csrf.exempt
@login_required
def add_note():
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        title = data.get('title')
        content = data.get('content')
        category = data.get('category', 'Personal')
        tags = data.get('tags', '')
        is_favorite = data.get('is_favorite', False)
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
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
            action='add',
            details={'note_id': note.id, 'category': 'notes', 'label': note.title}
        )
        
        return jsonify({'success': True, 'id': note.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/update/<int:note_id>', methods=['PUT'])
@csrf.exempt
@login_required
def update_note(note_id):
    user_id = session['user_id']
    
    try:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = encryption_service.encrypt(data['content'])
        if 'category' in data:
            note.category = data['category']
        if 'tags' in data:
            note.tags = data['tags']
        if 'is_favorite' in data:
            note.is_favorite = data['is_favorite']
        if 'is_archived' in data:
            note.is_archived = data['is_archived']
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        audit_service.log_action(
            user_id=user_id,
            action='edit',
            details={'note_id': note_id, 'category': 'notes', 'label': note.title}
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/delete/<int:note_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_note(note_id):
    user_id = session['user_id']
    
    try:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        db.session.delete(note)
        db.session.commit()
        
        audit_service.log_action(
            user_id=user_id,
            action='delete',
            details={'note_id': note_id, 'category': 'notes', 'label': note.title}
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/favorite/<int:note_id>', methods=['POST'])
@csrf.exempt
@login_required
def toggle_favorite(note_id):
    user_id = session['user_id']
    
    try:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        note.is_favorite = not note.is_favorite
        db.session.commit()
        
        return jsonify({'success': True, 'is_favorite': note.is_favorite})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/export')
@login_required
def export_notes():
    user_id = session['user_id']
    import json
    
    notes = Note.query.filter_by(user_id=user_id).all()
    
    data = [{
        'title': note.title,
        'content': encryption_service.decrypt(note.content),
        'category': note.category,
        'tags': note.tags,
        'is_favorite': note.is_favorite,
        'is_archived': note.is_archived,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    } for note in notes]
    
    return jsonify(data)