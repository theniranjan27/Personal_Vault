from functools import wraps
from flask import session, jsonify, request, redirect, url_for
from models.user import User
from models.login_attempt import LoginAttempt
from datetime import datetime, timedelta
import os
import re


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not session.get('pin_verified'):
            return jsonify({'error': 'PIN verification required'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def login_required_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        
        if not session.get('pin_verified'):
            return redirect(url_for('auth.pin_page'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('auth.login_page'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not session.get('pin_verified'):
            return jsonify({'error': 'PIN verification required'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_attempts=5, window_minutes=15):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            endpoint = request.endpoint
            
            attempts = LoginAttempt.query.filter_by(
                ip_address=ip,
                endpoint=endpoint,
                success=False
            ).filter(
                LoginAttempt.attempt_time > datetime.utcnow() - timedelta(minutes=window_minutes)
            ).count()
            
            if attempts >= max_attempts:
                return jsonify({
                    'error': 'Too many failed attempts. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_activity(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from services.audit import AuditService
        audit = AuditService()
        
        try:
            response = f(*args, **kwargs)
            
            if 'user_id' in session:
                audit.log_action(
                    user_id=session['user_id'],
                    action=f.__name__,
                    details={'endpoint': request.endpoint, 'method': request.method}
                )
            
            return response
        except Exception as e:
            audit.log_action(
                user_id=session.get('user_id'),
                action=f.__name__,
                details={'error': str(e)},
                success=False
            )
            raise
    return decorated_function


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'JSON required'}), 400
            
            data = request.get_json()
            errors = validate_schema(data, schema)
            if errors:
                return jsonify({'errors': errors}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_schema(data, schema):
    errors = {}
    for field, rules in schema.items():
        if rules.get('required') and field not in data:
            errors[field] = 'Field is required'
        elif field in data:
            value = data[field]
            if rules.get('type') == 'string' and not isinstance(value, str):
                errors[field] = 'Must be a string'
            elif rules.get('type') == 'number' and not isinstance(value, (int, float)):
                errors[field] = 'Must be a number'
            elif rules.get('type') == 'boolean' and not isinstance(value, bool):
                errors[field] = 'Must be a boolean'
            elif rules.get('min_length') and len(value) < rules['min_length']:
                errors[field] = f'Minimum length is {rules["min_length"]}'
            elif rules.get('max_length') and len(value) > rules['max_length']:
                errors[field] = f'Maximum length is {rules["max_length"]}'
            elif rules.get('pattern') and not re.match(rules['pattern'], str(value)):
                errors[field] = 'Invalid format'
    
    return errors