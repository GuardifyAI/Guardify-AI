from app import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, nullable=False)
    camera_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    final_detection = db.Column(db.Boolean, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    video_url = db.Column(db.String(255), nullable=True)
