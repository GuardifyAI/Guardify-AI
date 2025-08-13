from backend.db import db
from backend.app.dtos import AnalysisDTO


class Analysis(db.Model):
    __tablename__ = 'analysis'

    event_id = db.Column(db.String, db.ForeignKey('event.event_id'), primary_key=True)
    final_detection = db.Column(db.Boolean, nullable=True)
    final_confidence = db.Column(db.Numeric, nullable=True)
    decision_reasoning = db.Column(db.Text, nullable=True)
    analysis_timestamp = db.Column(db.DateTime, nullable=True)

    event = db.relationship('Event', back_populates='analysis')
    
    def __repr__(self):
        final_detection_str = self.final_detection if self.final_detection is not None else "N/A"
        confidence_str = self.final_confidence if self.final_confidence is not None else "N/A"
        return f"<Analysis {self.event_id} | Final Detection: {final_detection_str} | Confidence: {confidence_str}>"
    
    def to_dto(self, detailed: bool = True) -> AnalysisDTO:
        if detailed:
            return AnalysisDTO(
                event_id=self.event_id,
                final_detection=self.final_detection,
                final_confidence=self.final_confidence,
                decision_reasoning=self.decision_reasoning,
                analysis_timestamp=self.analysis_timestamp,
            )
        else:
            # Return minimal analysis data when detailed=False
            return AnalysisDTO(
                event_id=self.event_id,
                final_detection=self.final_detection,
                final_confidence=self.final_confidence,
                decision_reasoning=None,  # Exclude detailed reasoning
                analysis_timestamp=self.analysis_timestamp,
            )