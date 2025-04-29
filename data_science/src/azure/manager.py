import os
import pandas as pd
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

DATASET_LOCAL_DIR = "dataset_local"
FRAMES_LOCAL_DIR = "extracted_frames_local"


def download_videos(blob_helper: AzureBlobHelper):
    """
    Download videos from Azure Blob Storage to local dataset directory.
    """
    os.makedirs(DATASET_LOCAL_DIR, exist_ok=True)
    print(f"Downloading videos from Azure Storage: {DATASET_CONTAINER}...")

    video_blobs = blob_helper.list_blobs(DATASET_CONTAINER)

    for blob_name in tqdm(video_blobs, desc="Downloading videos"):
        filename = os.path.basename(blob_name)
        local_path = os.path.join(DATASET_LOCAL_DIR, filename)

        if not os.path.exists(local_path):
            blob_helper.download_blob_as_file(DATASET_CONTAINER, blob_name, local_path)
        else:
            print(f"Already downloaded: {filename}")


def extract_frames():
    """
    Extract frames from local dataset videos.
    """
    os.makedirs(FRAMES_LOCAL_DIR, exist_ok=True)
    print("Extracting frames from downloaded videos...")

    extractor = FrameExtractor(every_n_frames=8)

    video_files = [
        os.path.join(DATASET_LOCAL_DIR, f)
        for f in os.listdir(DATASET_LOCAL_DIR)
        if extractor.is_valid_video_file(f)
    ]

    for video_file in tqdm(video_files, desc="Extracting frames"):
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        output_folder = os.path.join(FRAMES_LOCAL_DIR, video_name)

        if not os.path.exists(output_folder) or not os.listdir(output_folder):
            extractor.extract_frames(video_file, output_folder)
        else:
            print(f"Frames already extracted for: {video_name}")


def upload_frames(blob_helper: AzureBlobHelper):
    """
    Upload extracted frames to Azure Blob Storage if they don't already exist (per video basis).
    """
    print(f"Uploading extracted frames to Azure Storage: {FRAMES_CONTAINER}...")

    for video_name in tqdm(os.listdir(FRAMES_LOCAL_DIR), desc="Checking videos"):
        video_folder = os.path.join(FRAMES_LOCAL_DIR, video_name)

        if os.path.isdir(video_folder):
            # Check if frames already exist for this video
            if blob_helper.does_video_frames_exist(FRAMES_CONTAINER, video_name):
                print(f"Frames already uploaded for video '{video_name}', skipping upload.")
                continue

            # Upload all frames inside this video folder
            for frame_filename in os.listdir(video_folder):
                local_frame_path = os.path.join(video_folder, frame_filename)
                blob_path = f"{video_name}/{frame_filename}"

                blob_helper.upload_file_as_blob(FRAMES_CONTAINER, local_frame_path, blob_path)


def analyze_frames(analyzer: ShopliftingAnalyzer, blob_helper: AzureBlobHelper):
    """
    Analyze extracted frames and upload results immediately.
    """
    print(f"Analyzing frames and uploading results to Azure Blob {os.getenv('AZURE_STORAGE_CONTAINER_OUTPUT_NAME')}...")

    results = analyzer.analyze_all_videos(FRAMES_LOCAL_DIR, blob_helper, RESULTS_CONTAINER)
    return results


def main():
    """
    Full pipeline manager: download ➔ extract ➔ upload frames ➔ analyze (with immediate result upload)
    """
    blob_helper = AzureBlobHelper(AZURE_STORAGE_CONNECTION_STRING)
    analyzer = ShopliftingAnalyzer()

    # Step 1: Download videos
    download_videos(blob_helper)

    # Step 2: Extract frames
    extract_frames()

    # Step 3: Upload frames
    upload_frames(blob_helper)

    # Step 4: Analyze frames and upload results immediately
    analysis_results = analyze_frames(analyzer, blob_helper)

    # Optional: create a summary DataFrame
    df = pd.DataFrame(analysis_results)
    print("\nSample Analysis Results:")
    print(df.head())


if __name__ == "__main__":
    main()
