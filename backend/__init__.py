from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config.settings import DATABASE_URI
from dotenv import load_dotenv
import os

# Laad environment variables uit .env bestand
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuratie van de database
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialiseer extensies
    CORS(app)
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        
        db.create_all()
        
        return app
