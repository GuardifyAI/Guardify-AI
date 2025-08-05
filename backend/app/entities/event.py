from app import db
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EventDTO:
    event_id: str
    shop_id: str
    camera_id: str
    event_timestamp: datetime | None
    description: str | None
    video_url: str | None

class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'))
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.camera_id'))
    event_timestamp = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String, nullable=True)
    video_url = db.Column(db.String, nullable=True)

    def __repr__(self):
        description_str = self.description if self.description is not None else "N/A"
        return f"<Event {self.event_id} | Shop {self.shop_id} | Camera {self.camera_id} | Description {description_str}>"

    def to_dto(self) -> EventDTO:
        return EventDTO(
            event_id=self.event_id,
            shop_id=self.shop_id,
            camera_id=self.camera_id,
            event_timestamp=self.event_timestamp,
            description=self.description,
            video_url=self.video_url,
        )
    

