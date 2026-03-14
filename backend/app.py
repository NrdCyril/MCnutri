from flask import Flask
from flask_cors import CORS
from .extensions import db, bcrypt, jwt, mail
from .config import Config
from .routes.auth import auth_bp
from .routes.recettes import recettes_bp
from .routes.admin import admin_bp
from .routes.users import users_bp
from .routes.aliments import aliments_bp
from .routes.social import social_bp
from .routes.stats import stats_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(recettes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(aliments_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(stats_bp)

    return app