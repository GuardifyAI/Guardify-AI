import os
import json
import base64
import argparse
from glob import glob
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()


def encode_image_to_base64(image_path):
    """
    Encode an image file to base64
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Base64 encoded image string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_frames(client, frames_paths: List[str], max_frames=8):
    """
    Analyze a set of frames for shoplifting detection
    
    Args:
        client: The Azure OpenAI ChatCompletionsClient
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
    As a security analyst, evaluate these surveillance video frames for potential shoplifting activity.
    Focus on suspicious behaviors like:
    1. Concealing items in clothing, bags, or containers
    2. Removing security tags
    3. Avoiding checkout areas
    4. Displaying nervous behavior
    5. Working with accomplices to distract staff
    
    Provide a detailed analysis with a conclusion stating:
    1. Whether shoplifting is occurring (definitive answer)
    2. Your confidence level (0-100%)
    3. Key behaviors that support your conclusion
    
    Structure your analysis as follows:
    1. Frame-by-frame observations
    2. Patterns of behavior
    3. Conclusion with shoplifting determination and confidence level
    """

    # Create the user message content
    user_content = [
        {"type": "text",
         "text": "Analyze these surveillance video frames for shoplifting activity. These frames are in temporal sequence."}
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
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    # Get the analysis from the model
    try:
        print("Sending request to Azure OpenAI...")
        response = client.complete(
            messages=messages,
            max_tokens=4000,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting analysis: {str(e)}")
        return f"Error: {str(e)}"


def analyze_shoplifting_directory(frames_dir, output_dir):
    """
    Analyze all frame sets in a directory for shoplifting
    
    Args:
        frames_dir: Directory containing extracted frame sets
        output_dir: Directory to save analysis results
    """
    # Get Azure OpenAI credentials from environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # Check if credentials are set
    if not api_key or not endpoint:
        print("Error: Azure OpenAI credentials not found. Please set the following environment variables:")
        print("  AZURE_OPENAI_API_KEY - Your Azure OpenAI API key")
        print("  AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL")
        print("  AZURE_OPENAI_DEPLOYMENT_NAME - Your Azure OpenAI deployment name")
        return

    # Print credentials for debugging (with masked API key)
    print("Using Azure OpenAI configuration:")
    print(f"  API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'Not set'}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Deployment Name: {deployment_name}")

    # Create the endpoint URL
    if deployment_name:
        # When the deployment name is provided in .env
        if "deployments" not in endpoint:
            endpoint = f"{endpoint}/openai/deployments/{deployment_name}"

    print(f"  Full Endpoint URL: {endpoint}")

    try:
        # Initialize the ChatCompletionsClient
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )

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
            analysis = analyze_frames(client, frames)

            # Save the analysis
            output_file = os.path.join(output_dir, f"{sequence_name}_analysis.json")
            with open(output_file, 'w') as f:
                json.dump({
                    "sequence_name": sequence_name,
                    "frame_count": len(frames),
                    "analyzed_frame_count": min(len(frames), 8),  # Assuming max_frames=8
                    "analysis": analysis
                }, f, indent=2)

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

    # Analyze the frames
    analyze_shoplifting_directory(args.frames, args.output)


if __name__ == "__main__":
    main()
