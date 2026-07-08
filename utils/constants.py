VAULT_CATEGORIES = {
    'identity': {
        'name': 'Identity',
        'icon': '🪪',
        'fields': ['Aadhaar', 'PAN', 'Passport', 'Driving License', 'Voter ID', 'Birth Certificate']
    },
    'banking': {
        'name': 'Banking',
        'icon': '🏦',
        'fields': ['Bank Name', 'Account Number', 'IFSC', 'UPI ID', 'Card Details']
    },
    'passwords': {
        'name': 'Passwords',
        'icon': '🔑',
        'fields': ['Website', 'Username', 'Password', 'Notes']
    },
    'notes': {
        'name': 'Notes',
        'icon': '📝',
        'fields': ['Title', 'Content', 'Category']
    },
    'documents': {
        'name': 'Documents',
        'icon': '📄',
        'fields': ['Title', 'Type', 'File', 'Notes']
    },
    'emergency': {
        'name': 'Emergency',
        'icon': '🚨',
        'fields': ['Contact Name', 'Phone', 'Relationship', 'Notes']
    },
    'digital_assets': {
        'name': 'Digital Assets',
        'icon': '💻',
        'fields': ['Name', 'Type', 'URL', 'Credentials']
    }
}

SECURITY_METHODS = {
    'master_password': {
        'name': 'Master Password',
        'enabled': True,
        'required': True,
        'description': 'Strong password for initial authentication'
    },
    'pin': {
        'name': 'PIN Verification',
        'enabled': True,
        'required': True,
        'description': '6-digit PIN for second authentication layer'
    },
    'email_otp': {
        'name': 'Email OTP',
        'enabled': False,
        'required': False,
        'description': 'One-time password sent to registered email'
    },
    'authenticator_otp': {
        'name': 'Authenticator App OTP',
        'enabled': False,
        'required': False,
        'description': 'TOTP from Google Authenticator or similar'
    },
    'trusted_device': {
        'name': 'Trusted Device',
        'enabled': False,
        'required': False,
        'description': 'Verify trusted devices for login'
    },
    'webauthn': {
        'name': 'Passkeys / WebAuthn',
        'enabled': False,
        'required': False,
        'description': 'Biometric or hardware-based authentication'
    },
    'hardware_key': {
        'name': 'Hardware Security Key',
        'enabled': False,
        'required': False,
        'description': 'YubiKey or similar hardware security key'
    },
    'ip_restriction': {
        'name': 'IP Restriction',
        'enabled': False,
        'required': False,
        'description': 'Restrict login to specific IP addresses'
    },
    'recovery_codes': {
        'name': 'Recovery Codes',
        'enabled': False,
        'required': False,
        'description': 'One-time recovery codes for account recovery'
    },
    'emergency_lock': {
        'name': 'Emergency Lock Mode',
        'enabled': False,
        'required': False,
        'description': 'Lock account in case of emergency'
    },
    'auto_logout': {
        'name': 'Auto Logout',
        'enabled': True,
        'required': False,
        'description': 'Automatically logout after inactivity'
    }
}

VAULT_TYPES = {
    'identity': 'Identity Document',
    'banking': 'Bank Account',
    'password': 'Password Entry',
    'note': 'Note',
    'document': 'Document',
    'emergency': 'Emergency Contact',
    'digital_asset': 'Digital Asset'
}

SENSITIVE_FIELDS = {
    'aadhaar': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}',
    'pan': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
    'passport': r'[A-Z0-9]{6,9}',
    'account_number': r'\d{9,18}',
    'ifsc': r'[A-Z]{4}0[A-Z0-9]{6}',
    'upi': r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+',
    'card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
    'phone': r'\+?[0-9]{10,15}',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
}

LOG_ACTIONS = {
    'login': 'User logged in',
    'logout': 'User logged out',
    'login_failed': 'Login attempt failed',
    'add_item': 'Item added to vault',
    'edit_item': 'Item updated',
    'delete_item': 'Item deleted',
    'view_item': 'Item viewed',
    'copy_item': 'Item copied',
    'reveal_sensitive': 'Sensitive value revealed',
    'upload_file': 'File uploaded',
    'download_file': 'File downloaded',
    'delete_file': 'File deleted',
    'backup_created': 'Backup created',
    'backup_restored': 'Backup restored',
    'security_changed': 'Security settings changed',
    'settings_changed': 'General settings changed'
}