import cv2
import os
import argparse
from tqdm import tqdm
import concurrent.futures
import tempfile
from azure.storage.blob import BlobServiceClient, ContainerClient
from typing import List, Tuple
import io
import numpy as np
from dotenv import load_dotenv


def extract_frames_to_blob(video_path: str, container_client: ContainerClient, video_name: str, fps=4) -> int:
    """
    Extract frames from video and upload directly to blob storage
    
    Args:
        video_path: Path to the video file
        container_client: Azure container client for upload
        video_name: Name of the video (used for blob naming)
        fps: Frames per second to extract
        
    Returns:
        Number of frames extracted and uploaded
    """
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return 0

    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)

    count = 0
    frame_count = 0
    success = True
    
    while success:
        success, frame = video.read()
        if not success:
            break
            
        if count % frame_interval == 0:
            # Convert frame to jpg format in memory
            is_success, buffer = cv2.imencode(".jpg", frame)
            if not is_success:
                print(f"Error encoding frame {frame_count} from {video_path}")
                continue
                
            # Convert to bytes and upload directly to blob storage
            io_buf = io.BytesIO(buffer)
            blob_name = f"{video_name}/frame_{frame_count:04d}.jpg"
            
            container_client.upload_blob(
                name=blob_name,
                data=io_buf,
                overwrite=True
            )
            
            frame_count += 1
        count += 1

    video.release()
    return frame_count


def ensure_container_exists(blob_service_client: BlobServiceClient, container_name: str):
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


def process_blob_videos(connection_string: str, source_container: str, output_container: str, fps: int = 4):
    """
    Process videos from Azure Blob Storage and upload frames directly to output container
    
    Args:
        connection_string: Azure Storage connection string
        source_container: Name of the source blob container
        output_container: Name of the output blob container
        fps: Frames per second to extract
    """
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    source_container_client = blob_service_client.get_container_client(source_container)
    
    # Ensure output container exists
    output_container_client = ensure_container_exists(blob_service_client, output_container)
    
    # Create temporary directory for video downloads
    temp_dir = tempfile.mkdtemp()
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    
    # Get list of videos in the container
    video_blobs = []
    for blob in source_container_client.list_blobs():
        if blob.name.lower().endswith(video_extensions):
            local_path = os.path.join(temp_dir, os.path.basename(blob.name))
            video_blobs.append((blob.name, local_path))
    
    print(f"Found {len(video_blobs)} video files in blob storage...")
    
    video_files = []
    temp_files = []
    
    # Download videos and prepare processing list
    for blob_name, local_path in video_blobs:
        try:
            print(f"Downloading {blob_name}...")
            blob_client = source_container_client.get_blob_client(blob_name)
            
            with open(local_path, "wb") as video_file:
                video_file.write(blob_client.download_blob().readall())
                
            temp_files.append(local_path)
            video_name = os.path.splitext(blob_name)[0]
            video_files.append((local_path, video_name))
        except Exception as e:
            print(f"Error downloading {blob_name}: {e}")
    
    print(f"Processing {len(video_files)} video files...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_video = {
            executor.submit(extract_frames_to_blob, video_path, output_container_client, video_name, fps): (video_path, video_name)
            for video_path, video_name in video_files
        }
        
        total_frames = 0
        for future in tqdm(concurrent.futures.as_completed(future_to_video), total=len(video_files)):
            video_path, video_name = future_to_video[future]
            try:
                frames = future.result()
                total_frames += frames
                print(f"Extracted and uploaded {frames} frames from {os.path.basename(video_path)}")
            except Exception as e:
                print(f"Error processing {video_path}: {e}")
    
    # Cleanup temporary files
    print("Cleaning up temporary files...")
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Error removing temporary file {temp_file}: {e}")
    
    try:
        os.rmdir(temp_dir)  # Remove temp directory
    except Exception as e:
        print(f"Error removing temporary directory: {e}")
    
    print(f"Processing complete. Total frames extracted and uploaded: {total_frames}")
    print(f"All frames have been uploaded to the '{output_container}' container")


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get settings from environment variables
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    source_container = os.getenv('AZURE_STORAGE_CONTAINER_DATASET_NAME')
    output_container = os.getenv('AZURE_STORAGE_CONTAINER_FRAMES_NAME')
    fps = int(os.getenv('FRAMES_PER_SECOND', '4'))
    
    # Validate required environment variables
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in .env file")
    if not source_container:
        raise ValueError("AZURE_STORAGE_CONTAINER_DATASET_NAME not found in .env file")
    if not output_container:
        raise ValueError("AZURE_OUTPUT_CONTAINER not found in .env file")
    
    print(f"Processing videos from '{source_container}' to '{output_container}' at {fps} FPS")
    process_blob_videos(connection_string, source_container, output_container, fps)


if __name__ == "__main__":
    main()