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
from data_science.src.utils import load_env_variables

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

    default_system_instruction = [
        "You are an expert computer vision analyst specializing in retail surveillance.",
        "Your role is to provide comprehensive, structured observations of customer behavior in retail environments.",
        "You excel at detailed behavioral analysis, tracking item interactions, and identifying movement patterns.",
        "You understand the difference between normal shopping behaviors and potentially suspicious activities.",
        "Your observations are factual, detailed, and structured to enable accurate security analysis.",
        "You focus on providing clear, actionable visual evidence that supports informed decision-making."
    ]

    # Enhanced structured response schema for JSON output
    enhanced_cv_response_schema = {
        "type": "object",
        "properties": {
            "person_description": {
                "type": "string",
                "description": "Physical appearance, clothing, and overall movement patterns"
            },
            "item_interactions": {
                "type": "string",
                "description": "Detailed tracking of merchandise handled, sequence, duration, and final disposition"
            },
            "hand_movements": {
                "type": "string",
                "description": "Detailed description of hand movements and body positioning relative to merchandise"
            },
            "behavioral_sequence": {
                "type": "string",
                "description": "Step-by-step sequence of all observed actions with timing and flow"
            },
            "environmental_context": {
                "type": "string",
                "description": "Camera angle, lighting, visibility limitations, and store layout context"
            },
            "suspicious_indicators": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of specific suspicious behaviors observed (if any)"
            },
            "normal_indicators": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of normal shopping behaviors observed (if any)"
            },
            "behavioral_tone": {
                "type": "string",
                "enum": ["highly_suspicious", "moderately_suspicious", "unclear", "mostly_normal", "clearly_normal"],
                "description": "Overall behavioral assessment tone"
            },
            "observation_confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Confidence in observation quality due to camera angle, lighting, etc."
            }
        },
        "required": [
            "person_description",
            "item_interactions", 
            "hand_movements",
            "behavioral_sequence",
            "environmental_context",
            "suspicious_indicators",
            "normal_indicators",
            "behavioral_tone",
            "observation_confidence"
        ]
    }

    # Enhanced prompt for detailed behavioral observation
    enhanced_observation_prompt = """
    ENHANCED RETAIL SURVEILLANCE ANALYSIS - STRUCTURED OBSERVATION MODE

    You are a specialized computer vision system providing detailed behavioral observations for retail security analysis.

    🎯 YOUR MISSION: Provide comprehensive, structured observations of ALL customer behaviors and interactions in JSON format.

    📋 REQUIRED ANALYSIS CATEGORIES:

    **1. PERSON DESCRIPTION & MOVEMENTS:**
    - Physical appearance and clothing
    - Overall movement patterns and positioning
    - Body language and behavioral characteristics
    - Time spent in different areas
    - Direction of movement and path taken

    **2. ITEM INTERACTION ANALYSIS:**
    - Detailed tracking of ALL merchandise handled
    - Sequence of item interactions (pickup, examination, placement)
    - Duration of each item interaction
    - Method of handling (careful examination vs quick grab)
    - Final disposition of each item (returned to shelf, taken with person, etc.)

    **3. HAND MOVEMENT & BODY BEHAVIOR TRACKING:**
    - Detailed description of all hand movements
    - Body positioning relative to merchandise
    - Any adjustments to clothing or personal items
    - Coordination between hand movements and body positioning
    - Timing of movements relative to item interactions

    **4. BEHAVIORAL SEQUENCE DOCUMENTATION:**
    - Step-by-step sequence of all observed actions
    - Timing and flow between different behaviors
    - Patterns in behavior (repetitive actions, systematic approach)
    - Coordination between different types of actions

    **5. ENVIRONMENTAL CONTEXT:**
    - Camera angle and visibility limitations
    - Lighting conditions affecting observation
    - Background activity and distractions
    - Store layout and merchandise arrangement
    - Other customers or staff in vicinity

    **6. SUSPICIOUS BEHAVIOR INDICATORS (list specific behaviors if observed):**
    - Items moved toward body/clothing areas
    - Hand movements to pockets, bags, or waistband areas
    - Body positioning that obscures actions from view
    - Quick or furtive movements
    - Concealment-related behaviors
    - Nervous or surveillance-aware behavior

    **7. NORMAL SHOPPING INDICATORS (list specific behaviors if observed):**
    - Items examined and returned to proper locations
    - Natural browsing and comparison behaviors
    - Normal shopping pace and movements
    - Items moved toward checkout or shopping areas
    - Casual, comfortable body language
    - Typical customer interaction patterns

    **8. BEHAVIORAL TONE ASSESSMENT:**
    Rate the overall behavioral pattern as one of:
    - "highly_suspicious": Clear patterns suggesting theft intent
    - "moderately_suspicious": Some concerning behaviors but not definitive
    - "unclear": Mixed or ambiguous behavioral signals
    - "mostly_normal": Predominantly normal with minor irregularities
    - "clearly_normal": Standard shopping behavior throughout

    **9. OBSERVATION CONFIDENCE:**
    Rate your confidence in these observations (0.0-1.0) based on:
    - Camera angle and visibility quality
    - Lighting and environmental conditions
    - Duration and clarity of observed behaviors

    🔍 ANALYSIS PRINCIPLES:
    - Report everything you observe objectively
    - Focus on behavioral sequences and patterns
    - Distinguish between clear observations and uncertain details
    - Provide context for visibility limitations
    - Use specific, factual descriptions

    Provide your structured observations in the specified JSON format. Be comprehensive and factual in your descriptions.
    """

    default_generation_config = GenerationConfig(
        temperature=0.1,  # Low temperature for consistent, factual observations
        top_p=0.9,  # Slightly broader vocabulary for detailed descriptions
        top_k=40,  # Expanded vocabulary for rich descriptions
        candidate_count=1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=enhanced_cv_response_schema
    )

    # Set safety settings.
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    def __init__(self,
                 model_name: str = os.getenv("DEFAULT_MODEL_ID"),
                 *,
                 generation_config: Optional[GenerationConfigType] = None,
                 safety_settings: Optional[SafetySettingsType] = None,
                 system_instruction: Optional[PartsType] = None,
                 labels: Optional[Dict[str, str]] = None):

        if system_instruction is None:
            system_instruction = self.default_system_instruction

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
            prompt (str, optional): Custom prompt. Uses enhanced prompt if None.
            
        Returns:
            str: Detailed structured observations
        """
        # Use enhanced observation prompt if no custom prompt provided
        if prompt is None:
            prompt = self.enhanced_observation_prompt

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
