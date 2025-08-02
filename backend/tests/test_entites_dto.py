from app import create_app
from app.entities.event import Event
from app.entities.shop import Shop
from app.entities.company import Company
from app.entities.user import User
from app.entities.camera import Camera
from app.entities.analysis import Analysis

app = create_app()

def print_first(model):
    result = model.query.first()
    model_name = model.__name__
    if result:
        print(f"✅ {model_name}: {result}")
    else:
        print(f"⚠️  {model_name}: No data found.")

def print_dto(entity_cls, entity_name: str):
    record = entity_cls.query.first()
    if record:
        try:
            dto = record.to_dto()
            print(f"✅ {entity_name} DTO: {dto}")
        except Exception as e:
            print(f"❌ {entity_name} DTO conversion failed: {e}")
    else:
        print(f"⚠️  {entity_name}: No data found.")

with app.app_context():
    # print("🔎 Testing models...")
    # print_first(Company)
    # print_first(Shop)
    # print_first(User)
    # print_first(Camera)
    # print_first(Event)
    # print_first(Analysis)
    print("🔍 Testing DTOs for all entities...")
    print_dto(Company, "Company")
    print_dto(Shop, "Shop")
    print_dto(User, "User")
    print_dto(Camera, "Camera")
    print_dto(Event, "Event")
    print_dto(Analysis, "Analysis")


if __name__ == "__main__":
    app.run(debug=True)