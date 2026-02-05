import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager


bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    #sqlalchemy config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #mailtrap config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
    app.config['MAIL_ASCII_ATTACHMENTS'] = False
    app.config['MAIL_SUPPRESS_SEND'] = False
    app.config['MAIL_DEBUG'] = True
    
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    from .models.user import User
    from .models.report import Report
    from .blueprints.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from .blueprints.user.routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/users')
    
    @app.route('/')
    def index():
        return {
            "project": "VAWC DeskHub API",
            "status": "Running",
            "version": "1.0.0"
        }
    
    migrate = Migrate(app, db)
    
    return app

