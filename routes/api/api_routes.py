import os
import shutil
from models import (
    Book,
    BookCategory,
    Transaction
)
from datetime import datetime, timedelta
from random import randint

from flask import (
    Blueprint,
    jsonify,
    request
)

from database import db

from models import (
    User,
    Book,
    Transaction,
    ActivityLog
)

from utils.face_utils.face_service import FaceService


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api.route("/test")
def test_api():

    return jsonify({
        "success": True,
        "message": "LibraX API Running"
    })


@api.route("/face-authenticate", methods=["POST"])
def face_authenticate():

    print(db.engine.url)
    uploaded_file = request.files.get("face_image")

    if not uploaded_file:

        return jsonify({
            "success": False,
            "message": "Image is required"
        }), 400

    os.makedirs(
        "static/uploads",
        exist_ok=True
    )

    temp_path = os.path.join(
        "static/uploads",
        f"auth_{uploaded_file.filename}"
    )

    uploaded_file.save(temp_path)

    try:

        face_service = FaceService()

        result = face_service.authenticate_face(
            image_path=temp_path
        )

        if result["authenticated"]:
            print("DB URL:", db.engine.url)

            for u in User.query.all():
                print("USER:", u.user_id, u.full_name)        
            user = User.query.filter_by(
                user_id=result["user_id"]
            ).first()

            if not user:
                return jsonify({
                    "success": False,
                    "message": f"User {result['user_id']} not found in database"
                })

            return jsonify({
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "name": user.full_name,
                    "roll_number": user.roll_no,
                    "department": user.department
                },
                "score": result["score"]
            })

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


@api.route("/borrow-book", methods=["POST"])
def borrow_book():

    data = request.json

    user_id = data.get("user_id")
    book_id = data.get("book_id")

    user = User.query.filter_by(
        user_id=user_id
    ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if not book:

        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    if book.available_copies <= 0:

        return jsonify({
            "success": False,
            "message": "Book unavailable"
        }), 400

    active_loans = Transaction.query.filter_by(
        user_id=user_id,
        status="Borrowed"
    ).count()

    if active_loans >= 3:

        return jsonify({
            "success": False,
            "message": "Maximum 3 books allowed"
        }), 400

    existing = Transaction.query.filter_by(
        user_id=user_id,
        book_id=book_id,
        status="Borrowed"
    ).first()

    if existing:

        return jsonify({
            "success": False,
            "message": "Book already borrowed"
        }), 400

    transaction_id = "T" + str(
        randint(100000, 999999)
    )

    borrow_date = datetime.utcnow()

    due_date = borrow_date + timedelta(
        days=14
    )

    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date,
        status="Borrowed"
    )

    book.available_copies -= 1

    log = ActivityLog(
        user_id=user_id,
        book_id=book_id,
        action="borrow",
        details=f"Borrowed {book_id}"
    )

    db.session.add(transaction)
    db.session.add(log)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book borrowed",
        "transaction_id": transaction_id
    })


@api.route("/return-book", methods=["POST"])
def return_book():

    data = request.json

    user_id = data.get("user_id")
    book_id = data.get("book_id")

    transaction = Transaction.query.filter_by(
        user_id=user_id,
        book_id=book_id,
        status="Borrowed"
    ).first()

    if not transaction:

        return jsonify({
            "success": False,
            "message": "No active loan found"
        }), 404

    transaction.status = "Returned"
    transaction.return_date = datetime.utcnow()

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if book:
        book.available_copies += 1

    log = ActivityLog(
        user_id=user_id,
        book_id=book_id,
        action="return",
        details=f"Returned {book_id}"
    )

    db.session.add(log)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book returned"
    })


@api.route("/perform-book-action", methods=["POST"])
def perform_book_action():

    data = request.json

    user_id = data.get("user_id")
    book_id = data.get("book_id")

    active_transaction = Transaction.query.filter_by(
        user_id=user_id,
        book_id=book_id,
        status="Borrowed"
    ).first()

    # RETURN
    if active_transaction:

        active_transaction.status = "Returned"
        active_transaction.return_date = datetime.utcnow()

        book = Book.query.filter_by(
            book_id=book_id
        ).first()

        if book:
            book.available_copies += 1

        log = ActivityLog(
            user_id=user_id,
            book_id=book_id,
            action="return",
            details=f"Returned {book_id}"
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({
            "success": True,
            "action": "return",
            "message": "Book returned successfully"
        })

    # BORROW

    user = User.query.filter_by(
        user_id=user_id
    ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "User not found"
        })

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if not book:

        return jsonify({
            "success": False,
            "message": "Book not found"
        })

    if book.available_copies <= 0:

        return jsonify({
            "success": False,
            "message": "Book unavailable"
        })

    active_loans = Transaction.query.filter_by(
        user_id=user_id,
        status="Borrowed"
    ).count()

    if active_loans >= 3:

        return jsonify({
            "success": False,
            "message": "Maximum 3 books allowed"
        })

    transaction_id = "T" + str(randint(100000, 999999))

    borrow_date = datetime.utcnow()

    due_date = borrow_date + timedelta(days=14)

    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date,
        status="Borrowed"
    )

    book.available_copies -= 1

    log = ActivityLog(
        user_id=user_id,
        book_id=book_id,
        action="borrow",
        details=f"Borrowed {book_id}"
    )

    db.session.add(transaction)
    db.session.add(log)

    db.session.commit()

    return jsonify({
        "success": True,
        "action": "borrow",
        "message": "Book borrowed successfully"
    })

@api.route("/check-book-action", methods=["POST"])
def check_book_action():

    data = request.get_json()

    user_id = data.get("user_id")
    book_id = data.get("book_id")

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found"
        })

    active_transaction = Transaction.query.filter_by(
        user_id=user_id,
        book_id=book_id,
        status="Borrowed"
    ).first()

    action = "return" if active_transaction else "borrow"

    category_name = ""

    if book.category_id:
        category = BookCategory.query.get(book.category_id)
        if category:
            category_name = category.category_name

    return jsonify({
        "success": True,
        "action": action,
        "book": {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author or "",
            "category": category_name,
            "barcode_value": book.book_id
        }
    })