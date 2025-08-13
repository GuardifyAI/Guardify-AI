from flask import Flask, Blueprint
from flask_cors import CORS
import os
from backend.db import db
from utils import load_env_variables


def create_app():
    load_env_variables()
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(Blueprint('api', __name__))

    return app