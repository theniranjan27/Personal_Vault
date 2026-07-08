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

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'identity_bp',
    'banking_bp',
    'passwords_bp',
    'notes_bp',
    'documents_bp',
    'emergency_bp',
    'digital_assets_bp',
    'activity_bp',
    'backup_bp',
    'security_bp',
    'settings_bp'
]