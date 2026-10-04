from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime, date 
from models import (
    User,
    Book,
    Transaction,
    ActivityLog
)
from database import db
from models import User, Book

dashboard = Blueprint(
    "dashboard",
    __name__
)


@dashboard.route("/")
@login_required
def dashboard_page():

    today = date.today()

    transactions_today = ActivityLog.query.filter(
        db.func.date(ActivityLog.created_at) == today
    ).count()

    active_borrowed_books = Transaction.query.filter_by(
        status="Borrowed"
    ).order_by(
        Transaction.created_at.desc()
    ).limit(10).all()

    total_users = User.query.count()

    total_books = Book.query.count()

    available_books = Book.query.filter(
        Book.available_copies > 0
    ).count()

    # borrowed_books = Transaction.query.filter_by(
    #     status="Borrowed"
    # ).count()

    total_transactions = Transaction.query.count()

    recent_activities = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    user_map = {
        user.user_id: user.full_name
        for user in User.query.all()
    }

    book_map = {
        book.book_id: book.title
        for book in Book.query.all()
    }

    return render_template(
        "dashboard/dashboard.html",
        total_users=total_users,
        total_books=total_books,
        available_books=available_books,
        # borrowed_books=borrowed_books,
        total_transactions=total_transactions,
        transactions_today=transactions_today,
        active_borrowed_books=active_borrowed_books,
        recent_activities=recent_activities,
        user_map=user_map,
        book_map=book_map
    )