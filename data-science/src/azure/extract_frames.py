import cv2
import os
import argparse
from tqdm import tqdm
import concurrent.futures


def extract_frames(video_path, output_dir, fps=4):
    """
    Extract frames from a video at the specified frames per second rate
    
    Args:
        video_path: Path to the input video file
        output_dir: Directory to save extracted frames
        fps: Frames per second to extract (default: 4)
    
    Returns:
        int: Number of frames extracted
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the video
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return 0

    # Get video properties
    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)

    # Get filename without extension for frame naming
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Initialize counters
    count = 0
    frame_count = 0

    # Read and extract frames
    success = True
    while success:
        success, frame = video.read()
        if not success:
            break

        if count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"{video_name}_frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

        count += 1

    # Release the video
    video.release()
    return frame_count


def process_directory(input_dir, output_dir):
    """
    Process all MP4 files in a directory and its subdirectories
    
    Args:
        input_dir: Directory containing MP4 files
        output_dir: Base directory to save extracted frames
    """
    # Create base output directory
    os.makedirs(output_dir, exist_ok=True)

    # Find all MP4 files
    video_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.mp4'):
                video_path = os.path.join(root, file)

                # Determine the relative path structure
                rel_path = os.path.relpath(root, input_dir)

                # Create corresponding output directory
                if rel_path == '.':
                    # File is in the root input directory
                    this_output_dir = os.path.join(output_dir, os.path.splitext(file)[0])
                else:
                    # File is in a subdirectory
                    # Use the subdirectory name and the file name to create a unique output directory
                    sequence_name = os.path.basename(rel_path)
                    file_name = os.path.splitext(file)[0]
                    this_output_dir = os.path.join(output_dir, f"{sequence_name}_{file_name}")

                video_files.append((video_path, this_output_dir))

    # Process videos with a progress bar
    print(f"Processing {len(video_files)} video files...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all extraction tasks
        future_to_video = {}
        for video_path, this_output_dir in video_files:
            future = executor.submit(extract_frames, video_path, this_output_dir)
            future_to_video[future] = (video_path, this_output_dir)

        # Process results with progress bar
        total_frames = 0
        for future in tqdm(concurrent.futures.as_completed(future_to_video), total=len(video_files)):
            video_path, this_output_dir = future_to_video[future]
            try:
                frames = future.result()
                total_frames += frames
                print(f"Extracted {frames} frames from {os.path.basename(video_path)} to {this_output_dir}")
            except Exception as e:
                print(f"Error processing {video_path}: {e}")

    print(f"Extraction complete. Total frames extracted: {total_frames}")


def main():
    parser = argparse.ArgumentParser(description="Extract frames from videos at a specified rate")
    parser.add_argument("--input", required=True, help="Input directory containing MP4 files")
    parser.add_argument("--output", required=True, help="Output directory for extracted frames")
    parser.add_argument("--fps", type=int, default=4, help="Frames per second to extract (default: 4)")
    args = parser.parse_args()

    process_directory(args.input, args.output)


if __name__ == "__main__":
    main()
