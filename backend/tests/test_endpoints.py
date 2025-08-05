import pytest
import jwt
from http import HTTPStatus
from backend.app import create_app
from backend.controller import Controller
import os
from data_science.src.utils import load_env_variables
load_env_variables()

@pytest.fixture
def client():
    app = create_app()
    Controller(app)  # Set up routes
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

    # Check result structure
    shops = data["result"]
    assert isinstance(shops, list), "Result should be a list of shops"
    assert len(shops) == 4, f"Expected 4 shops, got {len(shops)}"

    # Define expected shops based on the image
    expected_shops = [
        {"shop_id": "guardify_ai_central", "shop_name": "Guardify AI Central"},
        {"shop_id": "guardify_ai_north", "shop_name": "Guardify AI North"},
        {"shop_id": "guardify_ai_east", "shop_name": "Guardify AI East"},
        {"shop_id": "guardify_ai_west", "shop_name": "Guardify AI West"}
    ]

    # Check each shop
    for expected_shop in expected_shops:
        # Find the shop in the response
        found_shop = None
        for shop in shops:
            if shop["shop_id"] == expected_shop["shop_id"]:
                found_shop = shop
                break

        assert found_shop is not None, f"Shop with ID '{expected_shop['shop_id']}' not found in response"
        assert found_shop["shop_name"] == expected_shop["shop_name"], \
            f"Shop '{expected_shop['shop_id']}' should have name '{expected_shop['shop_name']}', got '{found_shop['shop_name']}'"

    print("Get user shops test passed successfully!")
    print(f"   Found {len(shops)} shops:")
    for shop in shops:
        print(f"     - {shop['shop_id']}: {shop['shop_name']}")


def test_get_user_shops_without_auth(client):
    """
    Test shops endpoint without authentication.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates authentication is required
    """
    # Make shops request without Authorization header
    shops_data = {"userId": "some_user_id"}
    response = client.get("/shops", json=shops_data)

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
    expected_error = "Authorization header is required"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Get user shops without auth test passed!")


def test_get_user_shops_missing_user_id(client, auth_token):
    """
    Test shops endpoint without providing userId.

    Verifies that:
    - Request returns 400 Bad Request status
    - Error message indicates userId is required
    """
    # Make shops request without userId
    shops_data = {}  # Empty payload
    response = client.get("/shops", json=shops_data, headers={"Authorization": auth_token})

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
    expected_error = "User ID is required"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Get user shops without userId test passed!")


def test_get_user_shops_unauthorized_user(client, auth_token):
    """
    Test shops endpoint with a different user ID than the authenticated user.

    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates user can only access their own shops
    """
    # Make shops request with a different user ID
    shops_data = {"userId": "different_user_id"}
    response = client.get("/shops", json=shops_data, headers={"Authorization": auth_token})

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
    expected_error = "Can only access your own shops"
    assert expected_error in data["errorMessage"], f"Expected error: '{expected_error}', got: '{data['errorMessage']}'"

    print("Get user shops with unauthorized user test passed!")