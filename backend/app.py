import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import get_config
from database import db
from services.auth_service import bcrypt, register_demo_user
from routes.auth import auth_bp
from routes.profile import profile_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Extensions
    bcrypt.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
        register_demo_user()

    print("Server running at http://localhost:5000")
    print("Demo: demo@example.com / demo1234")
    app.run(debug=True, port=5000)
