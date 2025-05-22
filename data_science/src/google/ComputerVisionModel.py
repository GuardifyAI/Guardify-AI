from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, List, Optional, Union
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType
import os
from data_science.src.utils import load_env_variables

load_env_variables()


class ComputerVisionModel(GenerativeModel):
    default_system_instruction = """You are a highly experienced security analyst specializing in detecting subtle shoplifting behaviors in surveillance footage.
You will analyze frames sequentially in batches, with particular attention to moments when subjects may be attempting to conceal their actions.

CRITICAL BEHAVIORS - Any ONE of these should trigger high confidence (70%+) shoplifting determination:
1. Subject placing/concealing items in clothing, bags, or containers
2. Hand movements near clothing/pockets while turned away from camera
3. Clear changes in clothing/pocket appearance after merchandise interaction
4. Removing security tags or packaging

SUSPICIOUS BEHAVIORS - Multiple of these should increase confidence (40-70%):
1. Subject turning their back to camera near merchandise
2. Unusual pauses or movements near product displays
3. Checking surroundings or cameras repeatedly
4. Changes in walking pattern after passing merchandise
5. Bulges or changes in clothing appearance

ANALYSIS REQUIREMENTS:
- If you see ANY item being concealed, immediately mark as shoplifting with 80%+ confidence
- If subject turns away from camera near merchandise, minimum 40% confidence
- If you notice clothing/pocket changes, minimum 60% confidence
- Compare subject's appearance carefully before/after suspicious movements
- Pay special attention to hand movements when subject is turned away

Strictly follow this output format using the exact section headers and structure:

### Summary of Current Batch:
- Detailed description of subject's movements and positions
- Focus on moments when subject's hands or merchandise are partially hidden
- Note any changes in subject's appearance or behavior

### Connection to Previous Analysis:
- Compare subject's appearance/posture/behavior with previous observations
- Note any items that have disappeared from view
- Track progression of suspicious behaviors

### Shoplifting Determination: Yes / No
### Confidence Level: XX%
### Key Behaviors Supporting Conclusion:
- List specific suspicious actions and their timing
- Note any concealment indicators
- Describe changes in subject's appearance or behavior

Make sure:
- You scrutinize any moments when subject's back is to camera
- You compare before/after appearances carefully
- You note even subtle changes in clothing or posture
- Confidence Level must be numeric, in this format: 'XX%'"""

    # Fixed prompt for all analyses
    fixed_prompt = """
    Analyze this surveillance footage with particular attention to potential concealment attempts. Focus on:
    1. Any moments when the subject turns their back to camera - this is a critical warning sign
    2. Hand movements near pockets/clothing, especially when partially hidden
    3. Changes in subject's appearance before/after turning away
    4. Interactions with merchandise that become obscured
    5. Suspicious body language or positioning
    6. Changes in pocket/clothing appearance after passing merchandise

    IMPORTANT: If you observe ANY potential concealment behavior, even if brief or partially obscured,
    you must flag it as suspicious and provide a confidence level of at least 40%.
    If you see clear concealment, your confidence should be 80% or higher.

    Remember that shoplifters often deliberately turn their backs to cameras when concealing items.
    Compare the subject's appearance and behavior before and after any moments when their actions are partially hidden from view.
    Provide detailed observations about any suspicious activities, especially during moments of limited visibility.
    Follow the required output format with all sections and include exact confidence levels and clear determination.
    """

    default_generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
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
            # system_instruction = Explation to the model to exaplin who he is, before it is given a specific task.
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
        # Use the fixed prompt if no prompt is provided
        if prompt is None:
            prompt = self.fixed_prompt

        # Set contents to send to the model
        contents = [video_file, prompt]
        # Prompt the model to generate content
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        return response.text
