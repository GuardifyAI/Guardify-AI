
from app import create_app, db
from app.models.event import Event
from app.models.shop import Shop
from app.models.company import Company
from app.models.user import User
from app.models.camera import Camera
from app.models.analysis import Analysis

app = create_app()

def print_first(model):
    result = model.query.first()
    model_name = model.__name__
    if result:
        print(f"✅ {model_name}: {result}")
    else:
        print(f"⚠️  {model_name}: No data found.")

with app.app_context():
    print("🔎 Testing models...")
    print_first(Company)
    print_first(Shop)
    print_first(User)
    print_first(Camera)
    print_first(Event)
    print_first(Analysis)

if __name__ == "__main__":
    app.run(debug=True)