import cv2
import os
import argparse
from tqdm import tqdm
import concurrent.futures


def extract_frames(video_path, output_dir, fps=4):
    os.makedirs(output_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return 0

    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    count = 0
    frame_count = 0
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

    video.release()
    return frame_count


def process_directory(input_dir, output_dir):
    """
    Process all video files in a directory and its subdirectories

    Args:
        input_dir: Directory containing video files
        output_dir: Base directory to save extracted frames
    """

    def rename_non_ascii_videos(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.avi') and any(ord(char) > 127 for char in file):
                    base, ext = os.path.splitext(file)
                    parts = base.split('_', 1)
                    if len(parts) == 2:
                        # TODO: this is a hard coded name
                        # exit1 is translating of the original name
                        # it hard coded!! we need to think if we can want it dynamic
                        new_base = f"exit1_{parts[1]}"
                    else:
                        new_base = "exit1"
                    new_filename = new_base + ext
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, new_filename)
                    print(f"Renaming: {file} → {new_filename}")
                    os.rename(old_path, new_path)

    rename_non_ascii_videos(input_dir)

    os.makedirs(output_dir, exist_ok=True)
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = []

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_dir)
                sequence_name = os.path.basename(rel_path)
                file_name = os.path.splitext(file)[0]

                if rel_path == '.':
                    this_output_dir = os.path.join(output_dir, file_name)
                else:
                    this_output_dir = os.path.join(output_dir, f"{sequence_name}_{file_name}")

                video_files.append((video_path, this_output_dir))

    print(f"Processing {len(video_files)} video files...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_video = {
            executor.submit(extract_frames, video_path, this_output_dir): (video_path, this_output_dir)
            for video_path, this_output_dir in video_files
        }

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
    parser.add_argument("--input", required=True, help="Input directory containing video files")
    parser.add_argument("--output", required=True, help="Output directory for extracted frames")
    parser.add_argument("--fps", type=int, default=4, help="Frames per second to extract (default: 4)")
    args = parser.parse_args()

    process_directory(args.input, args.output)


if __name__ == "__main__":
    main()