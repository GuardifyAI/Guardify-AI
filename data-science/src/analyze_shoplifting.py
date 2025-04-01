import os
import json
import base64
import argparse
from glob import glob
from tqdm import tqdm
from typing import List, Dict, Any
from config import AzureConfig
import openai


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


def analyze_frames(client, deployment_name, frames_paths: List[str], max_frames=8):
    """
    Analyze a set of frames for shoplifting detection using GPT-4o
    
    Args:
        client: The OpenAI client
        deployment_name: The Azure deployment name for GPT-4o
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

    # Create the system prompt
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

    # Create the messages list
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "text",
             "text": "Analyze these surveillance video frames for shoplifting activity. These frames are in temporal sequence."}
        ]}
    ]

    # Add all frames to the user message content
    for frame_path in frames_paths:
        encoded_image = encode_image_to_base64(frame_path)
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
            }
        })

    # Get the analysis from the model
    try:
        print(f"Sending request to deployment '{deployment_name}'...")
        response = client.chat.completions.create(
            model=deployment_name,  # This is the deployment name in Azure OpenAI
            messages=messages,
            max_tokens=4000,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting analysis: {str(e)}")
        return f"Error: {str(e)}"


def analyze_shoplifting_directory(frames_dir, output_dir, azure_config):
    """
    Analyze all frame sets in a directory for shoplifting
    
    Args:
        frames_dir: Directory containing extracted frame sets
        output_dir: Directory to save analysis results
        azure_config: Azure configuration object
    """
    # Print configuration for debugging
    print("Using Azure OpenAI configuration:")
    print(
        f"  API Key: {'*' * (len(azure_config.api_key) - 4) + azure_config.api_key[-4:] if azure_config.api_key else 'None'}")
    print(f"  API Base: {azure_config.api_base}")
    print(f"  API Version: {azure_config.api_version}")
    print(f"  Deployment Name: {azure_config.deployment_name}")

    # Initialize the Azure OpenAI client
    client = openai.AzureOpenAI(
        api_key=azure_config.api_key,
        api_version=azure_config.api_version,
        azure_endpoint=azure_config.api_base
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
        analysis = analyze_frames(client, azure_config.deployment_name, frames)

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


def main():
    parser = argparse.ArgumentParser(description="Analyze extracted frames for shoplifting detection")
    parser.add_argument("--frames", required=True, help="Directory containing extracted frames")
    parser.add_argument("--output", required=True, help="Output directory for analysis results")
    args = parser.parse_args()

    # Load Azure configuration
    azure_config = AzureConfig()

    # Verify Azure configuration
    if not azure_config.validate():
        print("ERROR: Invalid Azure OpenAI configuration. Please check your .env file.")
        print(
            "Required variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME")
        return

    # Analyze the frames
    analyze_shoplifting_directory(args.frames, args.output, azure_config)


if __name__ == "__main__":
    main()
