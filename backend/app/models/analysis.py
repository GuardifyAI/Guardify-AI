from app import db

class Analysis(db.Model):
    __tablename__ = 'analysis'

    event_id = db.Column(db.String, db.ForeignKey('event.event_id'), primary_key=True)
    final_detection = db.Column(db.Boolean)
    final_confidence = db.Column(db.Numeric)
    decision_reasoning = db.Column(db.Text)
    analysis_timestamp = db.Column(db.DateTime)

    event = db.relationship('Event', backref='analysis')
    
    def __repr__(self):
        return f"<Analysis {self.event_id} | Final Detection: {self.final_detection} | Confidence: {self.final_confidence}>"