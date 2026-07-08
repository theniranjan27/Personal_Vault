from models.activity_log import ActivityLog
from models.login_log import LoginLog
from app import db
from datetime import datetime
from flask import request, session
import json
from typing import Optional, Dict, Any

class AuditService:
    """Audit logging service for tracking all actions"""
    
    def __init__(self):
        self.app = None
    
    def init_app(self, app):
        self.app = app
    
    def log_action(self, user_id: int, action: str, details: Optional[Dict] = None, 
                   success: bool = True, ip_address: Optional[str] = None, 
                   user_agent: Optional[str] = None) -> ActivityLog:
        """Log a user action"""
        if not ip_address and request:
            ip_address = request.remote_addr
        
        if not user_agent and request:
            user_agent = request.headers.get('User-Agent', 'Unknown')
        
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=json.dumps(details) if details else None,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    def log_login_attempt(self, user_id: Optional[int], ip_address: str, 
                          user_agent: str, success: bool, 
                          failure_reason: Optional[str] = None) -> LoginLog:
        """Log a login attempt"""
        log = LoginLog(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            login_time=datetime.utcnow(),
            login_success=success,
            failure_reason=failure_reason
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    def log_logout(self, user_id: int, ip_address: Optional[str] = None) -> None:
        """Log logout event"""
        if not ip_address and request:
            ip_address = request.remote_addr
        
        # Find the most recent login log for this user
        log = LoginLog.query.filter_by(
            user_id=user_id,
            logout_time=None
        ).order_by(LoginLog.login_time.desc()).first()
        
        if log:
            log.logout_time = datetime.utcnow()
            db.session.commit()
    
    def get_user_activity(self, user_id: int, limit: int = 50, 
                          offset: int = 0) -> list:
        """Get user activity logs"""
        logs = ActivityLog.query.filter_by(user_id=user_id)\
            .order_by(ActivityLog.timestamp.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return logs
    
    def get_login_history(self, user_id: int, limit: int = 20) -> list:
        """Get user login history"""
        logs = LoginLog.query.filter_by(user_id=user_id)\
            .order_by(LoginLog.login_time.desc())\
            .limit(limit)\
            .all()
        
        return logs
    
    def get_recent_activity(self, user_id: int, limit: int = 10) -> list:
        """Get recent user activity"""
        logs = ActivityLog.query.filter_by(user_id=user_id)\
            .order_by(ActivityLog.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return logs
    
    def log_sensitive_reveal(self, user_id: int, item_id: int, 
                             item_type: str = 'vault_item') -> None:
        """Log when a sensitive value is revealed"""
        self.log_action(
            user_id=user_id,
            action='reveal_sensitive',
            details={
                'item_id': item_id,
                'item_type': item_type
            }
        )
    
    def get_audit_summary(self, user_id: int) -> dict:
        """Get audit summary for user"""
        total_actions = ActivityLog.query.filter_by(user_id=user_id).count()
        total_logins = LoginLog.query.filter_by(
            user_id=user_id,
            login_success=True
        ).count()
        failed_logins = LoginLog.query.filter_by(
            user_id=user_id,
            login_success=False
        ).count()
        
        last_login = LoginLog.query.filter_by(
            user_id=user_id,
            login_success=True
        ).order_by(LoginLog.login_time.desc()).first()
        
        return {
            'total_actions': total_actions,
            'total_logins': total_logins,
            'failed_logins': failed_logins,
            'last_login': last_login.login_time if last_login else None
        }

# Singleton instance
audit_service = AuditService()