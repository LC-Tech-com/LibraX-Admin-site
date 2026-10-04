from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from database import db
from models import SystemSetting

settings = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


@settings.route("/", methods=["GET", "POST"])
@login_required
def settings_page():

    if request.method == "POST":

        settings_data = {
            "library_name": request.form.get("library_name"),
            "max_books_per_user": request.form.get("max_books_per_user"),
            "borrow_duration_days": request.form.get("borrow_duration_days"),
            "fine_per_day": request.form.get("fine_per_day"),
            "face_match_threshold": request.form.get("face_match_threshold")
        }

        for key, value in settings_data.items():

            setting = SystemSetting.query.filter_by(
                setting_key=key
            ).first()

            if setting:

                setting.setting_value = value

            else:

                setting = SystemSetting(
                    setting_key=key,
                    setting_value=value
                )

                db.session.add(setting)

        db.session.commit()

        return redirect(
            url_for("settings.settings_page")
        )

    all_settings = {
        s.setting_key: s.setting_value
        for s in SystemSetting.query.all()
    }

    return render_template(
        "settings/settings.html",
        settings=all_settings
    )