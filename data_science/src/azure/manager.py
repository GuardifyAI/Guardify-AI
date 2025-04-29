import os
from tqdm import tqdm

from data_science.src.azure.azure_blob_helpers import AzureBlobHelper
from data_science.src.azure.extract_frames import FrameExtractor
from data_science.src.azure.analyze_shoplifting import ShopliftingAnalyzer
from data_science.src.azure.utils import load_env_variables

# Load environment variables
load_env_variables()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
DATASET_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER_DATASET_NAME")
FRAMES_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER_FRAMES_NAME")
RESULTS_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER_OUTPUT_NAME")


def process_videos(blob_helper: AzureBlobHelper):
    """
    Process videos directly from Azure Storage: extract frames and analyze.
    """
    print(f"Processing videos from Azure Storage: {DATASET_CONTAINER}...")

    # Initialize components
    extractor = FrameExtractor()
    analyzer = ShopliftingAnalyzer()

    # List all videos
    video_blobs = [b for b in blob_helper.list_blobs(DATASET_CONTAINER) 
                   if extractor.is_valid_video_file(b)]

    results = []
    for blob_name in tqdm(video_blobs, desc="Processing videos"):
        video_name = os.path.splitext(os.path.basename(blob_name))[0]

        # Skip if frames already exist
        if blob_helper.does_video_frames_exist(FRAMES_CONTAINER, video_name):
            print(f"Frames already exist for video '{video_name}', skipping extraction.")
            continue

        # Download video as bytes stream
        print(f"Extracting frames for video: {video_name}")
        video_stream = blob_helper.download_blob_as_bytes(DATASET_CONTAINER, blob_name)
        
        # Extract frames directly to Azure storage
        extractor.extract_frames_from_stream(video_stream, blob_helper, FRAMES_CONTAINER, video_name)

    # Analyze all videos
    print("\nAnalyzing videos...")
    all_videos = set(os.path.dirname(frame) for frame in blob_helper.list_blobs(FRAMES_CONTAINER))
    
    for video_name in sorted(all_videos):
        if not video_name:  # Skip empty video names
            continue
            
        print(f"\nAnalyzing video: {video_name}")
        result = analyzer.analyze_frames_from_azure(video_name, blob_helper, FRAMES_CONTAINER)
        
        if result:
            # Upload result
            blob_name = f"{video_name}_analysis.json"
            blob_helper.upload_json_object(RESULTS_CONTAINER, blob_name, result)
            
            # Print determination
            determination = result["shoplifting_determination"]
            confidence = result["confidence_level"]
            print(f"✓ {video_name}: {determination} (Confidence: {confidence})")
            
            results.append(result)
        else:
            print(f"✗ {video_name}: Analysis failed")
    
    print("\nAnalysis complete! Results have been uploaded to Azure Storage.")
    return results


def main():
    """
    Full pipeline manager: process videos directly from Azure Storage
    """
    blob_helper = AzureBlobHelper(AZURE_STORAGE_CONNECTION_STRING)
    
    # Ensure containers exist
    for container in [DATASET_CONTAINER, FRAMES_CONTAINER, RESULTS_CONTAINER]:
        blob_helper.ensure_container_exists(container)
    
    # Process videos and get results
    results = process_videos(blob_helper)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total videos analyzed: {len(results)}")
    for result in results:
        video_name = result["sequence_name"]
        determination = result["shoplifting_determination"]
        confidence = result["confidence_level"]
        print(f"- {video_name}: {determination} (Confidence: {confidence})")


if __name__ == "__main__":
    main()
