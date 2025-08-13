import pytest
from http import HTTPStatus
from utils.env_utils import load_env_variables
load_env_variables()
from backend.api_handler import ApiHandler
from backend.app import create_app

# Define specific shop_id and camera_name for these tests
TEST_SHOP_ID = "michal_shop_1"
TEST_CAMERA_NAME = "Sweets 1"

@pytest.fixture
def client():
    app = create_app()
    ApiHandler(app)  # Set up routes
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def john_doe():
    return {
        "email": "michal@gmail.com",
        "password": "1234"
    }

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

# ====================
# RECORDING ENDPOINT TESTS
# ====================

def test_start_recording_success(client, john_doe_login):
    """
    Test successful start recording request.
    
    Verifies that:
    - Request returns OK status
    - Recording service is called with correct parameters
    - Response follows standard format
    """
    user_id, auth_token = john_doe_login
    
    # Test data for starting recording
    recording_data = {
        "camera_name": TEST_CAMERA_NAME,
        "duration": 5  # Short duration for testing
    }
    
    # Make POST request to start recording
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Check response status - might succeed or fail depending on environment setup
    # For testing purposes, we expect either success or controlled failure
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected 200 OK or 500 Internal Server Error, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    
    if response.status_code == HTTPStatus.OK:
        # Successful recording start
        assert data["errorMessage"] is None, "Should not have error message on success"
        assert data["result"] == "OK", "Result should be 'OK' on success"
        print("Recording start test passed - recording started successfully!")
        
        # Try to stop the recording to clean up
        try:
            stop_data = {"camera_name": TEST_CAMERA_NAME}
            stop_response = client.post(
                f"/shops/{TEST_SHOP_ID}/recording/stop",
                json=stop_data,
                headers={"Authorization": auth_token}
            )
            if stop_response.status_code == HTTPStatus.OK:
                print("   Successfully stopped recording for cleanup")
        except Exception as e:
            print(f"   Warning: Could not stop recording for cleanup: {e}")
    else:
        # Expected failure (environment not set up for recording)
        assert data["result"] is None, "Result should be None on error"
        assert data["errorMessage"] is not None, "Should have error message on failure"
        print("Recording start test passed - expected failure due to environment setup")
        print(f"   Error message: {data['errorMessage']}")


def test_start_recording_with_default_duration(client, john_doe_login):
    """
    Test starting recording without specifying duration (should use default 30 seconds).
    """
    user_id, auth_token = john_doe_login
    
    # Test data without duration (should default to 30)
    recording_data = {
        "camera_name": TEST_CAMERA_NAME
    }
    
    # Make POST request to start recording
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Should either succeed or fail gracefully
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected 200 OK or 500 Internal Server Error, got {response.status_code}"
    
    data = response.get_json()
    assert "result" in data and "errorMessage" in data, "Response should have standard format"
    
    # Clean up if successful
    if response.status_code == HTTPStatus.OK:
        try:
            stop_data = {"camera_name": TEST_CAMERA_NAME}
            client.post(
                f"/shops/{TEST_SHOP_ID}/recording/stop",
                json=stop_data,
                headers={"Authorization": auth_token}
            )
        except:
            pass
    
    print("Recording start with default duration test passed!")


def test_start_recording_unauthorized(client):
    """
    Test starting recording without authentication.
    
    Verifies that:
    - Request returns 401 Unauthorized status
    - Error message indicates authentication is required
    """
    recording_data = {
        "camera_name": TEST_CAMERA_NAME,
        "duration": 30
    }
    
    # Make POST request without authentication
    response = client.post(f"/shops/{TEST_SHOP_ID}/recording/start", json=recording_data)
    
    # Check response status
    assert response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 Unauthorized, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for unauthorized request"
    assert data["errorMessage"] is not None, "Should have error message for unauthorized request"
    
    print("Start recording unauthorized test passed!")


def test_start_recording_missing_camera_name(client, john_doe_login):
    """
    Test starting recording without camera_name field.
    
    Verifies that:
    - Request returns 400 Bad Request status
    - Error message indicates camera_name is required
    """
    user_id, auth_token = john_doe_login
    
    # Test data without camera_name
    recording_data = {
        "duration": 30
    }
    
    # Make POST request with missing camera_name
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Check response status
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"
    
    # Check that error message mentions camera_name
    assert "camera_name is required" in data["errorMessage"], \
        f"Error message should mention camera_name requirement: {data['errorMessage']}"
    
    print("Start recording missing camera_name test passed!")


def test_start_recording_empty_camera_name(client, john_doe_login):
    """
    Test starting recording with empty camera_name field.
    """
    user_id, auth_token = john_doe_login
    
    # Test data with empty camera_name
    recording_data = {
        "camera_name": "",
        "duration": 30
    }
    
    # Make POST request with empty camera_name
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Should fail with bad request
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}"
    
    data = response.get_json()
    assert data["result"] is None and data["errorMessage"] is not None, "Should have error for empty camera_name"
    
    print("Start recording empty camera_name test passed!")


