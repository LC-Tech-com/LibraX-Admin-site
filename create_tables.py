from app import app
from database import db
from models import (
    Admin,
    User,
    UserFace,
    Book,
    BookCategory,
    ActivityLog,
    Transaction
)
with app.app_context():
    db.create_all()
    print("✓ All tables created successfully")
