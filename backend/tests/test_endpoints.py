import pytest
import jwt
from http import HTTPStatus
from backend.app import create_app
from backend.api_handler import ApiHandler
import os
from data_science.src.utils import load_env_variables
load_env_variables()
from deepdiff import DeepDiff

@pytest.fixture
def client():
    app = create_app()
    ApiHandler(app)  # Set up routes
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def login_data():
    return {
        "email": "aiguardify@gmail.com",
        "password": "demo_user"
    }
@pytest.fixture
def john_doe():
    return {
        "email": "user_4ef9faf8-4fa4-4868-94ea-710be8598487@example.com",
        "password": "john_doe"
    }

@pytest.fixture
def jane_smith():
    return {
        "email": "user_4ef9faf8-4fa4-4868-94ea-710be8598487@example.com",
        "password": "jane_smith"
    }

def test_successful_login(client, login_data):
    """
    Test successful login with valid credentials.

    Verifies that:
    - Request returns OK status
    - Token is valid and can be decoded
    - User ID is 'demo_user'
    - First name is 'Demo'
    - Last name is 'User'
    """
    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.OK, f"Expected OK status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Check result structure
    result = data["result"]
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "userId" in result, "Result should contain userId"
    assert "firstName" in result, "Result should contain firstName"
    assert "lastName" in result, "Result should contain lastName"
    assert "token" in result, "Result should contain token"

    # Check user data
    assert result["userId"] == "demo_user", f"Expected userId 'demo_user', got '{result['userId']}'"
    assert result["firstName"] == "Demo", f"Expected firstName 'Demo', got '{result['firstName']}'"
    assert result["lastName"] == "User", f"Expected lastName 'User', got '{result['lastName']}'"

    # Validate token format
    token = result["token"]
    assert token.startswith("Bearer "), "Token should start with 'Bearer '"

    # Validate JWT token
    jwt_token = token[7:]  # Remove "Bearer " prefix
    try:
        # Decode token (using the same secret as in AppLogic)
        payload = jwt.decode(jwt_token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])

        # Check token payload
        assert "user_id" in payload, "Token should contain user_id"
        assert payload["user_id"] == "demo_user", f"Token should contain userId 'demo_user', got '{payload['user_id']}'"
        assert "exp" in payload, "Token should contain expiration"
        assert "jti" in payload, "Token should contain jti (JWT ID)"

    except jwt.ExpiredSignatureError:
        pytest.fail("Token should not be expired")
    except jwt.InvalidTokenError as e:
        pytest.fail(f"Token should be valid: {e}")

    print("Login test passed successfully!")
    print(f"   User ID: {result['userId']}")
    print(f"   First Name: {result['firstName']}")
    print(f"   Last Name: {result['lastName']}")
    print(f"   Token: {token[:20]}...")  # Show first 20 chars of token


def test_login_nonexistent_email(client):
    """
    Test login with an email that doesn't exist in the database.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates user doesn't exist
    """
    # Test data with non-existent email
    login_data = {
        "email": "nonexistent@example.com",
        "password": "demo_user"
    }

    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "User with email 'nonexistent@example.com' does not exist"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Login with nonexistent email test passed!")


def test_login_wrong_password(client):
    """
    Test login with correct email but wrong password.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates incorrect password
    """
    # Test data with correct email but wrong password
    login_data = {
        "email": "aiguardify@gmail.com",
        "password": "wrong_password"
    }

    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "Incorrect password"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Login with wrong password test passed!")


def test_login_missing_password(client):
    """
    Test login request without password in the payload.

    Verifies that:
    - Request returns 400 Bad Request status
    - Error message indicates password is required
    """
    # Test data without password
    login_data = {
        "email": "aiguardify@gmail.com"
        # password is missing
    }

    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "Password is required"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Login with missing password test passed!")


def test_login_missing_email(client):
    """
    Test login request without email in the payload.

    Verifies that:
    - Request returns 400 Bad Request status
    - Error message indicates email is required
    """
    # Test data without email
    login_data = {
        "password": "demo_user"
        # email is missing
    }

    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "Email is required"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Login with missing email test passed!")


def test_login_empty_payload(client):
    """
    Test login request with empty JSON payload.

    Verifies that:
    - Request returns 400 Bad Request status
    - Error message indicates email is required
    """
    # Test data with empty payload
    login_data = {}

    # Make login request
    response = client.post("/login", json=login_data)

    # Check response status
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message (should be the first validation error encountered)
    expected_error = "Email is required"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Login with empty payload test passed!")


