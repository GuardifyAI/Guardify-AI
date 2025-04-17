import os
import json
import base64
import argparse
import re
from glob import glob
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()


class ShopliftingAnalyzer:
    def __init__(self):
        """Initialize the ShopliftingAnalyzer with Azure OpenAI client."""
        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Check if credentials are set
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure OpenAI credentials not found. Please set the following environment variables:\n"
                "  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key\n"
                "  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL\n"
                "  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name"
            )

        # Create the endpoint URL
        if self.deployment_name and "deployments" not in self.endpoint:
            self.endpoint = f"{self.endpoint}/openai/deployments/{self.deployment_name}"

        # Initialize the ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )

    @staticmethod
    def restructure_analysis(analysis_text: str) -> dict:
        """
        Parse the detailed analysis and restructure it into a simplified JSON format.
        """
        # Extract summary from "### Summary of Video:"
        summary_match = re.search(
            r"### Summary of Video:\s*(.*?)(?=\n### Shoplifting Determination:)",
            analysis_text, re.DOTALL | re.IGNORECASE
        )
        summary = summary_match.group(1).strip() if summary_match else "N/A"

        # Extract conclusion from "### Shoplifting Determination:"
        conclusion_match = re.search(
            r"### Shoplifting Determination:\s*(Yes|No|Inconclusive)",
            analysis_text, re.IGNORECASE
        )
        conclusion = conclusion_match.group(1) if conclusion_match else "N/A"

        # Extract confidence level
        confidence_match = re.search(
            r"### Confidence Level:\s*(\d{1,3})%",
            analysis_text, re.IGNORECASE
        )
        confidence = f"{confidence_match.group(1)}%" if confidence_match else "N/A"

        # Extract key behaviors
        behaviors_match = re.search(
            r"### Key Behaviors Supporting Conclusion:\s*(.*)",
            analysis_text, re.DOTALL | re.IGNORECASE
        )
        key_behaviors = behaviors_match.group(1).strip() if behaviors_match else "N/A"

        return {
            "summary_of_video": summary,
            "conclusion": conclusion,
            "confidence_level": confidence,
            "key_behaviors": key_behaviors
        }

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

    def analyze_frames(self, frames_paths: List[str], max_frames: int = 8) -> str:
        """
        Analyze a set of frames for shoplifting detection
        
        Args:
            frames_paths: List of paths to frames to analyze
            max_frames: Maximum number of frames to include (to avoid token limits)
            
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

        print(f"Analyzing {len(frames_paths)} frames...")

        # Create system prompt
        system_prompt = """
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

        ### Shoplifting Determination: Yes / No / Inconclusive
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

        # Create the user message content
        user_content = [
            {"type": "text",
             "text": "Analyze these surveillance video frames for shoplifting activity. These frames are in temporal sequence."}
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
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Get the analysis from the model
        try:
            print("Sending request to Azure OpenAI...")
            response = self.client.complete(
                messages=messages,
                max_tokens=4000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting analysis: {str(e)}")
            return f"Error: {str(e)}"

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
                    print(f"No frames found in {frame_dir}, skipping.")
                    continue

                # Analyze the frames
                print(f"Analyzing sequence: {sequence_name} ({len(frames)} frames)")
                analysis = self.analyze_frames(frames)

                # Save the analysis
                output_file = os.path.join(output_dir, f"{sequence_name}_analysis.json")
                result = self.restructure_analysis(analysis)
                result.update({
                    "sequence_name": sequence_name,
                    "frame_count": len(frames),
                    "analyzed_frame_count": min(len(frames), 8)
                })

                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)

                print(f"Analysis saved to {output_file}")

        except Exception as e:
            print(f"Error: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Check if your API key is correct")
            print("2. Verify your endpoint URL format")
            print("3. Make sure your deployment name is correct")
            print("4. Check if your Azure region is correct")


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
