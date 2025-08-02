from app import db

class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'))
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.camera_id'))
    event_timestamp = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String, nullable=True)
    video_url = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Event {self.event_id} | Shop {self.shop_id} | Camera {self.camera_id} | Description {self.description}>"
