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


def test_successful_login(client):
    """
    Test successful login with valid credentials.

    Verifies that:
    - Request returns OK status
    - Token is valid and can be decoded
    - User ID is 'demo_user'
    - First name is 'Demo'
    - Last name is 'User'
    """
    # Test data
    login_data = {
        "email": "aiguardify@gmail.com",
        "password": "demo_user"
    }

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

    except jwt.ExpiredSignatureError:
        pytest.fail("Token should not be expired")
    except jwt.InvalidTokenError as e:
        pytest.fail(f"Token should be valid: {e}")

    print("Login test passed successfully!")
    print(f"   User ID: {result['userId']}")
    print(f"   First Name: {result['firstName']}")
    print(f"   Last Name: {result['lastName']}")
    print(f"   Token: {token[:20]}...")  # Show first 20 chars of token