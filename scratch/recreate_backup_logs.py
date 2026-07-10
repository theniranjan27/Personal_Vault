import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("Dropping existing backup_logs table...")
    db.session.execute(text("DROP TABLE IF EXISTS backup_logs CASCADE"))
    db.session.commit()
    
    print("Recreating database tables...")
    db.create_all()
    db.session.commit()
    print("Database tables updated successfully!")
