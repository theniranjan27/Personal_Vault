#!/usr/bin/env python
"""
Create admin user for Private Vault
Run: python scripts/create_admin.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from models.user import User
from services.hashing import password_service
from services.encryption import encryption_service
from services.security import security_service
from getpass import getpass
import re

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def validate_pin(pin):
    """Validate PIN"""
    if len(pin) != 6:
        return False, "PIN must be exactly 6 digits"
    if not pin.isdigit():
        return False, "PIN must contain only numbers"
    return True, "PIN is valid"

def create_admin():
    """Create admin user"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("🔐 Private Vault - Admin Setup")
        print("="*50 + "\n")
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"⚠️ Admin user already exists: {existing_admin.username}")
            response = input("Do you want to create another admin? (y/N): ")
            if response.lower() != 'y':
                print("Exiting...")
                return
        
        # Get username
        while True:
            username = input("Enter admin username (min 3 chars): ").strip()
            if len(username) < 3:
                print("❌ Username must be at least 3 characters")
                continue
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                print("❌ Username can only contain letters, numbers, and underscores")
                continue
            # Check if username exists
            if User.query.filter_by(username=username).first():
                print("❌ Username already exists")
                continue
            break
        
        # Get email
        while True:
            email = input("Enter admin email: ").strip()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                print("❌ Invalid email format")
                continue
            if User.query.filter_by(email=email).first():
                print("❌ Email already exists")
                continue
            break
        
        # Get full name
        while True:
            full_name = input("Enter admin full name: ").strip()
            if len(full_name) < 2:
                print("❌ Full name must be at least 2 characters")
                continue
            break
        
        # Get master password
        while True:
            print("\n📌 Master Password Requirements:")
            print("  • At least 8 characters")
            print("  • At least one uppercase letter")
            print("  • At least one lowercase letter")
            print("  • At least one number")
            print("  • At least one special character (!@#$%^&*(),.?\":{}|<>)\n")
            
            password = getpass("Enter master password: ")
            valid, message = validate_password(password)
            if not valid:
                print(f"❌ {message}")
                continue
            
            confirm = getpass("Confirm master password: ")
            if password != confirm:
                print("❌ Passwords do not match")
                continue
            
            break
        
        # Get PIN
        while True:
            print("\n📌 PIN Requirements:")
            print("  • Exactly 6 digits\n")
            
            pin = getpass("Enter 6-digit PIN: ")
            valid, message = validate_pin(pin)
            if not valid:
                print(f"❌ {message}")
                continue
            
            confirm = getpass("Confirm PIN: ")
            if pin != confirm:
                print("❌ PINs do not match")
                continue
            
            break
        
        # Create admin user
        try:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='Admin User',
                master_password_hash=password_service.hash_password('Admin@123'),
                pin_hash=password_service.hash_pin('123456'),
                is_admin=True,
                is_active=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            # Create default security methods
            security_service._create_default_methods(admin.id)
            
            print("\n" + "="*50)
            print("✅ Admin user created successfully!")
            print("="*50)
            print(f"📋 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"👤 Name: {full_name}")
            print(f"🆔 User ID: {admin.id}")
            print("\n⚠️ Please save these credentials securely.")
            print("🔐 You can now login at: https://localhost:5000")
            print("="*50 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)