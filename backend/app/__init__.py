from flask import Flask, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
import os
from backend.db import db

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(Blueprint('api', __name__))

    return app