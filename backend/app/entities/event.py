from backend.db import db
from backend.app.dtos import EventDTO


class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.String, primary_key=True)
    shop_id = db.Column(db.String, db.ForeignKey('shop.shop_id'))
    camera_id = db.Column(db.String, db.ForeignKey('camera.camera_id'))
    event_timestamp = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String, nullable=True)
    video_url = db.Column(db.String, nullable=True)

    # Relationships
    shop = db.relationship('Shop', backref='events', lazy='select')
    camera = db.relationship('Camera', backref='events', lazy='select')
    analysis = db.relationship('Analysis', back_populates='event', uselist=False, lazy='select')

    def __repr__(self):
        description_str = self.description if self.description is not None else "N/A"
        return f"<Event {self.event_id} | Shop {self.shop_id} | Camera {self.camera_id} | Description {description_str}>"

    def to_dto(self, include_analysis: bool = False) -> EventDTO:
        return EventDTO(
            event_id=self.event_id,
            shop_id=self.shop_id,
            camera_id=self.camera_id,
            event_timestamp=self.event_timestamp,
            description=self.description,
            video_url=self.video_url,
            shop_name=self.shop.name if self.shop else None,
            camera_name=self.camera.camera_name if self.camera else None,
            event_datetime=self.event_timestamp.isoformat() if self.event_timestamp else None,
            analysis=self.analysis.to_dto() if include_analysis and self.analysis else None,
        )
