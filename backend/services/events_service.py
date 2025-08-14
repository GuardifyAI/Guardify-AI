from datetime import datetime
from werkzeug.exceptions import NotFound
from backend.app.entities import Event
from backend.app.entities.analysis import Analysis
from backend.app.dtos import AnalysisDTO
from backend.app.request_bodies.analysis_request_body import AnalysisRequestBody
from backend.db import db, save_and_refresh
from utils.env_utils import load_env_variables
load_env_variables()


class EventsService:

    def get_event_analysis(self, event_id: str) -> AnalysisDTO:
        if not event_id or str(event_id).strip() == "":
            raise ValueError("Event ID is required")
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            raise NotFound(f"Event with ID '{event_id}' does not exist")

        # Query the analysis for the event
        analysis = Analysis.query.filter_by(event_id=event_id).first()
        if not analysis:
            raise NotFound(f"Analysis for event ID '{event_id}' does not exist")

        # Convert to DTOs
        return analysis.to_dto()

    def create_event_analysis(self, event_id: str, analysis_req_body: AnalysisRequestBody) -> AnalysisDTO:
        if not event_id or str(event_id).strip() == "":
            raise ValueError("Event ID is required")
            
        # Check if event exists
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            raise NotFound(f"Event with ID '{event_id}' does not exist")
            
        try:
            # Create Analysis entity
            new_analysis = Analysis(
                event_id=event_id,
                final_detection=analysis_req_body.final_detection,
                final_confidence=analysis_req_body.final_confidence,
                decision_reasoning=analysis_req_body.decision_reasoning,
                analysis_timestamp=datetime.fromisoformat(datetime.now().isoformat()),
            )

            # Save and refresh the entity
            save_and_refresh(new_analysis)

            # Convert to DTO - this might be where the error occurs
            result_dto = new_analysis.to_dto()
            return result_dto

        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            raise Exception(f"Failed to create event analysis: {str(e)}")