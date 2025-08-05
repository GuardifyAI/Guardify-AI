from playwright.sync_api import Page
import os
import time
from dotenv import load_dotenv

from data_science.src.utils import create_logger

load_dotenv()


class VideoRecorder:
    """
    A video recording system that captures camera streams from Provision ISR platform.
    """

    def __init__(self, video_uploader):
        """
        Initialize the VideoRecorder with video uploader integration.
        
        Args:
            video_uploader (VideoUploader): An instance of VideoUploader for handling
                                          concurrent upload processing.
        """
        self.logger = create_logger("video_recorder", "video_recorder.log")
        self.video_uploader = video_uploader

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

    def record_camera_stream(self, page: Page, camera_name: str, duration_in_sec: int) -> None:
        """
        Start continuous recording from a specified camera with concurrent upload processing.
        
        This function performs continuous video recording in an infinite loop, where each
        recording session lasts for the specified duration. It uses the VideoUploader
        for concurrent upload processing while the main thread handles recording.
        
        The function navigates to the specified camera stream and begins the recording loop.
        Each completed recording is immediately queued for upload via the VideoUploader
        while the next recording begins, maximizing throughput.
        
        Args:
            page (Page): Playwright Page object with active session to the Provision ISR platform.
                        Must be logged in and ready to access camera streams.
            camera_name (str): Name of the camera to record from. This should match the camera
                             name as it appears in the Provision ISR interface.
            duration_in_sec (int): Duration of each recording session in seconds.
        
        Behavior:
            - Navigates to the specified camera by double-clicking its name
            - Ensures the upload worker is running
            - Begins infinite recording loop:
                * Starts recording (clicks "Client Record On")
                * Waits for specified duration
                * Stops recording (clicks "Client Record Off") 
                * Queues upload task for background processing
                * Immediately starts next recording
            - Handles KeyboardInterrupt for graceful shutdown
        
        Environment Variables Required:
            - BUCKET_NAME: Google Cloud Storage bucket name for uploading recordings
        
        Raises:
            KeyboardInterrupt: Can be used to stop the infinite recording loop
            Any Playwright exceptions: If camera navigation or recording controls fail
        
        Note:
            This function runs indefinitely until interrupted. The VideoUploader
            will continue processing any queued uploads even after recording stops.
        """
        self.logger.info(f"Navigating to the camera stream of {camera_name}")
        for i in range(2):
            page.get_by_text(camera_name).dblclick()
            time.sleep(2)

        # Ensure the upload worker is running
        if not self.video_uploader.is_running():
            self.video_uploader.start()

        try:
            while True:
                self.logger.info("Started recording")
                time.sleep(1)
                page.get_by_title("Client Record On").click()

                self.logger.info(f"Recording for {duration_in_sec} seconds...")
                time.sleep(duration_in_sec)

                page.get_by_title("Client Record Off").click()
                self.logger.info("Recording finished")

                # Queue the upload task for background processing
                bucket_name = os.getenv("BUCKET_NAME")
                self.video_uploader.add_to_queue(bucket_name, camera_name)
                
        except KeyboardInterrupt:
            self.logger.info("Recording interrupted by user")
