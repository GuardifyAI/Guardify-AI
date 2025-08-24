from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory
)

from typing import Dict, Optional
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType
import os

from data_science.src.model.agentic.prompt_and_scheme.event_description_prompt import (
    default_system_instruction,
    event_description_response_schema
)
from utils import load_env_variables

load_env_variables()


class EventDescriptionModel(GenerativeModel):
    """
    EVENT DESCRIPTION MODEL FOR RETAIL SECURITY EVENTS
    =================================================
    
    This specialized model generates concise, professional event descriptions
    from detailed security analysis decision reasoning.
    
    Key Features:
    - Generates 1-6 word descriptions
    - Professional security terminology
    - Consistent formatting and style
    - Focused on actionable information
    - Low temperature for consistent outputs
    """

    default_generation_config = GenerationConfig(
        temperature=0.1,  # Very low for consistent, focused descriptions
        top_p=0.7,  # Focused vocabulary for professional terminology
        top_k=10,  # Conservative selection for consistency
        candidate_count=1,
        max_output_tokens=500,  # Increased for JSON response formatting
        response_mime_type="application/json",
        response_schema=event_description_response_schema
    )

    # Set safety settings - allow security-related content
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,  # Allow security content
    }

    def __init__(self,
                 model_name: str = os.getenv("DEFAULT_MODEL_ID"),
                 *,
                 generation_config: Optional[GenerationConfigType] = None,
                 safety_settings: Optional[SafetySettingsType] = None,
                 system_instruction: Optional[PartsType] = None,
                 labels: Optional[Dict[str, str]] = None):

        if system_instruction is None:
            system_instruction = default_system_instruction

        if generation_config is None:
            generation_config = self.default_generation_config

        if safety_settings is None:
            safety_settings = self.default_safety_settings

        super().__init__(model_name=model_name,
                         generation_config=generation_config,
                         safety_settings=safety_settings,
                         system_instruction=system_instruction,
                         labels=labels)

    def generate_description(self, decision_reasoning: str) -> str:
        """
        Generate a concise event description from decision reasoning.
        
        Args:
            decision_reasoning (str): The detailed decision reasoning from analysis
            
        Returns:
            str: Concise 1-6 word event description
            
        Raises:
            Exception: If generation fails
        """
        if not decision_reasoning or not decision_reasoning.strip():
            return "Analysis completed"
        
        # Prepare a concise prompt with the decision reasoning
        prompt = f"""
Generate a concise 1-6 word description of what the person was actually doing in this video:

ANALYSIS: {decision_reasoning[:500]}

Focus on OBSERVABLE ACTIONS, not security classifications.

Examples:
- "Person checking phone while shopping"
- "Customer examining product labels"
- "Individual browsing clothing rack"
- "Person putting item in pocket"
- "Shopper comparing two products"

Respond with JSON containing only the event_description field.
"""
        
        try:
            # Generate the description
            response = self.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from model")
            
            # Parse JSON response
            import json
            result = json.loads(response.text)
            description = result.get("event_description", "").strip()
            
            if not description:
                raise Exception("Empty description in response")
            
            # Ensure it's not too long (fallback validation)
            words = description.split()
            if len(words) > 6:
                description = " ".join(words[:6])
            
            return description
            
        except Exception as e:
            raise Exception(f"Failed to generate event description: {str(e)}")