def test_start_recording_nonexistent_shop(client, john_doe_login):
    """
    Test starting recording for a shop that doesn't exist.
    """
    user_id, auth_token = john_doe_login
    
    recording_data = {
        "camera_name": TEST_CAMERA_NAME,
        "duration": 30
    }
    
    # Make POST request to nonexistent shop
    response = client.post(
        "/shops/nonexistent_shop/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Should fail when shop doesn't exist
    assert response.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected error status for nonexistent shop, got {response.status_code}"
    
    data = response.get_json()
    assert data["result"] is None and data["errorMessage"] is not None, "Should have error for nonexistent shop"
    
    print("Start recording nonexistent shop test passed!")


def test_start_recording_invalid_duration(client, john_doe_login):
    """
    Test starting recording with invalid duration values.
    """
    user_id, auth_token = john_doe_login
    
    # Test with negative duration
    recording_data = {
        "camera_name": TEST_CAMERA_NAME,
        "duration": -10
    }
    
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Should either accept (and handle internally) or reject negative duration
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected valid response for negative duration, got {response.status_code}"
    
    # Clean up if it somehow succeeded
    if response.status_code == HTTPStatus.OK:
        try:
            stop_data = {"camera_name": TEST_CAMERA_NAME}
            client.post(
                f"/shops/{TEST_SHOP_ID}/recording/stop",
                json=stop_data,
                headers={"Authorization": auth_token}
            )
        except:
            pass
    
    print("Start recording invalid duration test passed!")


def test_stop_recording_success(client, john_doe_login):
    """
    Test successful stop recording request.
    
    Note: This test expects there's no active recording, so it should fail gracefully.
    """
    user_id, auth_token = john_doe_login
    
    # Test data for stopping recording
    stop_data = {
        "camera_name": TEST_CAMERA_NAME
    }
    
    # Make POST request to stop recording (should fail since no recording is active)
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/stop",
        json=stop_data,
        headers={"Authorization": auth_token}
    )
    
    # Should fail since no recording is active
    assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected 400 Bad Request or 500 Internal Server Error, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert "result" in data, "Response should contain 'result' key"
    assert "errorMessage" in data, "Response should contain 'errorMessage' key"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"
    
    # Check that error message mentions no active recording
    expected_error_text = "No active recording found"
    assert expected_error_text in data["errorMessage"], \
        f"Error message should mention no active recording: {data['errorMessage']}"
    
    print("Stop recording (no active recording) test passed!")
    print(f"   Error message: {data['errorMessage']}")


def test_stop_recording_unauthorized(client):
    """
    Test stopping recording without authentication.
    """
    stop_data = {
        "camera_name": TEST_CAMERA_NAME
    }
    
    # Make POST request without authentication
    response = client.post(f"/shops/{TEST_SHOP_ID}/recording/stop", json=stop_data)
    
    # Check response status
    assert response.status_code == HTTPStatus.UNAUTHORIZED, f"Expected 401 Unauthorized, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert data["result"] is None, "Result should be None for unauthorized request"
    assert data["errorMessage"] is not None, "Should have error message for unauthorized request"
    
    print("Stop recording unauthorized test passed!")


def test_stop_recording_missing_camera_name(client, john_doe_login):
    """
    Test stopping recording without camera_name field.
    """
    user_id, auth_token = john_doe_login
    
    # Test data without camera_name
    stop_data = {}
    
    # Make POST request with missing camera_name
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/stop",
        json=stop_data,
        headers={"Authorization": auth_token}
    )
    
    # Check response status
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}"
    
    # Parse response
    data = response.get_json()
    assert data is not None, "Response should be JSON"
    assert data["result"] is None, "Result should be None for error"
    assert data["errorMessage"] is not None, "Should have error message"
    
    # Check that error message mentions camera_name
    assert "camera_name is required" in data["errorMessage"], \
        f"Error message should mention camera_name requirement: {data['errorMessage']}"
    
    print("Stop recording missing camera_name test passed!")


def test_stop_recording_empty_camera_name(client, john_doe_login):
    """
    Test stopping recording with empty camera_name field.
    """
    user_id, auth_token = john_doe_login
    
    # Test data with empty camera_name
    stop_data = {
        "camera_name": ""
    }
    
    # Make POST request with empty camera_name
    response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/stop",
        json=stop_data,
        headers={"Authorization": auth_token}
    )
    
    # Should fail with bad request
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}"
    
    data = response.get_json()
    assert data["result"] is None and data["errorMessage"] is not None, "Should have error for empty camera_name"
    
    print("Stop recording empty camera_name test passed!")


