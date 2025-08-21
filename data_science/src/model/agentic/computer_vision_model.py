from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, Optional
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType
import os

from data_science.src.model.agentic.prompt_and_scheme.computer_vision_prompt import enhanced_response_schema, \
    default_system_instruction, enhanced_observation_prompt
from utils import load_env_variables

load_env_variables()


class ComputerVisionModel(GenerativeModel):
    """
    ENHANCED COMPUTER VISION MODEL FOR AGENTIC ARCHITECTURE
    ======================================================
    
    This upgraded CV model provides detailed, structured observations specifically 
    designed to feed into the AnalysisModel for optimal theft detection.
    
    Key Improvements:
    - Enhanced behavioral pattern recognition
    - Structured observation format for better analysis
    - Focus on actionable visual evidence
    - Balanced perspective on normal vs suspicious behavior
    """

    default_generation_config = GenerationConfig(
        temperature=0.1,  # Low temperature for consistent, factual observations
        top_p=0.9,  # Slightly broader vocabulary for detailed descriptions
        top_k=40,  # Expanded vocabulary for rich descriptions
        candidate_count=1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=enhanced_response_schema
    )

    # Set safety settings.
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    def __init__(self,
                 # default to the DEFAULT_CV_MODEL_ID environment variable if not provided. if also this is not provided, default to DEFAULT_MODEL_ID.
                 model_name: str = os.getenv("DEFAULT_CV_MODEL_ID", os.getenv("DEFAULT_MODEL_ID")),
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

    def analyze_video(self, video_file: Part, prompt: Optional[str] = None) -> str:
        """
        Enhanced video analysis with structured observation approach.
        
        Args:
            video_file (Part): Video file part object
            prompt (str, optional): Custom prompt_and_scheme. Uses enhanced prompt_and_scheme if None.
            
        Returns:
            str: Detailed structured observations
        """
        # Use enhanced observation prompt_and_scheme if no custom prompt_and_scheme provided
        if prompt is None:
            prompt = enhanced_observation_prompt

        contents = [video_file, prompt]

        # Generate comprehensive observations
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        return response.text

    def analyze_video_structured(self, video_file: Part) -> Dict[str, str]:
        """
        Provide structured video analysis with JSON response format.
        
        Args:
            video_file (Part): Video file part object
            
        Returns:
            Dict[str, str]: Structured observations organized by category
        """
        observations = self.analyze_video(video_file)

        try:
            # Parse JSON response directly
            import json
            structured_data = json.loads(observations)
            
            # Add full observations for compatibility
            structured_data["full_observations"] = observations
            
            return structured_data
            
        except json.JSONDecodeError:
            # Return default structured response if JSON parsing fails
            return {
                "full_observations": observations,
                "person_description": "Unable to parse structured response",
                "item_interactions": "Unable to parse structured response", 
                "hand_movements": "Unable to parse structured response",
                "behavioral_sequence": "Unable to parse structured response",
                "environmental_context": "Unable to parse structured response",
                "suspicious_indicators": [],
                "normal_indicators": [],
                "behavioral_tone": "unclear",
                "observation_confidence": 0.1
            }
