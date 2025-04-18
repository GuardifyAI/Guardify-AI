import os
import json
import base64
import argparse
import re
import logging
from glob import glob
from tqdm import tqdm
from typing import List, Optional, Dict, Any
from azure.utils import load_env_variables
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.utils import create_logger, restructure_analysis, encode_image_to_base64

# Load environment variables
load_env_variables()


class PromptModel:
    def __init__(self, logger: Optional[logging.Logger] = None, system_prompt: str = None):
        """
        Initialize the PromptModel for generating prompts for CV analysis.

        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('PromptModel', 'shoplifting_analysis.log')
        else:
            self.logger = logger

        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Check if credentials are set
        if not self.api_key or not self.endpoint:
            self.logger.error("Azure OpenAI credentials not found")
            raise ValueError(
                "Azure OpenAI credentials not found. Please set the following environment variables:\n"
                "  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key\n"
                "  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL\n"
                "  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name"
            )

        # Create the endpoint URL
        if self.deployment_name and "deployments" not in self.endpoint:
            self.endpoint = f"{self.endpoint}/openai/deployments/{self.deployment_name}"

        self.logger.info("Initializing Azure OpenAI client for PromptModel")
        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
        self.logger.info("Azure OpenAI client initialized successfully")

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """
        As an assistant to the cv_model, your primary function is to help it perform its duties as a virtual security guard in a retail environment.
        Your role is to craft detailed prompts that will enable the cv_model to monitor customer behavior accurately and identify potential shoplifting activities by breaking down these complex tasks into smaller, more manageable steps.
        This approach is similar to how a human would tackle a complex problem, enhancing the cv_model’s ability to process and analyze situations effectively.
        Here's how you might construct a structured prompt for the cv_model:
        Imagine you are a highly skilled security guard working at a retail store.
        Your main responsibility is to monitor customer behavior and identify potential shoplifting activities.
        Break down your observation process into the following steps:
        Initial Surveillance: Scan the store entrance and aisles.
        Look for customers who avoid eye contact with staff or surveillance cameras, or those carrying empty bags.
        Detailed Observation: Focus on individuals who exhibit unusual or suspicious movements, such as concealing items or lingering in certain areas without a clear purpose.
        Behavior Analysis: Note behaviors like repeatedly entering and exiting the store without purchases, or carrying fuller bags after visiting the store.
        Pay special attention to customers who take items and do not head towards the checkout counters, as this could indicate an intent to shoplift.
        Situation Assessment: Combine the observed details to assess whether these behaviors cumulatively suggest a potential for shoplifting.
        Reporting: Describe in detail the specific behaviors, the exact locations within the store, and articulate why these actions may suggest potential shoplifting.
        Ensure that your report is polite and professional, focusing on behavior rather than personal attributes to avoid bias and false accusations.
        Each step should guide you through the task, making it easier to process complex information and make accurate judgments.
        This structured approach will help you enhance your observational techniques, distinguishing effectively between normal customer behavior and potential security risks.
        Your prompts should be clear, instructive, and carefully designed to assist the cv_model in processing and reporting information efficiently, by breaking complex observations into smaller analytical tasks.
        Each prompt should refine the cv_model's ability to observe and evaluate with precision.
        """

    def generate_prompt(self) -> str:
        # Create user message
        user_message = """
        Generate a detailed prompt for analyzing these surveillance frames for shoplifting detection.
        The frames are in temporal sequence and show a retail environment.

        The prompt should guide the model to:
        1. Analyze each person's behavior and movements
        2. Look for suspicious interactions with merchandise
        3. Identify potential concealment attempts
        4. Note any unusual patterns or behaviors
        5. Consider the context of the retail environment

        Please provide a comprehensive prompt that will result in detailed analysis.
        The generated prompt should follow the 'chain of thought' method to break down complex tasks into smaller, more manageable steps.
        """

        # Create messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            self.logger.info("Generating prompt for CV analysis...")
            response = self.client.complete(
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            prompt = response.choices[0].message.content
            self.logger.info("Prompt generated successfully")
            return prompt
        except Exception as e:
            self.logger.error(f"Error generating prompt: {str(e)}")
            # Return a default prompt if generation fails
            return """
            Analyze these surveillance frames for potential shoplifting activity. Focus on:
            1. Each person's behavior and movements
            2. Interactions with merchandise
            3. Potential concealment attempts
            4. Unusual patterns or behaviors
            5. Context of the retail environment

            Provide detailed observations about any suspicious activities or behaviors.
            """


class CVModel:
    def __init__(self, logger: Optional[logging.Logger] = None, system_prompt: str = None):
        """
        Initialize the CVModel for analyzing video frames.

        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('CVModel', 'shoplifting_analysis.log')
        else:
            self.logger = logger

        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Check if credentials are set
        if not self.api_key or not self.endpoint:
            self.logger.error("Azure OpenAI credentials not found")
            raise ValueError(
                "Azure OpenAI credentials not found. Please set the following environment variables:\n"
                "  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key\n"
                "  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL\n"
                "  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name"
            )

        # Create the endpoint URL
        if self.deployment_name and "deployments" not in self.endpoint:
            self.endpoint = f"{self.endpoint}/openai/deployments/{self.deployment_name}"

        self.logger.info("Initializing Azure OpenAI client for CVModel")
        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
        self.logger.info("Azure OpenAI client initialized successfully")

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """
                You are a security analyst reviewing surveillance frames to determine whether shoplifting is occurring.
                Focus on suspicious behaviors like:
                1. Concealing items in clothing, bags, or containers
                2. Removing security tags
                3. Avoiding checkout areas
                4. Displaying nervous behavior
                5. Working with accomplices to distract staff

                Strictly follow this output format using the exact section headers and structure:

                ### Summary of Video:
                - Summarize behaviors using consistent bullet points.
                - This section will be extracted as "summary_of_video" in a JSON.

                ### Shoplifting Determination: Yes / No
                ### Confidence Level: XX%
                ### Key Behaviors Supporting Conclusion:
                - Bullet 1
                - Bullet 2
                - Bullet 3

                Make sure:
                - You always include all 4 parts of the conclusion section.
                - Each part is labeled exactly as shown.
                - Confidence Level must be numeric, in this format: "XX%"
                """

    def analyze_frames(self, frames_paths: List[str], prompt: str, max_frames: int = 8) -> str:
        """
        Analyze frames using the provided prompt.

        Args:
            frames_paths: List of paths to frames to analyze
            prompt: The prompt to use for analysis
            max_frames: Maximum number of frames to include

        Returns:
            str: Analysis result
        """
        # Sort frames by name which should preserve temporal order
        frames_paths = sorted(frames_paths)

        # Take a representative sample if we have too many frames
        if len(frames_paths) > max_frames:
            # Get evenly spaced frames across the sequence
            step = len(frames_paths) // max_frames
            frames_paths = frames_paths[::step][:max_frames]

        self.logger.info(f"Analyzing {len(frames_paths)} frames...")

        # Create the user message content
        user_content = [
            {"type": "text",
             "text": prompt}
        ]

        # Add all frames to the user message content
        for frame_path in frames_paths:
            encoded_image = encode_image_to_base64(frame_path)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })

        # Create the messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Get the analysis from the model
        try:
            self.logger.info("Sending request to Azure OpenAI...")
            response = self.client.complete(
                messages=messages,
                max_tokens=4000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting analysis: {str(e)}")
            return f"Error: {str(e)}"


class ShopliftingAnalyzer:
    def __init__(self, logger=None):
        self.prompt_model = PromptModel()
        self.cv_model = CVModel()
        self.cached_prompt = None

    def get_prompt(self):
        if self.cached_prompt is None:
            self.cached_prompt = self.prompt_model.generate_prompt()
        return self.cached_prompt

    def analyze_single_video(self, video_name: str, input_base_folder: str, max_frames: int = 8) -> Dict[str, str]:
        video_folder = os.path.join(input_base_folder, video_name)
        frame_paths = sorted(glob(os.path.join(video_folder, "*.jpg")))

        if not frame_paths:
            return {}

        prompt = self.get_prompt()
        analysis_text = self.cv_model.analyze_frames(frame_paths, prompt, max_frames)

        structured_result = restructure_analysis(analysis_text)
        structured_result.update({
            "sequence_name": video_name,
            "frame_count": len(frame_paths),
            "analyzed_frame_count": min(len(frame_paths), max_frames)
        })

        return structured_result

    def analyze_all_videos(self, input_base_folder: str, max_frames: int = 8) -> List[Dict[str, str]]:
        all_video_names = [
            d for d in os.listdir(input_base_folder)
            if os.path.isdir(os.path.join(input_base_folder, d))
        ]

        all_results = []

        for video_name in tqdm(all_video_names, desc="Analyzing all videos"):
            result = self.analyze_single_video(video_name, input_base_folder, max_frames)
            if result:
                all_results.append(result)

        return all_results
