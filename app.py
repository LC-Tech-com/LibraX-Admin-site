from flask import Flask
from models import *
from database import db
from config import Config
from database import db
from flask_login import LoginManager, login_manager
from database import db
from models import Admin
from routes.api.api_routes import api
from routes.auth.auth_routes import auth
from routes.users.user_routes import users
from routes.books.book_routes import books
from routes.transactions.transaction_route import transactions
from routes.dashboard.dashboard_routes import dashboard
from routes.settings.settings_routes import settings

def create_app():
    app = Flask(__name__)
    # print("DB_PORT =", Config.DB_PORT)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager = LoginManager()

    login_manager.login_view = "auth.login"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✓ MySQL connection successful")
        except Exception as e:
            print(f"✗ MySQL connection failed: {e}")

    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(books)
    app.register_blueprint(transactions)
    app.register_blueprint(dashboard)
    app.register_blueprint(api)
    app.register_blueprint(settings)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
