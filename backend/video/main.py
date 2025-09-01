import argparse
import os
import signal
from playwright.sync_api import sync_playwright

from backend.video.video_recorder import VideoRecorder
from backend.video.video_uploader import VideoUploader
from google_client.google_client import GoogleClient
from utils import load_env_variables
from utils.logger_utils import create_logger

load_env_variables()

# Exit codes for video recording processes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_CAMERA_NOT_FOUND = 2

# Error code descriptions for logging
EXIT_CODE_DESCRIPTIONS = {
    EXIT_SUCCESS: "Recording completed successfully",
    EXIT_GENERAL_ERROR: "General error occurred",
    EXIT_CAMERA_NOT_FOUND: "Camera not found in Provision ISR interface"
}

# Initialize logger for the entire module
logger = create_logger("video_main", "video_main.log")

# Global flag for graceful shutdown
shutdown_requested = False

def get_exit_code_description(exit_code: int) -> str:
    """
    Get a readable description for an exit code.

    Args:
        exit_code (int): The exit code to describe

    Returns:
        str: Description of the exit code
    """
    return EXIT_CODE_DESCRIPTIONS.get(exit_code, f"Unknown exit code: {exit_code}")

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

# Register signal handlers
if os.name != 'nt':  # Unix/Linux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
else:  # Windows
    signal.signal(signal.SIGTERM, signal_handler)


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
    
    parser.add_argument(
        "--shop-id", "-s",
        type=str,
        default=None,
        help="Shop ID for context when triggering analysis callbacks"
    )
    
    parser.add_argument(
        "--detection-threshold",
        type=float,
        default=0.8,
        help="Detection confidence threshold for AI analysis (default: 0.8)"
    )
    
    parser.add_argument(
        "--analysis-iterations",
        type=int,
        default=1,
        help="Number of analysis iterations (default: 1)"
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
    
    logger.info("=" * 60)
    logger.info("VIDEO RECORDING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Camera: {args.camera}")
    logger.info(f"Duration per recording: {args.duration} seconds")
    logger.info(f"Upload bucket: {os.getenv('BUCKET_NAME', 'Not configured')}")
    logger.info("=" * 60)

    # Initialize Google Cloud client
    try:
        google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )
        logger.info("Google Cloud client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Cloud client: {e}")
        return EXIT_GENERAL_ERROR

    # Initialize video components
    video_uploader = VideoUploader(google_client)
    video_recorder = VideoRecorder(
        video_uploader, 
        shop_id=args.shop_id,
        detection_threshold=args.detection_threshold,
        analysis_iterations=args.analysis_iterations
    )
    logger.info("Video components initialized successfully")

    # Start the upload worker
    video_uploader.start()
    logger.info("Upload worker thread started")

    try:
        # Initialize Playwright and start recording
        with sync_playwright() as p:
            logger.info("Starting browser and authentication...")
            
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Authenticate to Provision ISR
            video_recorder.login_to_provisionisr(page)
            logger.info("Successfully authenticated to Provision ISR")

            # Start recording process
            logger.info(f"Starting continuous recording from camera: {args.camera}")
            logger.info("-" * 60)
            
            video_recorder.record_camera_stream(
                page, 
                camera_name=args.camera, 
                duration_in_sec=args.duration
            )

    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("SHUTDOWN INITIATED")
        logger.info("=" * 60)
    except SystemExit:
        logger.info("=" * 60)
        logger.info("SHUTDOWN INITIATED VIA SIGNAL")
        logger.info("=" * 60)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"An error occurred: {e}")
        
        # Return specific exit codes for different types of errors
        if "not found in Provision ISR interface" in error_msg:
            return EXIT_CAMERA_NOT_FOUND
        else:
            return EXIT_GENERAL_ERROR
        
    finally:
        # Cleanup and shutdown
        logger.info("Stopping upload worker and waiting for pending uploads...")
        video_uploader.stop()
        
        pending_uploads = video_uploader.get_queue_size()
        if pending_uploads > 0:
            logger.info(f"Completed {pending_uploads} pending uploads")
        
        logger.info("Upload worker stopped successfully")
        logger.info("All components shut down gracefully")
        logger.info("=" * 60)
        logger.info("SHUTDOWN COMPLETE")
        logger.info("=" * 60)

    return EXIT_SUCCESS


if __name__ == "__main__":
    exit(main())