def test_successful_logout(client, login_data):
    """
    Test successful logout with valid token.

    Verifies that:
    - Request returns OK status
    - Response contains the userId of the logged-out user
    - Token is properly validated
    """
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == HTTPStatus.OK, "Login should succeed to get token"

    login_result = login_response.get_json()["result"]
    token = login_result["token"]
    expected_user_id = login_result["userId"]

    # Now logout with the token
    logout_data = {"userId": expected_user_id}
    logout_response = client.get("/logout", json=logout_data, headers={"Authorization": token})

    # Check logout response status
    assert logout_response.status_code == HTTPStatus.OK, f"Expected OK status, got {logout_response.status_code}"

    # Parse logout response
    logout_data = logout_response.get_json()
    assert logout_data is not None, "Response should be JSON"
    assert "result" in logout_data, "Response should contain 'result' key"
    assert "errorMessage" in logout_data, "Response should contain 'errorMessage' key"
    assert logout_data["errorMessage"] is None, "Should not have error message"

    # Check result structure
    result = logout_data["result"]
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "userId" in result, "Result should contain userId"

    # Check that the userId matches the one from login
    assert result["userId"] == expected_user_id, f"Expected userId '{expected_user_id}', got '{result['userId']}'"

    print("Logout test passed successfully!")
    print(f"   Logged out user ID: {result['userId']}")


def test_logout_without_token(client):
    """
    Test logout without providing Authorization header.

    Verifies that:
    - Request returns 400 bad request status
    - Error message indicates token is required
    """
    # Make logout request without Authorization header
    logout_data = {"userId": "stam"}
    logout_response = client.get("/logout", json=logout_data)

    # Check response status
    assert logout_response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 401 status, got {logout_response.status_code}"

    # Parse response
    data = logout_response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "Token was not provided"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Logout without token test passed!")


def test_logout_invalid_token(client):
    """
    Test logout with invalid token format.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates invalid token format
    """
    # Make logout request with invalid token format
    logout_data = {"userId": "stam"}
    logout_response = client.get("/logout", json=logout_data, headers={"Authorization": "InvalidToken"})

    # Check response status
    assert logout_response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 status, got {logout_response.status_code}"

    # Parse response
    data = logout_response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = "Invalid token format"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Logout with invalid token test passed!")


def test_logout_mismatched_user_id(client, login_data):
    """
    Test logout with token that doesn't belong to the specified user.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates token doesn't belong to the user
    """
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == HTTPStatus.OK, "Login should succeed to get token"

    login_result = login_response.get_json()["result"]
    token = login_result["token"]
    actual_user_id = login_result["userId"]

    # Try to logout with a different user_id
    wrong_user_id = "different_user"
    logout_data = {"userId": wrong_user_id}
    logout_response = client.get("/logout", json=logout_data, headers={"Authorization": token})

    # Check response status
    assert logout_response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 status, got {logout_response.status_code}"

    # Parse response
    data = logout_response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"

    # Check error message
    expected_error = f"Token does not belong to user '{wrong_user_id}'"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Logout with mismatched user ID test passed!")


@pytest.fixture
def john_doe_login(client, john_doe):
    # Make login request
    response = client.post("/login", json=john_doe)
    assert response.status_code == HTTPStatus.OK, "Login should succeed to get token"
    # Extract token from response
    login_result = response.get_json()["result"]
    token = login_result["token"]
    user_id = login_result["userId"]
    return user_id, token

@pytest.fixture
def jane_smith_login(client, jane_smith):
    # Make login request
    response = client.post("/login", json=jane_smith)
    assert response.status_code == HTTPStatus.OK, "Login should succeed to get token"
    # Extract token from response
    login_result = response.get_json()["result"]
    token = login_result["token"]
    user_id = login_result["userId"]
    return user_id, token

def test_get_user_shops_success(client, john_doe, john_doe_login):
    """
    Test successful retrieval of user shops.

    Verifies that:
    - Request returns OK status
    - Response contains the expected shop structure
    - All expected shops are returned with correct IDs and names
    """
    user_id, john_doe_auth_token = john_doe_login

    # Make shops request
    shops_data = {"userId": user_id}
    response = client.get("/shops", json=shops_data, headers={"Authorization": john_doe_auth_token})

    # Check response status
    assert response.status_code == HTTPStatus.OK, f"Expected OK status, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Actual result
    shops = data["result"]
    assert isinstance(shops, list), "Shops should be a list"
    assert len(shops) == 4, "Should have exactly 4 shops"

    # Expected shops with only the fields we want to check
    expected_shops = [
        {"shop_id": "guardify_ai_central", "name": "Guardify AI Central"},
        {"shop_id": "guardify_ai_north", "name": "Guardify AI North"},
        {"shop_id": "guardify_ai_east", "name": "Guardify AI East"},
        {"shop_id": "guardify_ai_west", "name": "Guardify AI West"}
    ]

    # Check that each expected shop is present in the actual shops
    for expected_shop in expected_shops:
        found = False
        for actual_shop in shops:
            # Check if this actual shop matches the expected shop
            # We only check the fields that are in expected_shop
            matches = True
            for key, expected_value in expected_shop.items():
                if key not in actual_shop or actual_shop[key] != expected_value:
                    matches = False
                    break
            
            if matches:
                found = True
                break
        
        assert found, f"Expected shop {expected_shop} not found in actual shops"

    print("User shops test passed successfully!")
    print(f"   Found {len(shops)} shops")