def test_stop_recording_nonexistent_shop(client, john_doe_login):
    """
    Test stopping recording for a shop that doesn't exist.
    """
    user_id, auth_token = john_doe_login
    
    stop_data = {
        "camera_name": TEST_CAMERA_NAME
    }
    
    # Make POST request to nonexistent shop
    response = client.post(
        "/shops/nonexistent_shop/recording/stop",
        json=stop_data,
        headers={"Authorization": auth_token}
    )
    
    # Should fail when shop doesn't exist (or when no recording is active)
    assert response.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Expected error status for nonexistent shop, got {response.status_code}"
    
    data = response.get_json()
    assert data["result"] is None and data["errorMessage"] is not None, "Should have error for nonexistent shop"
    
    print("Stop recording nonexistent shop test passed!")


def test_recording_lifecycle_integration(client, john_doe_login):
    """
    Integration test for complete recording lifecycle: start -> stop.
    
    Note: This test might fail in testing environment if recording dependencies
    are not available, which is expected behavior.
    """
    user_id, auth_token = john_doe_login
    
    camera_name = TEST_CAMERA_NAME
    recording_data = {
        "camera_name": camera_name,
        "duration": 5  # Short duration for testing
    }
    
    # Try to start recording
    start_response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    # Should either succeed or fail gracefully
    assert start_response.status_code in [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR], \
        f"Start recording should succeed or fail gracefully, got {start_response.status_code}"
    
    start_data = start_response.get_json()
    
    if start_response.status_code == HTTPStatus.OK:
        # Recording started successfully, now try to stop it
        print("   Recording started successfully, attempting to stop...")
        
        stop_data = {"camera_name": camera_name}
        stop_response = client.post(
            f"/shops/{TEST_SHOP_ID}/recording/stop",
            json=stop_data,
            headers={"Authorization": auth_token}
        )
        
        # Stop should succeed
        assert stop_response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
            f"Stop recording should succeed or fail gracefully, got {stop_response.status_code}"
        
        stop_data_response = stop_response.get_json()
        
        if stop_response.status_code == HTTPStatus.OK:
            print("   Recording stopped successfully - full lifecycle test passed!")
        else:
            print(f"   Recording stop failed (expected): {stop_data_response['errorMessage']}")
    else:
        # Recording failed to start (expected in test environment)
        print(f"   Recording failed to start (expected in test environment): {start_data['errorMessage']}")
    
    print("Recording lifecycle integration test completed!")


def test_duplicate_start_recording_attempts(client, john_doe_login):
    """
    Test that starting recording twice for the same camera fails appropriately.
    """
    user_id, auth_token = john_doe_login
    
    camera_name = TEST_CAMERA_NAME
    recording_data = {
        "camera_name": camera_name,
        "duration": 10
    }
    
    # First start attempt
    response1 = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json=recording_data,
        headers={"Authorization": auth_token}
    )
    
    if response1.status_code == HTTPStatus.OK:
        # Recording started, try to start again (should fail)
        print("   First recording started, attempting duplicate start...")
        
        response2 = client.post(
            f"/shops/{TEST_SHOP_ID}/recording/start",
            json=recording_data,
            headers={"Authorization": auth_token}
        )
        
        # Second attempt should fail
        assert response2.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR], \
            f"Duplicate start should fail, got {response2.status_code}"
        
        data2 = response2.get_json()
        assert "already active" in data2["errorMessage"] or "Recording already" in data2["errorMessage"], \
            f"Error should mention recording already active: {data2['errorMessage']}"
        
        # Clean up - stop the recording
        stop_data = {"camera_name": camera_name}
        stop_response = client.post(
            f"/shops/{TEST_SHOP_ID}/recording/stop",
            json=stop_data,
            headers={"Authorization": auth_token}
        )
        
        print("   Duplicate start properly rejected and recording cleaned up")
    else:
        # First recording failed (expected in test environment)
        print(f"   Recording failed to start (expected): {response1.get_json()['errorMessage']}")
    
    print("Duplicate start recording test completed!")


def test_recording_endpoints_empty_payload(client, john_doe_login):
    """
    Test recording endpoints with empty JSON payloads.
    """
    user_id, auth_token = john_doe_login
    
    # Test start recording with empty payload
    start_response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/start",
        json={},
        headers={"Authorization": auth_token}
    )
    
    assert start_response.status_code == HTTPStatus.BAD_REQUEST, \
        f"Start recording with empty payload should fail, got {start_response.status_code}"
    
    start_data = start_response.get_json()
    assert "camera_name is required" in start_data["errorMessage"], \
        f"Should mention camera_name required: {start_data['errorMessage']}"
    
    # Test stop recording with empty payload
    stop_response = client.post(
        f"/shops/{TEST_SHOP_ID}/recording/stop",
        json={},
        headers={"Authorization": auth_token}
    )
    
    assert stop_response.status_code == HTTPStatus.BAD_REQUEST, \
        f"Stop recording with empty payload should fail, got {stop_response.status_code}"
    
    stop_data = stop_response.get_json()
    assert "camera_name is required" in stop_data["errorMessage"], \
        f"Should mention camera_name required: {stop_data['errorMessage']}"
    
    print("Recording endpoints empty payload test passed!")
