from app import create_app, db
from app.models.event import Event

app = create_app()

with app.app_context():
    first_event = Event.query.first()
    if first_event:
        print("First Event:", first_event)
    else:
        print("No events found in the database.")

if __name__ == "__main__":
    app.run(debug=True)