def test_get_shop_events(client, john_doe_login):
    """
    Test retrieval of events for shop 'guardify_ai_central'.
    Verifies that the response contains the expected event details.
    """
    user_id, auth_token = john_doe_login

    # Make request to the events endpoint for the shop
    response = client.get(
        "/shops/guardify_ai_central/events",
        headers={"Authorization": auth_token}
    )

    # Check response status
    assert response.status_code == HTTPStatus.OK, f"Expected 200 OK, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Actual result
    events = data["result"]
    assert isinstance(events, list), "Events should be a list"
    assert len(events) == 2, "There should be at least one event"

    # Expected events with only the fields we want to check
    expected_events = [
        {
            "event_id": "b88c061d-e375-4043-8305-9d5c79594151",
            "event_datetime": "2025-07-25T14:30:00",  # Adjust if your API returns a different format
            "shop_name": "Guardify AI Central",              # Adjust if your DB has a different name
            "camera_name": "Entrance",
            "description": "Person entering suspiciously"
        },
        {
            "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "event_datetime": "2025-07-27T10:45:00",  # Adjust if your API returns a different format
            "shop_name": "Guardify AI Central",
            "camera_name": "Checkout",
            "description": "Suspicious behavior at checkout"
        }
    ]

    # Check that each expected event is present in the actual events
    for expected_event in expected_events:
        found = False
        for actual_event in events:
            # Check if this actual event matches the expected event
            # We only check the fields that are in expected_event
            matches = True
            for key, expected_value in expected_event.items():
                if key not in actual_event or actual_event[key] != expected_value:
                    matches = False
                    break
            
            if matches:
                found = True
                break
        
        assert found, f"Expected event {expected_event} not found in actual events"

    print("Shop events test passed successfully!")
    print(f"   Found {len(events)} events")

def test_get_shop_stats(client, john_doe_login):
    """
    Test retrieval of statistics for shop 'guardify_ai_central'.
    Verifies that the response contains the expected statistics based on the known events.
    """
    user_id, auth_token = john_doe_login

    # Make request to the stats endpoint for the shop
    response = client.get(
        "/shops/guardify_ai_central/stats",
        headers={"Authorization": auth_token}
    )

    # Check response status
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Actual result
    stats = data["result"]
    assert isinstance(stats, dict), "Stats should be a dictionary"

    # Check that all expected keys are present
    expected_keys = ["events_per_day", "events_by_hour", "events_by_camera", "events_by_category"]
    for key in expected_keys:
        assert key in stats, f"Stats should contain '{key}' key"
        assert isinstance(stats[key], dict), f"'{key}' should be a dictionary"

    # Check that events_by_category is present (default behavior)
    assert "events_by_category" in stats, "events_by_category should be included by default"

    # Check that all values are integers
    for key in expected_keys:
        for value in stats[key].values():
            assert isinstance(value, int), f"All values in '{key}' should be integers"

    # Expected stats based on the two known events:
    # Event 1: 2025-07-25T14:30:00, "Entrance" camera
    # Event 2: 2025-07-27T10:45:00, "Checkout" camera
    
    # Check events_per_day
    expected_events_per_day = {
        "2025-07-25": 1,  # One event on 2025-07-25
        "2025-07-27": 1   # One event on 2025-07-27
    }
    for day, expected_count in expected_events_per_day.items():
        assert day in stats["events_per_day"], f"Day {day} should be in events_per_day"
        assert stats["events_per_day"][day] == expected_count, f"Expected {expected_count} events on {day}, got {stats['events_per_day'][day]}"

    # Check events_by_hour
    expected_events_by_hour = {
        "14": 1,  # One event at 14:30 (hour 14)
        "10": 1   # One event at 10:45 (hour 10)
    }
    for hour, expected_count in expected_events_by_hour.items():
        assert hour in stats["events_by_hour"], f"Hour {hour} should be in events_by_hour"
        assert stats["events_by_hour"][hour] == expected_count, f"Expected {expected_count} events at hour {hour}, got {stats['events_by_hour'][hour]}"

    # Check events_by_camera
    expected_events_by_camera = {
        "Entrance": 1,   # One event from Entrance camera
        "Checkout": 1    # One event from Checkout camera
    }
    for camera, expected_count in expected_events_by_camera.items():
        assert camera in stats["events_by_camera"], f"Camera {camera} should be in events_by_camera"
        assert stats["events_by_camera"][camera] == expected_count, f"Expected {expected_count} events from {camera} camera, got {stats['events_by_camera'][camera]}"

    # Check events_by_category
    # Based on the known events:
    # Event 1: "Person entering suspiciously" -> should be classified as "suspicious behavior"
    # Event 2: "Suspicious behavior at checkout" -> should be classified as "suspicious behavior"
    expected_events_by_category = {
        "Suspicious Behavior": 2  # Both events should be classified as suspicious behavior
    }
    
    # Check that events_by_category contains the expected categories
    # Note: The actual classification might vary based on the NLP model, so we'll be more flexible
    assert "events_by_category" in stats, "events_by_category should be included by default"
    assert isinstance(stats["events_by_category"], dict), "events_by_category should be a dictionary"
    
    # Check that we have some categories (the exact classification may vary)
    assert expected_events_by_category == stats["events_by_category"], \
        f"Expected events_by_category {expected_events_by_category}, got {stats['events_by_category']}"

    print("Shop stats test passed successfully!")
    print(f"   Events per day: {len(stats['events_per_day'])} days")
    print(f"   Events by hour: {len(stats['events_by_hour'])} hours")
    print(f"   Events by camera: {len(stats['events_by_camera'])} cameras")
    print(f"   Events by category: {len(stats['events_by_category'])} categories")


