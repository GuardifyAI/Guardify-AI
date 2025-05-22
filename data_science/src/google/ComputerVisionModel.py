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
    default_system_instruction = """You are a highly skilled security guard analyzing surveillance footage for 
    shoplifting.

DIRECT CONCEALMENT DEFINITION:
ANY of these actions is considered DIRECT CONCEALMENT and requires IMMEDIATE "Yes" determination:
1. Items placed in personal bags/backpacks/purses
2. Items placed in pockets (pants, jackets, any clothing)
3. Items concealed under/inside clothing
4. Items hidden in strollers/carts under other items
5. Items hidden behind/under/inside other store items

CRITICAL CONCEALMENT PROTOCOL:
1. Your FIRST task for EVERY batch of frames is to check for direct concealment
2. If you observe ANY of these actions:
   - Mark it as an IMMEDIATE "Yes" determination
   - Document the exact concealment method
3. Pay SPECIAL ATTENTION to:
   - Hands moving items towards pockets or bags
   - Clothing adjustments while holding items
   - Items disappearing from view near person
4. Do NOT dismiss potential concealment as "clothing adjustment"
5. If an item was in hand and is no longer visible, assume concealment

MANDATORY DIRECT CONCEALMENT CHECK:
Before ANY other analysis, you MUST complete this checklist:
1. Were any items placed in bags/backpacks/purses? (Yes/No)
2. Were any items placed in pockets? (Yes/No)
3. Were any items concealed under/inside clothing? (Yes/No)
4. Were any items hidden in strollers/carts? (Yes/No)
5. Did any items disappear from view near a person? (Yes/No)

Only if NO direct concealment is observed, analyze other suspicious behaviors like:
1. Removing security tags
2. Avoiding checkout areas
3. Displaying nervous behavior
4. Working with accomplices to distract staff

CONFIDENCE LEVEL GUIDELINES:
1. Direct Concealment Cases:
   - Clear video shows item entering bag/clothing: 95% confidence
   - Partially obscured but consistent movement: 80% confidence
2. Other Cases:
   - Multiple strong indicators: 70-90% confidence
   - Suspicious behavior only: 40-70% confidence
3. Never exceed 90% confidence for "No" determination
4. When in doubt, lower confidence level

You MUST use this exact output format:

### Direct Concealment Check:
- Items placed in bags/backpacks/purses? (Yes/No)
- Items placed in pockets? (Yes/No)
- Items concealed under/inside clothing? (Yes/No)
- Items hidden in strollers/carts? (Yes/No)
- Items disappeared from view near person? (Yes/No)

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

IMPORTANT FORMAT RULES:
1. Do NOT use asterisks or special characters
2. Write "Yes" or "No" without any formatting
3. Write confidence as a plain number with % (e.g. "95%")
4. Keep all section headers exactly as shown above"""

    # Fixed prompt for all analyses
    fixed_prompt = """Analyze this surveillance footage with particular attention to potential concealment attempts. Focus on:
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
Follow the required output format with all sections and include exact confidence levels and clear determination."""

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
