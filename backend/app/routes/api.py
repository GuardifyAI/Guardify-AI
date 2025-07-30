from flask import Blueprint, request, jsonify
from app.models.event import Event
from app import db
from datetime import datetime

api = Blueprint('api', __name__)

@api.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([e.serialize() for e in events])

@api.route("/event", methods=["POST"])
def create_event():
    data = request.get_json()
    event = Event(
        shop_id=data["shop_id"],
        camera_name=data["camera_name"],
        timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
        description=data["description"],
        final_detection=data["final_detection"],
        confidence=data["confidence"],
        video_url=data.get("video_url", "")
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Event created"}), 201
