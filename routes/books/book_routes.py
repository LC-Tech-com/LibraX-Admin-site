from flask import Blueprint, render_template
from flask_login import login_required
import os
import qrcode
from random import randint
from database import db
from models import Book, BookCategory
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import func

books = Blueprint("books", __name__, url_prefix="/books")


@books.route("/")
@login_required
def books_page():

    search = request.args.get("search", "")

    query = Book.query

    if search:

        query = query.filter(
            (Book.book_id.contains(search))
            | (Book.title.contains(search))
            | (Book.author.contains(search))
        )

    books_list = query.order_by(Book.created_at.desc()).all()

    total_copies = db.session.query(
        func.sum(Book.total_copies)
    ).scalar() or 0

    borrowed_copies = db.session.query(
        func.sum(
            Book.total_copies - Book.available_copies
        )
    ).scalar() or 0

    available_copies = db.session.query(
        func.sum(Book.available_copies)
    ).scalar() or 0

    total_books = Book.query.count()

    available_books = Book.query.filter(Book.available_copies > 0).count()

    borrowed_books = Book.query.filter(Book.available_copies < Book.total_copies).count()

    categories = {}

    for category in BookCategory.query.all():
        categories[category.id] = category

    return render_template(
        "books/books.html",
        books=books_list,
        total_books=total_books,
        available_books=available_books,
        borrowed_books=borrowed_books,
        categories=categories,
        search=search,
        total_copies=total_copies,
        borrowed_copies=borrowed_copies,
        available_copies=available_copies
    )


@books.route("/add", methods=["GET", "POST"])
@login_required
def add_book():

    categories = BookCategory.query.all()

    if request.method == "POST":

        book_id = "B" + str(randint(100000, 999999))

        while Book.query.filter_by(book_id=book_id).first():
            book_id = "B" + str(randint(100000, 999999))

        qr_filename = f"{book_id}.png"
        qr_path = os.path.join("static", "qrcodes", qr_filename)

        qr = qrcode.make(book_id)
        qr.save(qr_path)

        total_copies = int(request.form.get("total_copies", 1))

        book = Book(
            book_id=book_id,
            title=request.form.get("title"),
            author=request.form.get("author"),
            category_id=request.form.get("category_id"),
            publisher=request.form.get("publisher"),
            publication_year=request.form.get("publication_year") or None,
            isbn=request.form.get("isbn"),
            total_copies=total_copies,
            available_copies=total_copies,
            qr_code_path=qr_path,
        )

        db.session.add(book)
        db.session.commit()

        return redirect(url_for("books.books_page"))

    return render_template("books/add_book.html", categories=categories)


@books.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):

    book = Book.query.get_or_404(id)

    categories = BookCategory.query.all()

    if request.method == "POST":

        book.title = request.form.get("title")
        book.author = request.form.get("author")
        book.category_id = request.form.get("category_id")
        book.publisher = request.form.get("publisher")
        book.publication_year = request.form.get("publication_year") or None
        book.isbn = request.form.get("isbn")

        new_total = int(request.form.get("total_copies", book.total_copies))

        borrowed = book.total_copies - book.available_copies

        book.total_copies = new_total

        book.available_copies = max(0, new_total - borrowed)

        db.session.commit()

        return redirect(url_for("books.books_page"))

    return render_template("books/edit_book.html", book=book, categories=categories)


@books.route("/delete/<int:id>")
@login_required
def delete_book(id):

    book = Book.query.get_or_404(id)

    if book.qr_code_path and os.path.exists(book.qr_code_path):
        os.remove(book.qr_code_path)

    db.session.delete(book)
    db.session.commit()

    return redirect(url_for("books.books_page"))
