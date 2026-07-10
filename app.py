from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config.config import Config
import logging
import os
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure logging
    if not app.debug:
        setup_logging(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.identity import identity_bp
    from routes.banking import banking_bp
    from routes.passwords import passwords_bp
    from routes.notes import notes_bp
    from routes.documents import documents_bp
    from routes.emergency import emergency_bp
    from routes.digital_assets import digital_assets_bp
    from routes.activity import activity_bp
    from routes.backup import backup_bp
    from routes.security import security_bp
    from routes.settings import settings_bp
    
    # Register with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(identity_bp, url_prefix='/identity')
    app.register_blueprint(banking_bp, url_prefix='/banking')
    app.register_blueprint(passwords_bp, url_prefix='/passwords')
    app.register_blueprint(notes_bp, url_prefix='/notes')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(emergency_bp, url_prefix='/emergency')
    app.register_blueprint(digital_assets_bp, url_prefix='/digital-assets')
    app.register_blueprint(activity_bp, url_prefix='/activity')
    app.register_blueprint(backup_bp, url_prefix='/backup')
    app.register_blueprint(security_bp, url_prefix='/security')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Error handlers
    register_error_handlers(app)
    
    return app

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Vault application startup')

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server error: {error}')
        return {'error': 'Internal server error'}, 500

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')