def test_get_shop_stats_without_category(client, john_doe_login):
    """
    Test retrieval of statistics for shop 'guardify_ai_central' without category.
    Verifies that events_by_category is not included when include_category=false.
    """
    user_id, auth_token = john_doe_login

    # Make request to the stats endpoint for the shop with include_category=false
    response = client.get(
        "/shops/guardify_ai_central/stats?include_category=false",
        headers={"Authorization": auth_token}
    )

    # Check response status
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Actual result
    stats = data["result"]
    assert isinstance(stats, dict), "Stats should be a dictionary"

    # Check that events_by_category is NOT present
    assert stats.get("events_by_category") is None, "events_by_category should not be included when include_category=false"

    # Check that other expected keys are present
    expected_keys = ["events_per_day", "events_by_hour", "events_by_camera"]
    for key in expected_keys:
        assert key in stats, f"Stats should contain '{key}' key"
        assert isinstance(stats[key], dict), f"'{key}' should be a dictionary"

    print("Shop stats without category test passed successfully!")


def test_get_global_stats(client, john_doe_login):
    """
    Test retrieval of global statistics for all shops that the user is connected to.
    Verifies that the response contains aggregated statistics across all shops.
    """
    user_id, auth_token = john_doe_login

    # Make request to the global stats endpoint
    response = client.get(
        "/stats",
        headers={"Authorization": auth_token}
    )

    # Check response status
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["errorMessage"] is None, "Should not have error message"

    # Actual result
    stats = data["result"]
    assert isinstance(stats, dict), "Stats should be a dictionary"

    # Check that all expected keys are present
    expected_keys = ["events_per_day", "events_by_hour", "events_by_camera", "events_by_category"]
    for key in expected_keys:
        assert key in stats, f"Stats should contain '{key}' key"
        assert isinstance(stats[key], dict), f"'{key}' should be a dictionary"

    # Check that events_by_category is present (default behavior)
    assert "events_by_category" in stats, "events_by_category should be included by default"

    # Check that all values are integers
    for key in expected_keys:
        for value in stats[key].values():
            assert isinstance(value, int), f"All values in '{key}' should be integers"

    # Check that we have aggregated data from multiple shops
    # The user should have access to multiple shops, so we should see aggregated data
    assert len(stats["events_per_day"]) > 0, "Should have events per day data"
    assert len(stats["events_by_hour"]) > 0, "Should have events by hour data"
    assert len(stats["events_by_camera"]) > 0, "Should have events by camera data"
    assert len(stats["events_by_category"]) > 0, "Should have events by category data"

    print("Global stats test passed successfully!")
    print(f"   Events per day: {len(stats['events_per_day'])} days")
    print(f"   Events by hour: {len(stats['events_by_hour'])} hours")
    print(f"   Events by camera: {len(stats['events_by_camera'])} cameras")
    print(f"   Events by category: {len(stats['events_by_category'])} categories")


def test_calling_get_global_stats_before_per_shop_makes_it_faster(client, john_doe_login):
    # TODO: Implement test
    assert True


def test_get_global_stats_for_user_with_shops_without_events(client):
    # TODO: Implement test
    assert True