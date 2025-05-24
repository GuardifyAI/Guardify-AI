from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    Image
)

from typing import Dict, List, Optional, Union
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType
import os
from data_science.src.utils import load_env_variables
load_env_variables()

class ComputerVisionModel(GenerativeModel):
    """
    ENHANCED COMPUTER VISION MODEL FOR HYBRID ARCHITECTURE
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

    # Enhanced prompt for detailed behavioral observation
    enhanced_observation_prompt = """
    ENHANCED RETAIL SURVEILLANCE ANALYSIS - DETAILED OBSERVATION MODE

    You are a specialized computer vision system providing detailed behavioral observations for retail security analysis.

    🎯 YOUR MISSION: Provide comprehensive, structured observations of ALL customer behaviors and interactions.

    📋 REQUIRED ANALYSIS STRUCTURE:

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

    **6. SUSPICIOUS BEHAVIOR INDICATORS (when observed):**
    - Items moved toward body/clothing areas
    - Hand movements to pockets, bags, or waistband areas
    - Body positioning that obscures actions from view
    - Quick or furtive movements
    - Concealment-related behaviors
    - Nervous or surveillance-aware behavior

    **7. NORMAL SHOPPING INDICATORS (when observed):**
    - Items examined and returned to proper locations
    - Natural browsing and comparison behaviors
    - Normal shopping pace and movements
    - Items moved toward checkout or shopping areas
    - Casual, comfortable body language
    - Typical customer interaction patterns

    🔍 ANALYSIS PRINCIPLES:

    **Comprehensive Documentation:** Report everything you observe, even if it seems minor
    **Behavioral Sequencing:** Focus on the order and timing of actions
    **Context Awareness:** Consider environmental factors affecting your observations
    **Balanced Perspective:** Note both concerning and normal behaviors objectively
    **Evidence Quality:** Clearly distinguish between what you can see clearly vs what is unclear

    📊 STRUCTURED OUTPUT FORMAT:

    For each category above, provide:
    - Clear, factual descriptions
    - Specific timing information when possible
    - Confidence levels for observations ("clearly visible", "partially obscured", "unclear")
    - Relationships between different observed behaviors

    🎯 FOCUS AREAS FOR DETAILED ANALYSIS:

    **Item Trajectory Tracking:**
    - Where items come from (shelf, display, etc.)
    - How they are handled during examination
    - Where they go after interaction (back to shelf, with customer, unclear)

    **Movement Pattern Analysis:**
    - Approach patterns to merchandise
    - Body positioning during interactions
    - Departure patterns and directions

    **Temporal Behavior Analysis:**
    - Duration of different phases of interaction
    - Speed and rhythm of movements
    - Sequence timing and flow

    **Concealment Behavior Detection:**
    - Any movements toward typical concealment areas
    - Body language suggesting hiding or concealing
    - Clothing adjustments or manipulations

    Remember: Your detailed observations will be used by security analysts to make important decisions. Provide comprehensive, accurate, and structured information that enables informed analysis.

    Analyze this surveillance footage and provide detailed, structured observations according to the framework above.
    """

    default_generation_config = GenerationConfig(
        temperature=0.1,  # Low temperature for consistent, factual observations
        top_p=0.9,        # Slightly broader vocabulary for detailed descriptions
        top_k=40,         # Expanded vocabulary for rich descriptions
        candidate_count=1,
        max_output_tokens=8192,
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

        super().__init__(model_name=model_name
                         , generation_config=generation_config
                         , safety_settings=safety_settings
                         , system_instruction=system_instruction
                         , labels=labels)

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
        Provide structured video analysis with categorized observations.
        
        Args:
            video_file (Part): Video file part object
            
        Returns:
            Dict[str, str]: Structured observations organized by category
        """
        observations = self.analyze_video(video_file)
        
        # Parse the structured response into categories
        # This is a simple text-based parsing - could be enhanced with JSON schema
        structured_data = {
            "full_observations": observations,
            "person_description": self._extract_section(observations, "PERSON DESCRIPTION"),
            "item_interactions": self._extract_section(observations, "ITEM INTERACTION"),
            "hand_movements": self._extract_section(observations, "HAND MOVEMENT"),
            "behavioral_sequence": self._extract_section(observations, "BEHAVIORAL SEQUENCE"),
            "environmental_context": self._extract_section(observations, "ENVIRONMENTAL CONTEXT"),
            "suspicious_indicators": self._extract_section(observations, "SUSPICIOUS BEHAVIOR"),
            "normal_indicators": self._extract_section(observations, "NORMAL SHOPPING")
        }
        
        return structured_data
    
    def _extract_section(self, text: str, section_keyword: str) -> str:
        """
        Extract specific section from structured observations.
        
        Args:
            text (str): Full observation text
            section_keyword (str): Keyword to identify section
            
        Returns:
            str: Extracted section content
        """
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section_keyword.upper() in line.upper():
                in_section = True
                continue
            elif line.strip().startswith('**') and in_section:
                # New section started
                break
            elif in_section and line.strip():
                section_content.append(line.strip())
                
        return ' '.join(section_content) if section_content else "Not found in observations"


