import os
import json
import base64
import argparse
import re
from glob import glob
from tqdm import tqdm
from typing import List, Dict, Any
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
import concurrent.futures
import cv2
import numpy as np
from datetime import datetime

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


def download_and_analyze_frame(frame_blob: str, container_client: ContainerClient) -> Dict[str, Any]:
    """
    Download a frame from blob storage and analyze it for shoplifting behavior
    
    Args:
        frame_blob: Blob path of the frame
        container_client: Azure container client for downloading
        
    Returns:
        Dictionary containing analysis results
    """
    # Download frame
    blob_client = container_client.get_blob_client(frame_blob)
    frame_data = blob_client.download_blob().readall()
    
    # Convert to OpenCV format
    frame_array = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    
    # TODO: Add your actual shoplifting detection logic here
    # This is a placeholder that returns random results for demonstration
    # Convert numpy.bool_ to Python bool
    is_suspicious = bool(np.random.choice([True, False], p=[0.1, 0.9]))
    confidence = float(np.random.uniform(0.6, 0.99))
    
    results = {
        "frame": frame_blob,
        "timestamp": datetime.now().isoformat(),
        "suspicious_activity_detected": is_suspicious,
        "confidence_score": round(confidence, 2),
        "detected_objects": []
    }
    
    if results["suspicious_activity_detected"]:
        # Convert all numpy types to Python native types
        x = int(np.random.uniform(0, frame.shape[1]))
        y = int(np.random.uniform(0, frame.shape[0]))
        w = int(np.random.uniform(50, 200))
        h = int(np.random.uniform(100, 300))
        obj_confidence = float(np.random.uniform(0.7, 0.99))
        
        results["detected_objects"] = [
            {
                "type": "person",
                "bbox": [x, y, w, h],
                "confidence": round(obj_confidence, 2)
            }
        ]
    
    return results


def ensure_container_exists(blob_service_client: BlobServiceClient, container_name: str) -> ContainerClient:
    """
    Ensure that a container exists, create it if it doesn't
    """
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
    except Exception:
        container_client = blob_service_client.create_container(container_name)
        print(f"Created new container: {container_name}")
    return container_client


def analyze_frames(connection_string: str, frames_container: str, results_container: str):
    """
    Analyze frames from blob storage for shoplifting behavior
    
    Args:
        connection_string: Azure Storage connection string
        frames_container: Container name containing the extracted frames
        results_container: Container name for storing analysis results
    """
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    frames_container_client = blob_service_client.get_container_client(frames_container)
    
    # Ensure results container exists
    results_container_client = ensure_container_exists(blob_service_client, results_container)
    
    # Get list of all frames
    print("Listing frames from storage...")
    frame_blobs = []
    for blob in frames_container_client.list_blobs():
        if blob.name.lower().endswith('.jpg'):
            frame_blobs.append(blob.name)
    
    print(f"Found {len(frame_blobs)} frames to analyze...")
    
    # Process frames in parallel
    results_by_video = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_frame = {
            executor.submit(download_and_analyze_frame, frame_blob, frames_container_client): frame_blob
            for frame_blob in frame_blobs
        }
        
        for future in tqdm(concurrent.futures.as_completed(future_to_frame), total=len(frame_blobs)):
            frame_blob = future_to_frame[future]
            try:
                result = future.result()
                
                # Group results by video
                video_name = os.path.dirname(frame_blob)
                if video_name not in results_by_video:
                    results_by_video[video_name] = []
                results_by_video[video_name].append(result)
                
            except Exception as e:
                print(f"Error processing {frame_blob}: {e}")
    
    # Upload results for each video
    print("Uploading analysis results...")
    for video_name, results in results_by_video.items():
        # Sort results by frame number
        results.sort(key=lambda x: int(os.path.basename(x["frame"]).split("_")[1].split(".")[0]))
        
        # Prepare summary
        summary = {
            "video_name": video_name,
            "total_frames": len(results),
            "suspicious_frames": sum(1 for r in results if r["suspicious_activity_detected"]),
            "average_confidence": round(sum(r["confidence_score"] for r in results) / len(results), 2),
            "timestamp": datetime.now().isoformat(),
            "frame_results": results
        }
        
        # Upload results
        blob_name = f"{video_name}/analysis_results.json"
        results_container_client.upload_blob(
            name=blob_name,
            data=json.dumps(summary, indent=2),
            overwrite=True
        )
        print(f"Uploaded results for {video_name}")
    
    print(f"Analysis complete. Results uploaded to '{results_container}' container")


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get settings from environment variables
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    frames_container = os.getenv('AZURE_STORAGE_CONTAINER_FRAMES_NAME')
    results_container = os.getenv('AZURE_STORAGE_CONTAINER_OUTPUT_NAME')
    
    # Validate required environment variables
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in .env file")
    if not frames_container:
        raise ValueError("AZURE_STORAGE_CONTAINER_FRAMES_NAME not found in .env file")
    if not results_container:
        raise ValueError("AZURE_STORAGE_CONTAINER_OUTPUT_NAME not found in .env file")
    
    print(f"Processing frames from '{frames_container}' and storing results in '{results_container}'")
    analyze_frames(connection_string, frames_container, results_container)


if __name__ == "__main__":
    main()
