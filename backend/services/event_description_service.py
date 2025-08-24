"""
Event Description Service for generating AI-powered event descriptions.

This service uses the EventDescriptionModel to generate concise, professional
event descriptions from detailed decision reasoning.
"""
from typing import Optional
from data_science.src.model.agentic.event_description_model import EventDescriptionModel
from utils.logger_utils import create_logger


class EventDescriptionService:
    """
    Service for generating concise event descriptions using AI.
    
    This service provides a clean interface for generating professional
    event descriptions from analysis decision reasoning, with proper
    error handling and fallbacks.
    """
    
    def __init__(self):
        """Initialize the event description service."""
        self.logger = create_logger("EventDescriptionService", "event_description_service.log")
        self._model: Optional[EventDescriptionModel] = None
    
    def _get_model(self) -> EventDescriptionModel:
        """
        Lazy initialization of the EventDescriptionModel.
        
        Returns:
            EventDescriptionModel: Initialized model instance
        """
        if self._model is None:
            self.logger.info("Initializing EventDescriptionModel...")
            self._model = EventDescriptionModel()
            self.logger.info("EventDescriptionModel initialized successfully")
        return self._model
    
    def generate_event_description(self, decision_reasoning: str) -> str:
        """
        Generate a concise event description from decision reasoning.
        
        Args:
            decision_reasoning (str): The detailed decision reasoning from analysis
            
        Returns:
            str: Concise 1-6 word event description
        """
        try:
            # Input validation
            if not decision_reasoning or not decision_reasoning.strip():
                self.logger.warning("Empty decision reasoning provided, using fallback")
                return self._get_fallback_description(decision_reasoning)
            
            self.logger.info(f"Generating event description from reasoning: {decision_reasoning[:100]}...")
            
            # Get model and generate description
            model = self._get_model()
            description = model.generate_description(decision_reasoning)
            
            # Validate result
            if not description or not description.strip():
                self.logger.warning("Model returned empty description, using fallback")
                return self._get_fallback_description(decision_reasoning)
            
            # Clean up the description
            description = description.strip()
            
            # Ensure it's not too long (safety check)
            words = description.split()
            if len(words) > 6:
                description = " ".join(words[:6])
                self.logger.info(f"Truncated description to 6 words: {description}")
            
            self.logger.info(f"Generated event description: {description}")
            return description
            
        except Exception as e:
            self.logger.error(f"Failed to generate event description: {e}")
            return self._get_fallback_description(decision_reasoning)
    
    def _get_fallback_description(self, decision_reasoning: str) -> str:
        """
        Generate a fallback description focusing on observable actions.
        
        Args:
            decision_reasoning (str): The decision reasoning to analyze
            
        Returns:
            str: Simple fallback description of observed activity
        """
        if not decision_reasoning:
            return "Customer in store"
        
        text = decision_reasoning.lower()
        
        # Extract key observable activities
        if any(keyword in text for keyword in ['phone', 'smartphone', 'mobile', 'screen']):
            return "Person checking phone"
        
        elif any(keyword in text for keyword in ['pocket', 'putting', 'placed in', 'concealed']):
            return "Person putting item in pocket"
        
        elif any(keyword in text for keyword in ['examining', 'looking at', 'inspecting', 'product']):
            return "Customer examining products"
        
        elif any(keyword in text for keyword in ['browsing', 'walking', 'moving through']):
            return "Customer browsing store"
        
        elif any(keyword in text for keyword in ['basket', 'cart', 'shopping']):
            return "Person with shopping basket"
        
        elif any(keyword in text for keyword in ['comparing', 'selecting']):
            return "Customer selecting products"
        
        elif any(keyword in text for keyword in ['checkout', 'cashier', 'paying']):
            return "Customer at checkout"
        
        elif any(keyword in text for keyword in ['clothing', 'trying on', 'fitting']):
            return "Customer examining clothing"
        
        # Generic fallback based on common activities
        else:
            return "Customer in store"