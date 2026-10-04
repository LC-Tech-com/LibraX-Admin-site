from unittest import result

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from random import randint
from database import db
from models import User, UserFace
import os
from utils.face_utils.face_service import FaceService
import shutil

users = Blueprint("users", __name__, url_prefix="/users")

@users.route("/")
@login_required
def users_page():

    search = request.args.get("search", "")

    query = User.query

    if search:

        query = query.filter(
            (User.user_id.contains(search))
            |
            (User.full_name.contains(search))
            |
            (User.roll_no.contains(search))
        )

    all_users = query.order_by(
        User.created_at.desc()
    ).all()

    face_map = {}

    all_faces = UserFace.query.all()

    for face in all_faces:
        face_map[face.user_id] = face

    total_users = User.query.count()

    face_registered = User.query.filter_by(
    face_registered=True
    ).count()

    face_pending = total_users - face_registered

    return render_template(
        "users/users.html",
        users=all_users,
        face_map=face_map,
        total_users=total_users,
        face_registered=face_registered,
        face_pending=face_pending,
        search=search
    )

@users.route("/add", methods=["GET", "POST"])
@login_required
def add_user_page():

    if request.method == "POST":

        user_id = str(randint(100000, 999999))

        while User.query.filter_by(user_id=user_id).first():
            user_id = str(randint(100000, 999999))

        uploaded_files = request.files.getlist(
            "face_images"
        )

        if not uploaded_files:
            return "Face images are required"

        temp_paths = []

        try:

            for file in uploaded_files:

                if not file.filename:
                    continue

                temp_path = os.path.join(
                    "static",
                    "uploads",
                    f"{user_id}_{file.filename}"
                )

                file.save(temp_path)

                temp_paths.append(temp_path)

            if not temp_paths:
                return "No valid images uploaded"

            face_service = FaceService()

            result = face_service.register_multiple_faces(
                image_paths=temp_paths,
                user_id=user_id
            )

            display_face_path = os.path.join(
                "static",
                "user_faces",
                f"{user_id}.jpg"
            )

            shutil.copy2(
                result["image_path"],
                display_face_path
            )

            user = User(
                user_id=user_id,
                full_name=request.form.get("full_name"),
                roll_no=request.form.get("roll_no"),
                department=request.form.get("department"),
                phone=request.form.get("phone"),
                email=request.form.get("email"),
                face_registered=True,
            )

            user_face = UserFace(
                user_id=user_id,
                image_path=result["image_path"],
                embedding_path=f"face_data/embeddings/{user_id}_*.pkl",
            )

            db.session.add(user)
            db.session.add(user_face)

            db.session.commit()

            for temp_path in temp_paths:

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return redirect(
                url_for("users.users_page")
            )

        except Exception as e:

            for temp_path in temp_paths:

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            db.session.rollback()

            return str(e)

    return render_template(
        "users/add_user.html"
    )
@users.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):

    user = User.query.get_or_404(id)

    if request.method == "POST":

        user.full_name = request.form.get("full_name")
        user.roll_no = request.form.get("roll_no")
        user.department = request.form.get("department")
        user.phone = request.form.get("phone")
        user.email = request.form.get("email")

        uploaded_file = request.files.get("face_image")

        if uploaded_file and uploaded_file.filename:

            temp_path = os.path.join(
                "static",
                "uploads",
                f"{user.user_id}_{uploaded_file.filename}"
            )

            uploaded_file.save(temp_path)

            face_service = FaceService()

            result = face_service.register_face(
                image_path=temp_path,
                user_id=user.user_id
            )

            display_face_path = os.path.join(
                "static",
                "user_faces",
                f"{user.user_id}.jpg"
            )

            shutil.copy2(
                result["image_path"],
                display_face_path
            )

            user_face = UserFace.query.filter_by(
                user_id=user.user_id
            ).first()

            if user_face:

                user_face.image_path = result["image_path"]
                user_face.embedding_path = result["embedding_path"]

            if os.path.exists(temp_path):
                os.remove(temp_path)

            user.face_registered = True

        db.session.commit()

        return redirect(url_for("users.users_page"))

    return render_template(
        "users/edit_users.html",
        user=user
    )

@users.route("/delete/<int:id>")
@login_required
def delete_user(id):
    print("DELETE ROUTE V2 RUNNING")
    user = User.query.get_or_404(id)

    user_face = UserFace.query.filter_by(
        user_id=user.user_id
    ).first()

    if user_face:

        if user_face.image_path and os.path.exists(user_face.image_path):
            os.remove(user_face.image_path)

        if user_face.embedding_path and os.path.exists(user_face.embedding_path):
            os.remove(user_face.embedding_path)

        display_face_path = os.path.join(
            "static",
            "user_faces",
            f"{user.user_id}.jpg"
        )

        if os.path.exists(display_face_path):
            os.remove(display_face_path)

        db.session.delete(user_face)
    
        print("DB ID:", user.id)
        print("USER ID:", user.user_id)

        user_face = UserFace.query.filter_by(
            user_id=user.user_id
        ).first()

        print("USER FACE:", user_face)
    db.session.delete(user)

    db.session.commit()

    return redirect(url_for("users.users_page"))