import os
import json
import base64
import argparse
import re
import logging
from glob import glob
from tqdm import tqdm
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from .utils import create_logger

# Load environment variables
load_dotenv()


class PromptModel:
    def __init__(self, logger: Optional[logging.Logger] = None):
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

    def generate_prompt(self, frames_paths: List[str]) -> str:
        """
        Generate a prompt for CV analysis based on the frames.
        
        Args:
            frames_paths: List of paths to frames to analyze
            
        Returns:
            str: Generated prompt for CV analysis
        """
        # Create system prompt for prompt generation
        system_prompt = """
        You are a prompt engineering expert specializing in computer vision tasks. Your task is to generate 
        detailed prompts that will help a vision model analyze surveillance footage for shoplifting detection.
        
        The prompt should:
        1. Focus on specific visual elements and behaviors
        2. Guide the model to look for key indicators of shoplifting
        3. Request detailed analysis of suspicious activities
        4. Ask for specific observations about people's actions and movements
        5. Request analysis of interactions with merchandise and store equipment
        
        The prompt should be clear, specific, and structured to get the most detailed analysis possible.
        """

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
        """

        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
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
    def __init__(self, logger: Optional[logging.Logger] = None):
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

    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """
        Encode an image file to base64
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

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
            {"type": "text", "text": prompt}
        ]

        # Add all frames to the user message content
        for frame_path in frames_paths:
            encoded_image = self.encode_image_to_base64(frame_path)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })

        # Create the messages
        messages = [
            {"role": "system", "content": ""},  # TODO: Add system prompt
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


class AnalysisModel:
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the AnalysisModel for generating final conclusions.
        
        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('AnalysisModel', 'shoplifting_analysis.log')
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

        self.logger.info("Initializing Azure OpenAI client for AnalysisModel")
        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
        self.logger.info("Azure OpenAI client initialized successfully")

    def generate_analysis(self, cv_analysis: str) -> Dict[str, Any]:
        """
        Generate final analysis and conclusion based on CV analysis.
        
        Args:
            cv_analysis: The analysis from CVModel
            
        Returns:
            Dict[str, Any]: Structured analysis result
        """
        # TODO: Implement analysis generation logic
        return {}


class ShopliftingAnalyzer:
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the ShopliftingAnalyzer with all three models.
        
        Args:
            logger: Optional logger instance. If None, a default logger will be created.
        """
        # Setup logging
        if logger is None:
            self.logger = create_logger('ShopliftingAnalyzer', 'shoplifting_analysis.log')
        else:
            self.logger = logger
        
        # Initialize all three models
        self.prompt_model = PromptModel(logger)
        self.cv_model = CVModel(logger)
        self.analysis_model = AnalysisModel(logger)

    def analyze_frames(self, frames_paths: List[str], max_frames: int = 8) -> Dict[str, Any]:
        """
        Analyze a set of frames for shoplifting detection using all three models.
        
        Args:
            frames_paths: List of paths to frames to analyze
            max_frames: Maximum number of frames to include
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        # Generate prompt
        prompt = self.prompt_model.generate_prompt(frames_paths)
        
        # Get CV analysis
        cv_analysis = self.cv_model.analyze_frames(frames_paths, prompt, max_frames)
        
        # Generate final analysis
        return self.analysis_model.generate_analysis(cv_analysis)

    def analyze_shoplifting_directory(self, frames_dir: str, output_dir: str) -> None:
        """
        Analyze all frame sets in a directory for shoplifting
        
        Args:
            frames_dir: Directory containing extracted frame sets
            output_dir: Directory to save analysis results
        """
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"Created output directory: {output_dir}")

            # Find all directories with frames
            frame_directories = [d for d in glob(os.path.join(frames_dir, "**"), recursive=True)
                               if os.path.isdir(d) and any(f.endswith('.jpg') for f in os.listdir(d))]

            # Process each directory
            for frame_dir in tqdm(frame_directories, desc="Analyzing frame sets"):
                # Get the sequence name
                sequence_name = os.path.basename(frame_dir)

                # Find all frames in this directory
                frames = glob(os.path.join(frame_dir, "*.jpg"))

                if not frames:
                    self.logger.warning(f"No frames found in {frame_dir}, skipping.")
                    continue

                # Analyze the frames
                self.logger.info(f"Analyzing sequence: {sequence_name} ({len(frames)} frames)")
                result = self.analyze_frames(frames)

                # Save the analysis
                output_file = os.path.join(output_dir, f"{sequence_name}_analysis.json")
                result.update({
                    "sequence_name": sequence_name,
                    "frame_count": len(frames),
                    "analyzed_frame_count": min(len(frames), 8)
                })

                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)

                self.logger.info(f"Analysis saved to {output_file}")

        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            self.logger.error("\nTroubleshooting tips:")
            self.logger.error("1. Check if your API key is correct")
            self.logger.error("2. Verify your endpoint URL format")
            self.logger.error("3. Make sure your deployment name is correct")
            self.logger.error("4. Check if your Azure region is correct")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze extracted frames for shoplifting detection using Azure ChatCompletionsClient")
    parser.add_argument("--frames", required=True, help="Directory containing extracted frames")
    parser.add_argument("--output", required=True, help="Output directory for analysis results")
    args = parser.parse_args()

    # Create analyzer instance and analyze the frames
    analyzer = ShopliftingAnalyzer()
    analyzer.analyze_shoplifting_directory(args.frames, args.output)


if __name__ == "__main__":
    main()
