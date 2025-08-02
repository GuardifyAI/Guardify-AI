from app import db

class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer)
    camera_id = db.Column(db.Integer)
    event_timestamp = db.Column(db.DateTime)
    description = db.Column(db.String)
    video_url = db.Column(db.String)

    def __repr__(self):
        return f"<Event {self.event_id} | Shop {self.shop_id} | Camera {self.camera_id} | Description {self.description}>"
