from flask import Blueprint, request, jsonify, session, render_template
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
    return render_template('settings/activity.html')


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
    
    query = ActivityLog.query.filter_by(user_id=user_id)
    
    if action and action != 'all':
        query = query.filter_by(action=action)
    
    if search:
        query = query.filter(ActivityLog.details.ilike(f'%{search}%'))
    
    if date_filter:
        date = datetime.strptime(date_filter, '%Y-%m-%d')
        query = query.filter(
            ActivityLog.timestamp >= date,
            ActivityLog.timestamp < date + timedelta(days=1)
        )
    
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
            'timestamp': activity.timestamp.isoformat()
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
    
    audit_service.log_action(
        user_id=user_id,
        action='reveal_sensitive',
        details={'item_id': item_id}
    )
    
    return jsonify({'success': True})


@activity_bp.route('/export')
@login_required
def export_activity():
    """Export activity logs"""
    user_id = session['user_id']
    import json
    
    activities = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.timestamp.desc()).all()
    
    data = [{
        'action': activity.action,
        'details': activity.details,
        'success': activity.success,
        'ip_address': activity.ip_address,
        'user_agent': activity.user_agent,
        'timestamp': activity.timestamp.isoformat()
    } for activity in activities]
    
    return jsonify(data)


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