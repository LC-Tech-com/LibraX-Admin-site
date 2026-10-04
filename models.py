from datetime import datetime
from flask_login import UserMixin
from database import db


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.Enum("super_admin", "admin"), default="admin")
    profile_image = db.Column(
        db.String(255),
        default="default.png"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BookCategory(db.Model):
    __tablename__ = "book_categories"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum("active", "inactive"), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(6), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    face_registered = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum("active", "inactive"), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserFace(db.Model):
    __tablename__ = "user_faces"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(6), db.ForeignKey("users.user_id"), nullable=False)
    image_path = db.Column(db.String(255))
    embedding_path = db.Column(db.String(255))
    face_version = db.Column(db.Integer, default=1)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey("book_categories.id"))
    publisher = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    isbn = db.Column(db.String(50))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    qr_code_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"

    id = db.Column(db.Integer, primary_key=True)

    transaction_id = db.Column(db.String(30), unique=True, nullable=False)

    user_id = db.Column(db.String(6), db.ForeignKey("users.user_id"), nullable=False)

    book_id = db.Column(db.String(10), db.ForeignKey("books.book_id"), nullable=False)

    borrow_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)

    status = db.Column(db.Enum("borrowed", "returned", "overdue"), default="borrowed")


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(6))
    book_id = db.Column(db.String(10))

    action = db.Column(
        db.Enum("face_login", "borrow", "return", "register_user", "register_book")
    )

    details = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FaceRecognitionLog(db.Model):
    __tablename__ = "face_recognition_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(6))

    confidence = db.Column(db.Float)

    status = db.Column(db.Enum("matched", "failed"))

    image_path = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)

    setting_key = db.Column(db.String(100), unique=True, nullable=False)

    setting_value = db.Column(db.String(255), nullable=False)

    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    transaction_id = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.String(6),
        nullable=False
    )

    book_id = db.Column(
        db.String(10),
        nullable=False
    )

    borrow_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    due_date = db.Column(
        db.DateTime,
        nullable=False
    )

    return_date = db.Column(
        db.DateTime
    )

    status = db.Column(
        db.Enum(
            "Borrowed",
            "Returned",
            "Overdue"
        ),
        default="Borrowed"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )