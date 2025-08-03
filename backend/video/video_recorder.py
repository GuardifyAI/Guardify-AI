from playwright.sync_api import Page, sync_playwright
from data_science.src.google.google_client import GoogleClient
import os
import threading
import time
import queue
import argparse
from dotenv import load_dotenv

from data_science.src.utils import create_logger

load_dotenv()


class VideoRecorder:
    """
    A video recording system that captures camera streams and uploads them to Google Cloud Storage.
    """

    def __init__(self, google_client: GoogleClient):
        """
        Initialize the VideoRecorder with Google Cloud client and threading components.
        
        Args:
            google_client (GoogleClient): An instance of GoogleClient for handling
                                        uploads to Google Cloud Storage buckets.
        """
        self.logger = create_logger("video_recorder", "video_recorder.log")
        self.google_client = google_client

        # A thread-safe queue for passing upload tasks between threads
        self.upload_queue = queue.Queue()

        # An event to signal when the upload thread should stop
        self.stop_upload_thread = threading.Event()

        # Reference to the upload worker thread
        self.upload_thread = None

    def login_to_provisionisr(self, page: Page) -> None:
        """
        Authenticate to the Provision ISR cloud platform using credentials from environment variables.
        
        This function navigates to the Provision ISR login page and automatically fills in
        the required authentication fields (QR code, username, password) before submitting
        the login form. After successful login, it waits for the live video interface to load.
        
        Args:
            page (Page): Playwright Page object representing the browser page to use for login.
        
        Raises:
            TimeoutError: If login form elements are not found within the timeout period.
            Any Playwright exceptions: If navigation or form interaction fails.
        
        Environment Variables Required:
            - PROVISION_QR_CODE: The QR code number for authentication
            - PROVISION_USERNAME: Username for the Provision ISR account  
            - PROVISION_PASSWORD: Password for the Provision ISR account
        """
        self.logger.info("Navigating to provision ISR login page")
        page.goto("https://www.provisionisr-cloud.com/index.html")

        # Wait for login form to be ready
        page.get_by_role("textbox", name="QR code number").wait_for(timeout=10000)

        self.logger.info("Entering login details")
        page.get_by_role("textbox", name="QR code number").fill(os.getenv("PROVISION_QR_CODE"))
        page.get_by_role("textbox", name="Enter Your Username").fill(os.getenv("PROVISION_USERNAME"))
        page.get_by_role("textbox", name="Enter Your Password").fill(os.getenv("PROVISION_PASSWORD"))
        page.get_by_role("button", name="Login").click()

        page.locator("#divLiveOCX").wait_for()

    def _upload_worker(self) -> None:
        """
        Background worker thread that processes upload tasks from the upload queue.
        
        This function runs continuously in a separate thread, monitoring the upload_queue
        for new upload tasks. When a task is found, it attempts to upload the recording
        to the specified Google Cloud Storage bucket. The worker handles errors gracefully
        and continues processing until the stop_upload_thread event is set.
        
        The worker uses a timeout-based approach to periodically check if it should stop,
        allowing for clean shutdown even when no uploads are pending.
        
        Queue Task Format:
            Each task in the queue should be a tuple: (bucket_name, camera_name)
        
        Behavior:
            - Processes upload tasks sequentially from the queue
            - Logs upload progress and results
            - Handles upload failures without crashing
            - Stops gracefully when stop_upload_thread event is set
            - Uses 1-second timeout to allow responsive shutdown
        """
        self.logger.info("Upload thread started")
        
        while not self.stop_upload_thread.is_set():
            try:
                # Wait for upload task with timeout to allow checking stop event
                bucket_name, camera_name = self.upload_queue.get(timeout=1)
                
                self.logger.info(f"Starting upload for camera {camera_name} to bucket {bucket_name}")
                self.google_client.export_camera_recording_to_bucket(bucket_name, camera_name)
                self.logger.info(f"Upload succeeded for camera {camera_name}")
                
                self.upload_queue.task_done()
                
            except queue.Empty:
                # Timeout occurred, check if we should stop
                continue
            except Exception as e:
                self.logger.error(f"Upload failed: {e}")
                self.upload_queue.task_done()
        
        self.logger.info("Upload thread stopped")

    def record_camera_stream(self, page: Page, camera_name: str, duration_in_sec: int) -> None:
        """
        Start continuous recording from a specified camera with concurrent upload processing.
        
        This function performs continuous video recording in an infinite loop, where each
        recording session lasts for the specified duration. It uses a multi-threaded approach
        where recording and uploading happen concurrently:
        - Main thread: Handles the recording process (start/stop recording)
        - Background thread: Processes upload tasks from the queue
        
        The function first navigates to the specified camera stream, then starts the upload
        worker thread, and begins the recording loop. Each recording is immediately queued
        for upload while the next recording begins, maximizing throughput.
        
        Args:
            page (Page): Playwright Page object with active session to the Provision ISR platform.
                        Must be logged in and ready to access camera streams.
            camera_name (str): Name of the camera to record from. This should match the camera
                             name as it appears in the Provision ISR interface.
            duration_in_sec (int): Duration of each recording session in seconds.
        
        Behavior:
            - Navigates to the specified camera by double-clicking its name
            - Starts a background upload worker thread
            - Begins infinite recording loop:
                * Starts recording (clicks "Client Record On")
                * Waits for specified duration
                * Stops recording (clicks "Client Record Off") 
                * Queues upload task for background processing
                * Immediately starts next recording
            - Handles KeyboardInterrupt for graceful shutdown
            - Ensures proper cleanup of background threads on exit
        
        Environment Variables Required:
            - BUCKET_NAME: Google Cloud Storage bucket name for uploading recordings
        
        Raises:
            KeyboardInterrupt: Can be used to stop the infinite recording loop
            Any Playwright exceptions: If camera navigation or recording controls fail
        
        Note:
            This function runs indefinitely until interrupted. The background upload thread
            will continue processing any queued uploads even after recording stops.
        """
        self.logger.info(f"Navigating to the camera stream of {camera_name}")
        for i in range(2):
            page.get_by_text(camera_name).dblclick()
            time.sleep(2)

        # Start the upload worker thread
        self.stop_upload_thread.clear()
        self.upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()

        try:
            while True:
                self.logger.info("Started recording")
                time.sleep(1)
                page.get_by_title("Client Record On").click()

                self.logger.info(f"Recording for {duration_in_sec} seconds...")
                time.sleep(duration_in_sec)

                page.get_by_title("Client Record Off").click()
                self.logger.info("Recording finished")

                # Queue the upload task instead of doing it synchronously
                bucket_name = os.getenv("BUCKET_NAME")
                self.logger.info(f"Queuing upload task for camera {camera_name} to bucket {bucket_name}")
                self.upload_queue.put((bucket_name, camera_name))
                
        except KeyboardInterrupt:
            self.logger.info("Recording interrupted by user")
        finally:
            self._cleanup_threads()

    def _cleanup_threads(self) -> None:
        """
        Perform graceful cleanup of background threads when recording stops.
        
        This function ensures proper shutdown of the upload worker thread by:
        1. Signaling the upload thread to stop processing new tasks
        2. Waiting for all pending upload tasks in the queue to complete
        3. Waiting for the upload thread to finish with a timeout
        4. Logging warnings if the thread doesn't stop gracefully
        
        The cleanup process is designed to ensure no uploads are lost during shutdown
        while also preventing the application from hanging indefinitely.
        
        Note:
            This function should be called in a finally block or similar context
            to ensure proper cleanup even if exceptions occur during recording.
        """
        self.logger.info("Cleaning up threads...")
        
        # Signal the upload thread to stop
        self.stop_upload_thread.set()
        
        # Wait for any pending uploads to complete
        self.logger.info("Waiting for pending uploads to complete...")
        self.upload_queue.join()
        
        # Wait for the upload thread to finish
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join(timeout=5)
            if self.upload_thread.is_alive():
                self.logger.warning("Upload thread did not stop gracefully")
        
        self.logger.info("Thread cleanup completed")


def parse_arguments():
    """
    Parse command line arguments for camera configuration.
    
    Returns:
        argparse.Namespace: Parsed command line arguments containing:
            - camera_name: Name of the camera to record from
            - duration: Duration of each recording session in seconds
    """
    parser = argparse.ArgumentParser(
        description="Video recording system that captures camera streams and uploads to Google Cloud Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python video_recorder.py --camera "Back storage 2" --duration 30
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
    Main function that handles the video recording process with configurable parameters.
    
    This function parses command line arguments, initializes the browser and Google Client,
    performs authentication, and starts the video recording process.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    print(f"Starting video recording with the following configuration:")
    print(f"  Camera: {args.camera}")
    print(f"  Duration per recording: {args.duration} seconds")
    print()

    # Initialize Playwright and start recording
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )

        video_recorder = VideoRecorder(google_client)
        video_recorder.login_to_provisionisr(page)
        video_recorder.record_camera_stream(page, camera_name=args.camera, duration_in_sec=args.duration)

        browser.close()


if __name__ == "__main__":
    main()
