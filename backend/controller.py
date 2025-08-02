from flask import Flask, request, jsonify
from backend.logic.app_logic import AppLogic

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"

class Controller:
    def __init__(self, app: Flask):
        self.app = app
        self.app_logic = AppLogic()
        self.setup_routes()  # Ensure routes are set up during initialization

    def setup_routes(self):
        @self.app.route("/app/health", methods=["GET"])
        def get_health():
            return "OK", 200