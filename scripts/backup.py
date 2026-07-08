#!/usr/bin/env python
"""
Backup script for Private Vault
Run: python scripts/backup.py [--export] [--restore BACKUP_ID]
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from models.user import User
from services.backup import backup_service
from services.encryption import encryption_service
from getpass import getpass

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Private Vault Backup Tool')
    parser.add_argument('--export', action='store_true', help='Export backup')
    parser.add_argument('--restore', help='Restore backup with ID')
    parser.add_argument('--list', action='store_true', help='List all backups')
    parser.add_argument('--delete', help='Delete backup with ID')
    parser.add_argument('--password', help='Backup password (for encrypted backups)')
    parser.add_argument('--user', default='admin', help='Username (default: admin)')
    return parser.parse_args()

def get_user(username):
    """Get user by username"""
    return User.query.filter_by(username=username).first()

def list_backups(user_id):
    """List all backups for user"""
    backups = backup_service.get_backup_history(user_id)
    
    if not backups:
        print("\n📭 No backups found")
        return
    
    print("\n" + "="*80)
    print(f"{'ID':<12} {'Date':<25} {'Size':<12} {'Items':<8} {'Status':<12} {'Encrypted'}")
    print("-"*80)
    
    for backup in backups:
        date = backup['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        size = f"{backup['file_size'] / 1024:.1f} KB"
        status = backup['status']
        encrypted = "🔒" if backup['encrypted'] else "🔓"
        
        print(f"{backup['backup_id']:<12} {date:<25} {size:<12} {backup['items_count']:<8} {status:<12} {encrypted}")
    
    print("="*80)

def export_backup(user_id, password=None):
    """Export backup"""
    print("\n📤 Creating backup...")
    
    result = backup_service.create_backup(
        user_id=user_id,
        password=password,
        include_files=True,
        include_settings=True
    )
    
    print(f"\n✅ Backup created successfully!")
    print(f"📋 Backup ID: {result['backup_id']}")
    print(f"📁 File: {result['filename']}")
    print(f"📊 Size: {result['size'] / 1024:.1f} KB")
    print(f"📦 Items: {result['items']}")
    print(f"📄 Files: {result['files']}")
    
    if password:
        print("🔒 Backup encrypted with password")
    else:
        print("🔓 Backup not encrypted")
    
    # Get the actual file path
    filepath = os.path.join(backup_service.backup_dir, result['filename'])
    print(f"💾 Location: {filepath}")

def restore_backup(user_id, backup_id, password=None):
    """Restore from backup"""
    print(f"\n🔄 Restoring backup: {backup_id}")
    
    # Confirm
    confirm = input("\n⚠️ This will replace all current data. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Restore cancelled")
        return
    
    try:
        result = backup_service.restore_backup(
            user_id=user_id,
            backup_id=backup_id,
            password=password
        )
        
        print(f"\n✅ Backup restored successfully!")
        print(f"📦 Items restored: {result['items']}")
        print(f"📝 Notes restored: {result['notes']}")
        
    except Exception as e:
        print(f"\n❌ Error restoring backup: {str(e)}")

def delete_backup(user_id, backup_id):
    """Delete backup"""
    print(f"\n🗑️ Deleting backup: {backup_id}")
    
    confirm = input("Are you sure? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Delete cancelled")
        return
    
    success = backup_service.delete_backup(user_id, backup_id)
    
    if success:
        print("✅ Backup deleted successfully")
    else:
        print("❌ Error deleting backup")

def main():
    """Main entry point"""
    args = parse_args()
    
    app = create_app()
    
    with app.app_context():
        # Get user
        user = get_user(args.user)
        if not user:
            print(f"❌ User not found: {args.user}")
            print("Run create_admin.py to create an admin user")
            sys.exit(1)
        
        print(f"\n🔐 Private Vault Backup Tool")
        print(f"👤 User: {user.username}")
        
        # List backups
        if args.list:
            list_backups(user.id)
            return
        
        # Export backup
        if args.export:
            export_backup(user.id, args.password)
            return
        
        # Restore backup
        if args.restore:
            restore_backup(user.id, args.restore, args.password)
            return
        
        # Delete backup
        if args.delete:
            delete_backup(user.id, args.delete)
            return
        
        # Interactive mode
        print("\nOptions:")
        print("  1. List backups")
        print("  2. Create backup")
        print("  3. Restore backup")
        print("  4. Delete backup")
        print("  0. Exit")
        
        while True:
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice == '0':
                    print("Goodbye!")
                    break
                elif choice == '1':
                    list_backups(user.id)
                elif choice == '2':
                    password = None
                    encrypt = input("Encrypt backup with password? (y/N): ")
                    if encrypt.lower() == 'y':
                        password = getpass("Enter backup password: ")
                    export_backup(user.id, password)
                elif choice == '3':
                    backup_id = input("Enter backup ID: ").strip()
                    if backup_id:
                        password = None
                        encrypted = input("Is backup encrypted? (y/N): ")
                        if encrypted.lower() == 'y':
                            password = getpass("Enter backup password: ")
                        restore_backup(user.id, backup_id, password)
                elif choice == '4':
                    backup_id = input("Enter backup ID: ").strip()
                    if backup_id:
                        delete_backup(user.id, backup_id)
                else:
                    print("❌ Invalid option")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)