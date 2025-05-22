from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    Image
)

from typing import Dict, List, Optional, Union
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType, GenerationResponse
from typing import Tuple
import os
import json
from data_science.src.utils import load_env_variables
load_env_variables()

class AnalysisModel(GenerativeModel):

    default_system_instruction = """You are a security analyst reviewing surveillance frames to determine whether shoplifting is occurring.
You will analyze frames sequentially in batches, taking into account previous observations and conclusions.

Focus on suspicious behaviors like:
1. Concealing items in clothing, bags, or containers
2. Removing security tags
3. Avoiding checkout areas
4. Displaying nervous behavior
5. Working with accomplices to distract staff

When analyzing each batch, consider:
- How the current observations relate to previous findings
- Whether suspicious behaviors are continuing or changing
- New individuals entering the scene
- The progression of events over time

Strictly follow this output format using the exact section headers and structure:

### Summary of Current Batch:
- Summarize behaviors in current frames using bullet points
- Note any continuation or changes from previous observations

### Connection to Previous Analysis:
- How current observations relate to previous findings
- Whether suspicious behaviors are escalating or diminishing
- New developments or patterns emerging

### Shoplifting Determination: Yes / No
### Confidence Level: XX%
### Key Behaviors Supporting Conclusion:
- Bullet 1
- Bullet 2
- Bullet 3

Make sure:
- You always include all 5 parts of the conclusion section
- Each part is labeled exactly as shown
- Confidence Level must be numeric, in this format: 'XX%'"""

    default_prompt = """Analyze the provided video and cv_model's observations to assess the likelihood of shoplifting.
Focus on:
1. Each person's behavior and movements
2. Interactions with merchandise
3. Potential concealment attempts
4. Unusual patterns or behaviors
5. Context of the retail environment

Provide detailed observations about any suspicious activities or behaviors following the required output format with all sections.
Remember to include exact confidence levels and clear determination."""

    default_generation_config = GenerationConfig(
        temperature=0.3,  # Slightly increased to allow for more nuanced analysis
        top_p=0.95,      # Slightly reduced to maintain focus while allowing flexibility
        top_k=40,        # Increased to consider more token options
        candidate_count=1,
        max_output_tokens=8192,
    )

    # Set safety settings to be less restrictive for security analysis
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
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

    def analyze_video_observations(self, video_file: Part, video_observations: str, prompt: str = None) -> Tuple[str, bool, float]:
        """
        Analyze video observations and determine if shoplifting occurred.
        
        Args:
            video_file: The video file to analyze
            video_observations: Previous observations from the CV model
            prompt: Optional custom prompt to use
            
        Returns:
            Tuple containing:
            - Full analysis text
            - Boolean indicating if shoplifting was detected
            - Confidence level (0-1)
        """
        if prompt is None:
            prompt = self.default_prompt
        
        # Add the CV model's observations to the prompt
        full_prompt = f"{prompt}\n\nPrevious CV Model Observations:\n{video_observations}"
        
        # Set contents to send to the model
        contents = [video_file, full_prompt]
        
        # Generate the analysis
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        # Parse the response to extract determination and confidence
        analysis_text = response.text
        shoplifting_detected = "Yes" in analysis_text.split("### Shoplifting Determination:")[1].split("\n")[0]
        confidence_str = analysis_text.split("### Confidence Level:")[1].split("\n")[0].strip().replace("%", "")
        confidence_level = float(confidence_str) / 100  # Convert percentage to decimal

        return analysis_text, shoplifting_detected, confidence_level

    def _extract_values_from_response(self, response: GenerationResponse) -> Tuple[bool, float]:
        response_json = json.loads(response.text)
        return response_json["Shoplifting Detected"], response_json["Confidence Level"]


