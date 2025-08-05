from flask import Flask, request, jsonify, make_response
from flask_caching import Cache
from backend.logic.app_logic import AppLogic
from http import HTTPStatus
import time
from werkzeug.exceptions import Unauthorized

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"


class Controller:
    """
    Main controller class for handling HTTP requests and managing application routes.

    This controller provides endpoints for health checks, error handling, caching tests,
    and cache management. It also includes automatic response wrapping and exception handling.

    Attributes:
        app (Flask): The Flask application instance
        app_logic (AppLogic): Business logic handler
        cache (Cache): Flask-Caching instance for request caching
    """

    def __init__(self, app: Flask):
        """
        Initialize the controller with Flask app and configure caching.

        Args:
            app (Flask): The Flask application instance to configure routes for
        """
        self.app = app
        self.app_logic = AppLogic()

        # Configure Flask-Caching
        self.cache = Cache(app, config={
            'CACHE_TYPE': 'simple',  # In-memory cache
            'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes default TTL
        })

        self.setup_routes()  # Ensure routes are set up during initialization

    def run(self, host: str, port: int):
        self.app.run(host, port)

    def setup_routes(self):
        """
        Configure all application routes and middleware.

        Sets up endpoints for health checks, error handling, caching tests,
        cache management, and response wrapping middleware.
        """

        @self.app.route("/app/health", methods=["GET"])
        def get_health():
            """
            Health check endpoint.

            Returns:
                tuple: ("OK", 200) - Simple health status response
            """
            return "OK", HTTPStatus.OK

        @self.app.route("/app/error", methods=["GET"])
        def raise_error():
            """
            Error test endpoint that intentionally raises an exception.

            This endpoint is used for testing error handling and response wrapping.

            Raises:
                ValueError: Intentional error for testing purposes
            """
            raise ValueError("Intentional error")

        @self.app.route("/app/test", methods=["POST"])
        @self.cache.memoize()
        def test_calculation():
            """
            Test endpoint for caching functionality.

            Performs a simple calculation (squares the input number) with a simulated
            delay to demonstrate caching benefits. The result is cached based on the
            input parameters.

            Expected JSON payload:
                {"number": int} - The number to square

            Returns:
                JSON response with:
                    - result: Dict containing input, square, and timestamp
                    - errorMessage: None on success, error string on failure

            Raises:
                HTTP 500: If calculation fails or invalid input provided
            """
            try:
                data = request.get_json() or {}
                number = data.get("number", 0)
                time.sleep(1)  # Simulate expensive calculation
                result = {
                    "input": number,
                    "square": number * number,
                    "timestamp": time.time()
                }
                return jsonify({
                    RESULT_KEY: result,
                    ERROR_MESSAGE_KEY: None
                })
            except Exception as e:
                return jsonify({
                    RESULT_KEY: None,
                    ERROR_MESSAGE_KEY: str(e)
                }), HTTPStatus.INTERNAL_SERVER_ERROR

        @self.app.route("/app/cache/clear", methods=["POST"])
        def clear_cache():
            """
            Clear all cached responses.

            Removes all entries from the application cache. This is useful for
            testing or when cache invalidation is needed.

            Returns:
                JSON response with:
                    - result: "Cache cleared successfully" on success
                    - errorMessage: None on success, error string on failure

            Raises:
                HTTP 500: If cache clearing operation fails
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

        @self.app.route("/login", methods=["POST"])
        def login():
            """
            User login endpoint.

            Authenticates a user with email and password. The password is hashed
            before comparison with the stored hashed password in the database.

            Expected JSON payload:
                {
                    "email": str,     - User's email address
                    "password": str   - User's password
                }

            Returns:
                JSON response with:
                    - userId: user ID of the logged-in user
                    - firstName: user's first name
                    - lastName: user's last name
                    - token: JWT token for the session
                - errorMessage: None on success, error string on failure
            """
            data = request.get_json() or {}
            email = data.get("email")
            password = data.get("password")
            # Call the business logic
            return self.app_logic.login(email, password)

        @self.app.route("/logout", methods=["GET"])
        def logout():
            """
            User logout endpoint.

            Headers:
                Authorization: Bearer <token> - The JWT token of the logged-in user

            Returns:
                JSON response with:
                    - userId: user ID of the logged-out user
                - errorMessage: None on success, error string on failure
            """
            # Get token from Authorization header
            auth_header = request.headers.get("Authorization")
            # Call the business logic
            return self.app_logic.logout(auth_header)

        @self.app.after_request
        def wrap_success_response(response):
            """
            Middleware to wrap all responses in a consistent format.

            Ensures all responses follow the standard format with 'result' and
            'errorMessage' keys. Handles both JSON and non-JSON responses.

            Args:
                response: The original Flask response object

            Returns:
                Flask response: Wrapped response in standard format
            """
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
            """
            Global exception handler for all unhandled exceptions.

            Catches any unhandled exceptions and returns them in the standard
            response format with appropriate HTTP status codes.

            Args:
                e (Exception): The caught exception

            Returns:
                JSON response with:
                    - result: None (indicating error)
                    - errorMessage: String representation of the exception

            Status:
                HTTP 401: For Unauthorized exceptions
                HTTP 400: For ValueError (bad request)
                HTTP 500: For all other exceptions (internal server error)
            """
            if isinstance(e, Unauthorized):
                status = HTTPStatus.UNAUTHORIZED
            elif isinstance(e, ValueError):
                status = HTTPStatus.BAD_REQUEST
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR

            return jsonify({
                RESULT_KEY: None,
                ERROR_MESSAGE_KEY: str(e)
            }), status