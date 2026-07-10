from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app import db, csrf
from models.user import User
from services.hashing import password_service
from services.audit import audit_service
from services.session import session_service
from services.security import security_service
from utils.decorators import rate_limit
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session and session.get('pin_verified'):
        return redirect(url_for('dashboard.index'))
    return render_template('login/master_password.html')


@auth_bp.route('/pin', methods=['GET'])
def pin_page():
    if 'user_id' in session and session.get('pin_verified'):
        return redirect(url_for('dashboard.index'))

    if not session.get('master_verified'):
        session.clear()
        return redirect(url_for('auth.login_page'))

    return render_template('login/pin.html')


@auth_bp.route('/verify-master', methods=['POST'])
@csrf.exempt
@rate_limit(max_attempts=5, window_minutes=15)
def verify_master():
    """Verify master password"""
    try:
        print("="*50)
        print("VERIFY MASTER STARTED")
        
        data = request.get_json()
        print("STEP 1: data ok", data)
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        master_password = data.get('master_password')
        print("STEP 1.5: master_password:", master_password)
        
        if not master_password:
            return jsonify({'error': 'Master password required'}), 400
        
        print("STEP 2: getting user from database")
        user = User.query.first()
        print("STEP 2.5: user:", user)
        
        if not user:
            return jsonify({'error': 'User not found. Please setup admin.'}), 401
        
        print("STEP 3: checking lock")
        if user.locked_until and user.locked_until > datetime.utcnow():
            print("STEP 3.5: user is locked")
            return jsonify({'error': 'Account locked. Try again later.'}), 403
        
        print("STEP 4: verifying password")
        ok = password_service.verify_password(master_password, user.master_password_hash)
        print("STEP 5: password ok:", ok)
        
        if not ok:
            print("STEP 6: password failed - logging attempt")
            audit_service.log_login_attempt(
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', 'Unknown'),
                success=False,
                failure_reason='Invalid master password'
            )
            print("STEP 7: audit logged - handling failed attempt")
            result = security_service.handle_failed_attempt(user)
            print("STEP 8: failed attempt handled:", result)
            if result.get('locked'):
                return jsonify({'error': f'Account locked for {result["lockout_minutes"]} minutes'}), 403
            return jsonify({'error': 'Invalid master password'}), 401
        
        print("STEP 9: password ok - resetting attempts")
        security_service.reset_attempts(user)
        
        print("STEP 10: storing session")
        session.clear()
        session['master_verified'] = True
        session['user_id'] = user.id
        session['pin_verified'] = False
        
        print("STEP 11: returning success")
        return jsonify({'success': True, 'redirect': '/auth/pin'})
        
    except Exception as e:
        print(f"ERROR in verify_master: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify-pin', methods=['POST'])
@csrf.exempt
def verify_pin():
    data = request.get_json(silent=True) or request.form
    pin = data.get('pin')

    if not pin:
        return jsonify({'error': 'PIN required'}), 400

    if not session.get('master_verified'):
        return jsonify({'error': 'Master password verification required'}), 401

    user = User.query.get(session.get('user_id'))

    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 401

    if not password_service.verify_pin(pin, user.pin_hash):
        return jsonify({'error': 'Invalid PIN'}), 401

    session['pin_verified'] = True
    session.pop('master_verified', None)

    audit_service.log_action(
        user_id=user.id,
        action='login',
        details={'ip': request.remote_addr}
    )

    return jsonify({'success': True, 'redirect': url_for('dashboard.index')})


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        audit_service.log_action(
            user_id=user_id,
            action='logout',
            details={'ip': request.remote_addr}
        )
    session.clear()
    return redirect(url_for('auth.login_page'))