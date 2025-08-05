from backend.app.entities.event import Event
from backend.app.entities.shop import Shop
from backend.app.entities.company import Company
from backend.app.entities.user import User
from backend.app.entities.camera import Camera
from backend.app.entities.analysis import Analysis
from backend.run import app
import pytest
from backend.controller import Controller
from backend.app import create_app
from http import HTTPStatus

def print_first(model):
    result = model.query.first()
    model_name = model.__name__
    if result:
        print(f"✅ {model_name}: {result}")
    else:
        print(f"⚠️  {model_name}: No data found.")

def print_first_dto(entity_cls, entity_name: str):
    record = entity_cls.query.first()
    if record:
        try:
            dto = record.to_dto()
            print(f"✅ {entity_name} DTO: {dto}")
        except Exception as e:
            print(f"❌ {entity_name} DTO conversion failed: {e}")
    else:
        print(f"⚠️  {entity_name}: No data found.")

def test_print_first():
    with app.app_context():
        print("🔎 Testing models...")
        print_first(Company)
        print_first(Shop)
        print_first(User)
        print_first(Camera)
        print_first(Event)
        print_first(Analysis)

def test_print_first_dto():
    with app.app_context():
        print("🔍 Testing DTOs for all entities...")
        print_first_dto(Company, "Company")
        print_first_dto(Shop, "Shop")
        print_first_dto(User, "User")
        print_first_dto(Camera, "Camera")
        print_first_dto(Event, "Event")
        print_first_dto(Analysis, "Analysis")

@pytest.fixture
def client():
    app = create_app()
    Controller(app)  # Set up routes
    app.testing = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/app/health")
    assert response.status_code == HTTPStatus.OK
    assert response.is_json

    data = response.get_json()
    assert "result" in data
    assert "errorMessage" in data

    assert data["result"] == "OK"
    assert data["errorMessage"] in ("", None)

def test_error_handling(client):
    response = client.get("/app/error")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.is_json

    data = response.get_json()
    assert "result" in data
    assert "errorMessage" in data

    assert data["result"] is None
    assert isinstance(data["errorMessage"], str)
    assert len(data["errorMessage"]) > 0

def test_cache(client):
    payload = {"number": 7}

    # First request: should take longer and return a fresh result
    response1 = client.post("/app/test", json=payload)
    assert response1.status_code == HTTPStatus.OK
    data1 = response1.get_json()
    assert "result" in data1
    first_result = data1["result"]
    assert first_result["input"] == 7
    assert first_result["square"] == 49
    first_timestamp = first_result["timestamp"]

    # Second request: should be instant and return cached result (same timestamp)
    response2 = client.post("/app/test", json=payload)
    assert response2.status_code == HTTPStatus.OK
    data2 = response2.get_json()
    second_result = data2["result"]
    assert second_result["input"] == 7
    assert second_result["square"] == 49
    second_timestamp = second_result["timestamp"]

    # The timestamp should be the same, indicating the result was cached
    assert first_timestamp == second_timestamp

def test_clear_cache(client):
    payload = {"number": 7}

    # First request: get initial result and timestamp
    response1 = client.post("/app/test", json=payload)
    assert response1.status_code == HTTPStatus.OK
    data1 = response1.get_json()
    first_result = data1["result"]
    first_timestamp = first_result["timestamp"]

    # Clear the cache
    clear_response = client.post("/app/cache/clear")
    assert clear_response.status_code == HTTPStatus.OK
    clear_data = clear_response.get_json()
    assert clear_data["result"] == "Cache cleared successfully"
    assert clear_data["errorMessage"] is None

    # Second request: should return a new result with a new timestamp
    response2 = client.post("/app/test", json=payload)
    assert response2.status_code == HTTPStatus.OK
    data2 = response2.get_json()
    second_result = data2["result"]
    second_timestamp = second_result["timestamp"]

    # The timestamp should be different, indicating the calculation was performed again
    assert first_timestamp != second_timestamp