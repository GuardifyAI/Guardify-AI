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