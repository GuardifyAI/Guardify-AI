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

    default_system_instruction = [
        "You are a highly skilled security guard working at a retail store.",
        "Your main responsibility is to monitor customer behavior and identify potential shoplifting activities.",
    ]

    # Fixed prompt for all analyses
    fixed_prompt = """
    As a virtual security guard, your task is to observe the provided video and identify potential shoplifting activities. Please analyze the video following the steps below:
    1. Initial Surveillance:
   -   Scan the store layout, noting the placement of entrances, exits, aisles, and checkout areas.
   -   Identify any customers present and observe their initial movements upon entering the store.

    2. Detailed Observation:
   -   Focus on any customer who may be exhibiting any behaviors that may be considered suspicious.
   -   Note any instances of customers lingering in areas with merchandise without apparent intent to purchase.
   -   Look for any customers handling items in a way that may indicate an attempt to conceal them.

    3. Behavior Analysis:
   -   Observe if any items are being hidden from view.
   -   Note any attempts to alter the state of items, remove packaging.
   -   Are any items being taken towards an exit?
   -   Are any items being concealed under the clothing or in bags?

    4. Situation Assessment:
   -   Combine the observed details to assess whether these behaviors cumulatively suggest a potential for shoplifting.

    5. Reporting:
   -   Describe in detail the specific behaviors, their exact locations within the store, and the exact time they happened.
   -   Justify why these actions may suggest potential shoplifting.
   -   Maintain a polite and professional tone, focusing on observed actions rather than making assumptions about intent.
    """

    default_generation_config = GenerationConfig(
        temperature=0,
        top_p=1.0,
        top_k=32,
        candidate_count=1,
        max_output_tokens=8192,
    )

    # Set safety settings.
    # Dont know what does it mean, need to investigate
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


