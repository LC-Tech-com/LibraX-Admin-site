from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)
from flask_login import login_required
from datetime import datetime, timedelta
from random import randint
from sqlalchemy import or_
from database import db
from models import (
    User,
    Book,
    Transaction,
    ActivityLog
)

transactions = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions"
)
@transactions.route("/")
@login_required
def transactions_page():

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Transaction.query

    if search:

        query = query.filter(
            db.or_(
                Transaction.transaction_id.ilike(f"%{search}%"),
                Transaction.user_id.ilike(f"%{search}%"),
                Transaction.book_id.ilike(f"%{search}%"),
                Transaction.status.ilike(f"%{search}%")
            )
        )

    transactions_list = query.order_by(
        Transaction.created_at.desc()
    ).all()

    book_map = {
        book.book_id: book.title
        for book in Book.query.all()
    }

    total_transactions = Transaction.query.count()

    active_loans = Transaction.query.filter_by(
        status="Borrowed"
    ).count()

    returned_books = Transaction.query.filter_by(
        status="Returned"
    ).count()

    overdue_books = Transaction.query.filter_by(
        status="Overdue"
    ).count()

    return render_template(
        "transactions/transactions.html",
        transactions=transactions_list,
        book_map=book_map,
        total_transactions=total_transactions,
        active_loans=active_loans,
        returned_books=returned_books,
        overdue_books=overdue_books,
        search=search
    )