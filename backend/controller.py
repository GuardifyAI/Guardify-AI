from flask import Flask, request, jsonify, make_response
from flask_caching import Cache
from backend.logic.app_logic import AppLogic
from http import HTTPStatus

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"

class Controller:
    def __init__(self, app: Flask):
        self.app = app
        self.app_logic = AppLogic()
        
        # Configure Flask-Caching
        self.cache = Cache(app, config={
            'CACHE_TYPE': 'simple',  # In-memory cache
            'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes default TTL
        })
        
        self.setup_routes()  # Ensure routes are set up during initialization

    def setup_routes(self):
        @self.app.route("/app/health", methods=["GET"])
        def get_health():
            return "OK", HTTPStatus.OK

        @self.app.route("/app/error", methods=["GET"])
        def raise_error():
            raise ValueError("Intentional error")

        @self.app.route("/app/cache/clear", methods=["POST"])
        def clear_cache():
            """
            Endpoint to manually clear the cache.
            """
            try:
                self.cache.clear()
                return jsonify({
                    RESULT_KEY: "Cache cleared successfully",
                    ERROR_MESSAGE_KEY: None
                })
            except Exception as e:
                return jsonify({
                    RESULT_KEY: None,
                    ERROR_MESSAGE_KEY: str(e)
                }), HTTPStatus.INTERNAL_SERVER_ERROR

        @self.app.after_request
        def wrap_success_response(response):
            # Extract original response content
            try:
                original_data = response.get_json(silent=True)
            except Exception:
                original_data = None

            if original_data is None:
                # Non-JSON (e.g., string like "OK")
                response_data = response.get_data(as_text=True)
                wrapped = {
                    RESULT_KEY: response_data,
                    ERROR_MESSAGE_KEY: None
                }
                return make_response(jsonify(wrapped), response.status_code)
            else:
                # Already a JSON, check if we should wrap
                if RESULT_KEY in original_data and ERROR_MESSAGE_KEY in original_data:
                    return response  # Already wrapped
                wrapped = {
                    RESULT_KEY: original_data,
                    ERROR_MESSAGE_KEY: None
                }
                return make_response(jsonify(wrapped), response.status_code)

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            return jsonify({
                RESULT_KEY: None,
                ERROR_MESSAGE_KEY: str(e)  # or use traceback.format_exc() for debug
            }), HTTPStatus.INTERNAL_SERVER_ERROR