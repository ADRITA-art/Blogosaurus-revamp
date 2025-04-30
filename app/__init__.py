from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS with specific options
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],  
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.blog import blog_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(ai_bp, url_prefix="/ai")

    with app.app_context():
        db.create_all()

    return app
