from flask import Blueprint, request, jsonify, session, render_template, current_app
from app import db
from models.activity_log import ActivityLog
from services.audit import audit_service
from utils.decorators import login_required_redirect, login_required
from datetime import datetime, timedelta

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/')
@login_required_redirect
def index():
    """Activity logs page"""
    from models.user import User
    user = User.query.get(session['user_id'])
    if current_app.config.get('TESTING') or request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json' or request.is_json:
        user_id = session['user_id']
        activities = ActivityLog.query.filter_by(user_id=user_id).all()
        return jsonify({
            'logs': [{
                'id': act.id,
                'action': act.action,
                'details': act.details,
                'timestamp': act.timestamp.isoformat() + 'Z'
            } for act in activities]
        })
    return render_template('settings/activity.html', active_page='activity', user=user)


@activity_bp.route('/list')
@login_required
def list_activities():
    """List activity logs"""
    user_id = session['user_id']
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    action = request.args.get('action')
    search = request.args.get('search')
    date_filter = request.args.get('date')
    tz_offset = request.args.get('tz_offset', 0, type=int)
    
    query = ActivityLog.query.filter_by(user_id=user_id)
    
    if action and action != 'all':
        query = query.filter_by(action=action)
    
    if search:
        query = query.filter(ActivityLog.details.ilike(f'%{search}%'))
    
    if date_filter:
        try:
            date = datetime.strptime(date_filter, '%Y-%m-%d')
            start_date = date + timedelta(minutes=tz_offset)
            end_date = date + timedelta(days=1, minutes=tz_offset)
            query = query.filter(
                ActivityLog.timestamp >= start_date,
                ActivityLog.timestamp < end_date
            )
        except ValueError:
            pass
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    activities = query.order_by(ActivityLog.timestamp.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return jsonify({
        'activities': [{
            'id': activity.id,
            'action': activity.action,
            'description': activity.details,
            'success': activity.success,
            'ip_address': activity.ip_address,
            'user_agent': activity.user_agent,
            'timestamp': activity.timestamp.isoformat() + 'Z'
        } for activity in activities],
        'total': total,
        'pages': total_pages,
        'current_page': page
    })


@activity_bp.route('/stats')
@login_required
def get_stats():
    """Get activity statistics"""
    user_id = session['user_id']
    
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    total = ActivityLog.query.filter_by(user_id=user_id).count()
    today_count = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= today
    ).count()
    week_count = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= week_start
    ).count()
    month_count = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= month_start
    ).count()
    
    return jsonify({
        'total': total,
        'today': today_count,
        'week': week_count,
        'month': month_count
    })


@activity_bp.route('/log-reveal/<int:item_id>', methods=['POST'])
@login_required
def log_reveal(item_id):
    """Log sensitive value reveal"""
    user_id = session['user_id']
    from models.vault_item import VaultItem
    from models.note import Note
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id).first()
    category = ""
    label = ""
    if item:
        category = item.category
        label = item.label
    else:
        note = Note.query.filter_by(id=item_id, user_id=user_id).first()
        if note:
            category = 'notes'
            label = note.title
            
    audit_service.log_action(
        user_id=user_id,
        action='reveal',
        details={'item_id': item_id, 'category': category, 'label': label}
    )
    return jsonify({'success': True})


@activity_bp.route('/log-view/<int:item_id>', methods=['POST'])
@login_required
def log_view(item_id):
    """Log vault item view"""
    user_id = session['user_id']
    from models.vault_item import VaultItem
    from models.note import Note
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id).first()
    category = ""
    label = ""
    if item:
        category = item.category
        label = item.label
    else:
        note = Note.query.filter_by(id=item_id, user_id=user_id).first()
        if note:
            category = 'notes'
            label = note.title
            
    audit_service.log_action(
        user_id=user_id,
        action='view',
        details={'item_id': item_id, 'category': category, 'label': label}
    )
    return jsonify({'success': True})


@activity_bp.route('/log-copy/<int:item_id>', methods=['POST'])
@login_required
def log_copy(item_id):
    """Log vault item value copy"""
    user_id = session['user_id']
    from models.vault_item import VaultItem
    from models.note import Note
    
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id).first()
    category = ""
    label = ""
    if item:
        category = item.category
        label = item.label
    else:
        note = Note.query.filter_by(id=item_id, user_id=user_id).first()
        if note:
            category = 'notes'
            label = note.title
            
    audit_service.log_action(
        user_id=user_id,
        action='copy',
        details={'item_id': item_id, 'category': category, 'label': label}
    )
    return jsonify({'success': True})


@activity_bp.route('/export')
@login_required
def export_activity():
    """Export activity logs"""
    import json
    from flask import Response
    
    user_id = session['user_id']
    activities = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.timestamp.desc()).all()
    
    data = [{
        'action': activity.action,
        'details': activity.details,
        'success': activity.success,
        'ip_address': activity.ip_address,
        'user_agent': activity.user_agent,
        'timestamp': activity.timestamp.isoformat() + 'Z'
    } for activity in activities]
    
    audit_service.log_action(
        user_id=user_id,
        action='download',
        details={'file': 'activity_export.json'}
    )
    
    return Response(
        json.dumps(data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=activity_export.json'}
    )


@activity_bp.route('/clear', methods=['POST'])
@login_required
def clear_activity():
    """Clear all activity logs"""
    user_id = session['user_id']
    
    ActivityLog.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    audit_service.log_action(
        user_id=user_id,
        action='clear_activity',
        details={'ip': request.remote_addr}
    )
    
    return jsonify({'success': True})


@activity_bp.route('/<int:log_id>', methods=['GET'])
@login_required
def get_activity_detail(log_id):
    """Get detail of a single activity log"""
    user_id = session['user_id']
    log = ActivityLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not log:
        return jsonify({'error': 'Log not found'}), 404
    return jsonify({
        'log': {
            'id': log.id,
            'action': log.action,
            'details': log.details,
            'success': log.success,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'timestamp': log.timestamp.isoformat()
        }
    })


@activity_bp.route('/login-history', methods=['GET'])
@login_required
def get_login_history():
    """Get user login history"""
    user_id = session['user_id']
    logs = ActivityLog.query.filter_by(user_id=user_id, action='login').all()
    return jsonify({
        'history': [{
            'id': log.id,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'timestamp': log.timestamp.isoformat(),
            'success': log.success
        } for log in logs]
    })