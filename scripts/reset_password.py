#!/usr/bin/env python
"""
Reset admin password for Private Vault
Run: python scripts/reset_password.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from models.user import User
from services.hashing import password_service
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

def reset_password():
    """Reset admin password"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("🔑 Private Vault - Password Reset")
        print("="*50 + "\n")
        
        # Find admin users
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ No admin users found. Please run create_admin.py first.")
            return
        
        print("Admin users:")
        for i, admin in enumerate(admins, 1):
            print(f"  {i}. {admin.username} ({admin.email})")
        
        if len(admins) == 1:
            choice = 1
        else:
            while True:
                try:
                    choice = int(input("\nSelect admin user (number): "))
                    if 1 <= choice <= len(admins):
                        break
                    print(f"❌ Please enter a number between 1 and {len(admins)}")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        admin = admins[choice - 1]
        print(f"\n📋 Selected: {admin.username} ({admin.email})")
        
        # Confirm
        confirm = input(f"\nReset password for {admin.username}? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
        
        # Get new password
        while True:
            print("\n📌 Password Requirements:")
            print("  • At least 8 characters")
            print("  • At least one uppercase letter")
            print("  • At least one lowercase letter")
            print("  • At least one number")
            print("  • At least one special character (!@#$%^&*(),.?\":{}|<>)\n")
            
            password = getpass("Enter new master password: ")
            valid, message = validate_password(password)
            if not valid:
                print(f"❌ {message}")
                continue
            
            confirm_password = getpass("Confirm new master password: ")
            if password != confirm_password:
                print("❌ Passwords do not match")
                continue
            
            break
        
        # Update password
        try:
            admin.master_password_hash = password_service.hash_password(password)
            admin.failed_attempts = 0
            admin.locked_until = None
            db.session.commit()
            
            print("\n" + "="*50)
            print("✅ Password reset successfully!")
            print("="*50)
            print(f"👤 User: {admin.username}")
            print("🔐 Password has been updated")
            print("\n⚠️ Please use the new password to login.")
            print("="*50 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error resetting password: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        reset_password()
    except KeyboardInterrupt:
        print("\n\n❌ Reset cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)