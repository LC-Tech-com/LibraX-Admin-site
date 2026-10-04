from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from werkzeug.security import check_password_hash
from flask_login import login_required, current_user
from models import Admin
from flask_login import logout_user

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            print("LOGIN SUCCESS:", admin.username)
            return redirect(url_for("dashboard.dashboard_page"))

    return render_template("auth/login.html")


@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html", admin=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for("auth.login"))
