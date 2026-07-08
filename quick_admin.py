import sys
sys.path.insert(0, '.')

from app import create_app, db
from models.user import User
from models.security_method import SecurityMethod
from services.hashing import password_service
from services.security import security_service

app = create_app()

with app.app_context():
    # Check if admin user exists
    user = User.query.filter_by(username='admin').first()
    
    if user:
        print("Existing admin user found. Re-seeding passwords...")
        user.master_password_hash = password_service.hash_password('Admin@123')
        user.pin_hash = password_service.hash_pin('123456')
        db.session.commit()
    else:
        print("Admin user not found. Creating new admin...")
        user = User(
            username='admin',
            email='admin@example.com',
            full_name='Admin User',
            master_password_hash=password_service.hash_password('Admin@123'),
            pin_hash=password_service.hash_pin('123456'),
            is_admin=True,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default security methods since this is a new user
        security_service._create_default_methods(user.id)
    
    print("[SUCCESS] Admin seeded successfully!")
    print("Username: admin")
    print("Password: Admin@123")
    print("PIN: 123456")