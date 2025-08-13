from flask import Flask, request, jsonify, make_response
from flask_caching import Cache

from backend.app.request_bodies.analysis_request_body import AnalysisRequestBody
from backend.app.request_bodies.camera_request_body import CameraRequestBody
from backend.app.request_bodies.event_request_body import EventRequestBody
from backend.app.request_bodies.recording_request_body import StartRecordingRequestBody, StopRecordingRequestBody
from backend.services.events_service import EventsService
from backend.services.user_service import UserService
from backend.services.shops_service import ShopsService
from backend.services.stats_service import StatsService
from backend.services.recording_service import RecordingService
from http import HTTPStatus
import time
from werkzeug.exceptions import Unauthorized, NotFound
from functools import wraps
from dataclasses import asdict

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"
SUCCESS_RESPONSE = "OK"


class ApiHandler:
    """
    Main api handler class for handling HTTP requests and managing application routes.

    This api handler provides endpoints for health checks, error handling, caching tests,
    and cache management. It also includes automatic response wrapping and exception handling.

    Attributes:
        app (Flask): The Flask application instance
        user_service (UserService): The user service instance
        stats_service (StatsService): The stats service instance
        shops_service (ShopsService): The shops service instance
        events_service (EventsService): The events service instance
        recording_service (RecordingService): The recording service instance
        cache (Cache): Flask-Caching instance for request caching
    """

    def __init__(self, app: Flask):
        """
        Initialize the handler with Flask app and configure caching.

        Args:
            app (Flask): The Flask application instance to configure routes for
        """
        self.app = app
        self.user_service = UserService()
        self.stats_service = StatsService()
        self.shops_service = ShopsService()
        self.events_service = EventsService()
        self.recording_service = RecordingService(self.shops_service)

        # Configure Flask-Caching
        self.cache = Cache(app, config={
            'CACHE_TYPE': 'simple',  # In-memory cache
            'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes default TTL
        })

        self.setup_routes()  # Ensure routes are set up during initialization

    def run(self, host: str, port: int):
        """
        Run the app on the given host and port

        Args:
            host (str): The host to run the app on
            port (int): The port to run the app on
        """
        self.app.run(host, port)

    def require_auth(self, f):
        """
        Decorator to require authentication for protected endpoints.

        Args:
            f: The function to decorate

        Returns:
            The decorated function that validates the token before execution
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise Unauthorized("Authorization header is required")
            # Validate token and get user ID
            user_id = self.user_service.validate_token(auth_header)
            # Add user_id to request context for use in the endpoint
            request.user_id = user_id
            return f(*args, **kwargs)

        return decorated_function

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
            return SUCCESS_RESPONSE, HTTPStatus.OK

        @self.app.route("/app/error", methods=["GET"])
        def raise_error():
            """
            Error test endpoint that intentionally raises an exception.

            This endpoint is used for testing error handling and response wrapping.

            Raises:
                AssertionError: Intentional error for testing purposes
            """
            raise AssertionError("Intentional error")

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
            data = request.get_json(silent=True) or {}
            number = data.get("number", 0)
            time.sleep(1)  # Simulate expensive calculation
            result = {
                "input": number,
                "square": number * number,
                "timestamp": time.time()
            }
            return result

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
            self.cache.clear()
            return "Cache cleared successfully"

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
            data = request.get_json(silent=True) or {}
            email = data.get("email")
            password = data.get("password")
            # Call the business logic
            return self.user_service.login(email, password)

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
            # Get user_id from request body
            data = request.get_json(silent=True) or {}
            user_id = data.get("userId")
            # Call the business logic
            return self.user_service.logout(user_id, auth_header)

        @self.app.route("/shops", methods=["GET"])
        @self.require_auth
        @self.cache.memoize(timeout=1800)
        def get_user_shops():
            """
            Get all shops for the current authenticated user.

            Headers:
                Authorization: Bearer <token> - The JWT token of the logged-in user

            Returns:
                JSON response with:
                    - result: Array of shop objects with shop_id and shop_name
                    - errorMessage: None on success, error string on failure
            """
            user_id = getattr(request, "user_id", None)
            # Call the business logic
            return self.shops_service.get_user_shops(user_id)

        @self.app.route("/events", methods=["GET"])
        @self.require_auth
        @self.cache.memoize(timeout=1800)
        def get_user_events():
            """
            Get all events for the current authenticated user.

            Headers:
                Authorization: Bearer <token> - The JWT token of the logged-in user

            Returns:
                JSON response with:
                    - result: Array of events objects
                    - errorMessage: None on success, error string on failure
            """
            user_id = getattr(request, "user_id", None)
            # Call the business logic
            return self.user_service.get_events(user_id)

        @self.app.route("/shops/<shop_id>/events", methods=["GET"])
        @self.require_auth
        @self.cache.memoize()
        def get_shop_events(shop_id):
            """
            Returns all events of a specific shop (event_id, event_datetime, shop_name, camera_name, description)
            """
            return self.shops_service.get_shop_events(shop_id)

        @self.app.route("/shops/<shop_id>/events", methods=["POST"])
        @self.require_auth
        def post_shop_event(shop_id):
            """
            Creates a new event for a specific shop
            :param shop_id: The shop ID from the URL path
            :return: The new event that was created
            """
            data = request.get_json(silent=True) or {}
            
            event_req_body = EventRequestBody(
                camera_id=data.get("camera_id"),
                description=data.get("description"),
                video_url=data.get("video_url")
            )

            return asdict(self.shops_service.create_shop_event(shop_id, event_req_body))

        @self.app.route("/shops/<shop_id>/events/<event_id>", methods=["GET"])
        @self.require_auth
        @self.cache.memoize()
        def get_event(shop_id, event_id: str):
            """
            Get event for a specific event ID
            :param shop_id: The shop ID from the URL path
            :param event_id: The event ID from the URL path
            :return: The event for that event ID
            """
            analysis = self.shops_service.get_event(shop_id, event_id)
            return asdict(analysis)

        @self.app.route("/analysis/<event_id>", methods=["GET"])
        @self.require_auth
        @self.cache.memoize()
        def get_event_analysis(event_id: str):
            """
            Get analysis for a specific event ID
            :param event_id: The event ID from the URL path
            :return: The analysis for that event ID
            """
            analysis = self.events_service.get_event_analysis(event_id)
            return asdict(analysis)

        @self.app.route("/analysis/<event_id>", methods=["POST"])
        @self.require_auth
        def post_event_analysis(event_id: str):
            """
            Post analysis for a specific event ID
            :param event_id: The analysis for that event ID
            :return: The analysis that was posted for that event ID
            """
            data = request.get_json(silent=True) or {}

            analysis_req_body = AnalysisRequestBody(
                final_detection=data.get("final_detection"),
                final_confidence=data.get("final_confidence"),
                decision_reasoning=data.get("decision_reasoning")
            )

            return asdict(self.events_service.create_event_analysis(event_id, analysis_req_body))

        @self.app.route("/shops/<shop_id>/cameras", methods=["GET"])
        @self.require_auth
        @self.cache.memoize()
        def get_shop_cameras(shop_id: str):
            """
            Get all cameras for a specific shop
            :param shop_id: The shop ID from the URL path
            :return: The cameras for that shop
            """
            return self.shops_service.get_shop_cameras(shop_id)

        @self.app.route("/shops/<shop_id>/cameras", methods=["POST"])
        @self.require_auth
        def post_shop_camera(shop_id: str):
            """
            Post camera for a specific shop
            :param shop_id: The shop ID from the URL path
            :return: The camera that was posted for that shop
            """
            data = request.get_json(silent=True) or {}

            camera_req_body = CameraRequestBody(
                camera_name=data.get("camera_name")
            )

            return asdict(self.shops_service.create_shop_camera(shop_id, camera_req_body))

        @self.app.route("/shops/<shop_id>/recording/start", methods=["POST"])
        @self.require_auth
        def start_shop_recording(shop_id):
            """
            Start video recording for a camera in the specified shop.
            
            Args:
                shop_id (str): The shop ID to start recording for
                
            Expected JSON payload:
                {
                    "camera_name": str,  - Name of the camera to record from (required)
                    "duration": int      - Duration in seconds (optional, defaults to 30)
                }
                
            Returns:
                JSON response with:
                    - result: "OK" on success
                    - errorMessage: None on success, error string on failure
            """
            data = request.get_json(silent=True) or {}
            
            start_recording_req_body = StartRecordingRequestBody(
                camera_name=data.get("camera_name"),
                duration=data.get("duration", 30)
            )
            
            # Start the recording
            self.recording_service.start_recording(shop_id, start_recording_req_body)
            
            return SUCCESS_RESPONSE, HTTPStatus.OK

        @self.app.route("/shops/<shop_id>/recording/stop", methods=["POST"])
        @self.require_auth 
        def stop_shop_recording(shop_id):
            """
            Stop video recording for a camera in the specified shop.
            
            Args:
                shop_id (str): The shop ID to stop recording for
                
            Expected JSON payload:
                {
                    "camera_name": str  - Name of the camera to stop recording (required)
                }
                
            Returns:
                JSON response with:
                    - result: "OK" on success
                    - errorMessage: None on success, error string on failure
            """
            data = request.get_json(silent=True) or {}
            
            stop_recording_req_body = StopRecordingRequestBody(
                camera_name=data.get("camera_name")
            )
            
            # Stop the recording
            self.recording_service.stop_recording(shop_id, stop_recording_req_body)
            
            return SUCCESS_RESPONSE, HTTPStatus.OK

        @self.app.route("/shops/<shop_id>/stats", methods=["GET"])
        @self.require_auth
        @self.cache.memoize()
        def get_shop_stats(shop_id):
            """
            Get aggregated statistics for a specific shop.
            
            Query Parameters:
                include_category (bool, optional): Whether to include events_by_category (default: true)
                
            Returns:
                JSON response with computed statistics
            """
            # Get include_category query parameter and cast to boolean
            include_category_str = request.args.get("include_category", "true")
            include_category = include_category_str.lower() == "true"

            # Call the business logic and return StatsDTO converted to dict
            stats = self.stats_service.get_shop_stats(shop_id, include_category=include_category)
            return asdict(stats)

        @self.app.route("/stats", methods=["GET"])
        @self.require_auth
        @self.cache.memoize(
            make_name=lambda fname: f"{fname}|{request.query_string.decode()}")  # Make query params part of cache key
        def get_global_stats():
            """
            Get global statistics aggregated across all shops for the authenticated user.
            
            Query Parameters:
                include_category (bool, optional): Whether to include events_by_category (default: true)
                
            Returns:
                JSON response with global aggregated statistics
            """
            # Get include_category query parameter and cast to boolean
            include_category_str = request.args.get("include_category", "true")
            include_category = include_category_str.lower() == "true"
            # Get user_id from request context (set by require_auth decorator)
            user_id = getattr(request, "user_id", None)
            # Call the business logic and return StatsDTO converted to dict
            stats = self.stats_service.get_global_stats(user_id, include_category=include_category)
            return asdict(stats)

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
                HTTP 404: For NotFound exceptions
                HTTP 500: For StatsComputationError and all other exceptions (internal server error)
            """
            if isinstance(e, Unauthorized):
                status = HTTPStatus.UNAUTHORIZED
            elif isinstance(e, ValueError):
                status = HTTPStatus.BAD_REQUEST
            elif isinstance(e, NotFound):
                status = HTTPStatus.NOT_FOUND
            elif isinstance(e, StatsService.StatsComputationError):
                status = HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR

            return jsonify({
                RESULT_KEY: None,
                ERROR_MESSAGE_KEY: str(e)
            }), status
