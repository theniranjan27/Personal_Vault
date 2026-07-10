from flask import request, session, jsonify
from datetime import datetime, timedelta
import os
import re

class Middleware:
    def __init__(self, app):
        self.app = app
        self.setup_middleware()
    
    def setup_middleware(self):
        @self.app.before_request
        def before_request():
            self.check_session_timeout()
            self.redirect_http_to_https()
            self.add_security_headers()
            self.log_request()
        
        @self.app.after_request
        def after_request(response):
            self.add_cors_headers(response)
            return response
    
    def check_session_timeout(self):
        if 'user_id' in session and 'login_time' in session:
            login_time = datetime.fromisoformat(session['login_time'])
            timeout_minutes = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 15))
            if datetime.utcnow() - login_time > timedelta(minutes=timeout_minutes):
                session.clear()
                return jsonify({'error': 'Session expired'}), 401
    
    def redirect_http_to_https(self):
        if os.environ.get('FLASK_ENV') == 'production':
            if request.headers.get('X-Forwarded-Proto') == 'http':
                return redirect(request.url.replace('http://', 'https://'), 301)
    
    def add_security_headers(self):
        @self.app.after_request
        def security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            return response
    
    def log_request(self):
        self.app.logger.info(f'{request.method} {request.path} - {request.remote_addr}')
    
    def add_cors_headers(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

def setup_middleware(app):
    return Middleware(app)