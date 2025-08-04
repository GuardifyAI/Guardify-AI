import argparse
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from data_science.src.google.GoogleClient import GoogleClient
from backend.video.video_recorder import VideoRecorder
from backend.video.video_uploader import VideoUploader

load_dotenv()


def parse_arguments():
    """
    Parse command line arguments for camera configuration.
    
    Returns:
        argparse.Namespace: Parsed command line arguments containing:
            - camera: Name of the camera to record from
            - duration: Duration of each recording session in seconds
    """
    parser = argparse.ArgumentParser(
        description="Video recording system that captures camera streams and uploads to Google Cloud Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --camera "Back storage 2" --duration 30
        """
    )
    
    parser.add_argument(
        "--camera", "-c",
        type=str,
        required=True,
        help="Name of the camera to record from (must match camera name in Provision ISR interface)"
    )
    
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=30,
        help="Duration of each recording session in seconds (default: 30)"
    )
    
    return parser.parse_args()


def main():
    """
    Main function that orchestrates the video recording and upload process.
    
    This function:
    1. Parses command line arguments
    2. Initializes Google Cloud client and video components
    3. Sets up the browser and authentication
    4. Coordinates the recording and upload processes
    5. Handles graceful shutdown and cleanup
    
    The function uses a modular approach where VideoRecorder handles the recording
    process and VideoUploader manages concurrent upload operations in the background.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    print("=" * 60)
    print("VIDEO RECORDING SYSTEM")
    print("=" * 60)
    print(f"Camera: {args.camera}")
    print(f"Duration per recording: {args.duration} seconds")
    print(f"Upload bucket: {os.getenv('BUCKET_NAME', 'Not configured')}")
    print("=" * 60)
    print()

    # Initialize Google Cloud client
    try:
        google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )
        print("Google Cloud client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Google Cloud client: {e}")
        return 1

    # Initialize video components
    video_uploader = VideoUploader(google_client)
    video_recorder = VideoRecorder(video_uploader)
    print("Video components initialized successfully")

    # Start the upload worker
    video_uploader.start()
    print("Upload worker thread started")
    print()

    try:
        # Initialize Playwright and start recording
        with sync_playwright() as p:
            print("Starting browser and authentication...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Authenticate to Provision ISR
            video_recorder.login_to_provisionisr(page)
            print("Successfully authenticated to Provision ISR")
            print()

            # Start recording process
            print(f"Starting continuous recording from camera: {args.camera}")
            print("Press Ctrl+C to stop recording...")
            print("-" * 60)
            
            video_recorder.record_camera_stream(
                page, 
                camera_name=args.camera, 
                duration_in_sec=args.duration
            )

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("SHUTDOWN INITIATED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return 1
        
    finally:
        # Cleanup and shutdown
        print("Stopping upload worker and waiting for pending uploads...")
        video_uploader.stop()
        
        pending_uploads = video_uploader.get_queue_size()
        if pending_uploads > 0:
            print(f"Completed {pending_uploads} pending uploads")
        
        print("Upload worker stopped successfully")
        print("All components shut down gracefully")
        print("=" * 60)
        print("SHUTDOWN COMPLETE")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
