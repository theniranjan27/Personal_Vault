import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.activity_log import ActivityLog
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Print all activity logs timestamps
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    print("All logs count:", len(logs))
    for log in logs[:5]:
        print(f"Log ID: {log.id}, Action: {log.action}, Timestamp: {log.timestamp}")
        
    # Try querying with standard query
    date_filter = '2026-07-10'
    date = datetime.strptime(date_filter, '%Y-%m-%d')
    res1 = ActivityLog.query.filter(
        ActivityLog.timestamp >= date,
        ActivityLog.timestamp < date + timedelta(days=1)
    ).all()
    print("\nRes1 (standard):", len(res1))
    
    # Try querying with db.func.date
    res2 = ActivityLog.query.filter(
        db.func.date(ActivityLog.timestamp) == date_filter
    ).all()
    print("Res2 (db.func.date):", len(res2))
