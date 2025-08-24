from playwright.sync_api import Page
import os
import sys
import time

from utils import load_env_variables
from utils.logger_utils import create_logger
from backend.celery_tasks.upload_task import UploadTask

load_env_variables()


class VideoRecorder:
    """
    A video recording system that captures camera streams from Provision ISR platform.
    """

    def __init__(self, video_uploader, shop_id: str, detection_threshold: float = 0.8, analysis_iterations: int = 1):
        """
        Initialize the VideoRecorder with video uploader integration.
        
        Args:
            video_uploader (VideoUploader): An instance of VideoUploader for handling
                                          concurrent upload processing.
            shop_id (str): Shop ID for context when triggering analysis callbacks.
                          This is required as it's essential for video analysis.
            detection_threshold (float): Detection confidence threshold for AI analysis (default: 0.8)
            analysis_iterations (int): Number of analysis iterations (default: 1)
                          
        Raises:
            ValueError: If shop_id is None or empty string
        """
        if not shop_id or not shop_id.strip():
            raise ValueError("shop_id is required and cannot be None or empty string")
            
        self.logger = create_logger("video_recorder", "video_recorder.log")
        self.video_uploader = video_uploader
        self.shop_id = shop_id
        self.detection_threshold = detection_threshold
        self.analysis_iterations = analysis_iterations

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
        
        # Try to find the camera with exact text match first
        try:
            camera_element = page.get_by_text(camera_name)
            camera_element.wait_for(timeout=5000)  # Wait up to 5 seconds
            self.logger.info(f"Found camera '{camera_name}' - attempting to navigate")
            
            for i in range(2):
                camera_element.dblclick()
                time.sleep(2)
                
        except Exception as e:
            # If exact match fails, try partial match
            self.logger.warning(f"Exact match for '{camera_name}' failed: {e}")
            self.logger.info("Attempting partial match search...")
            
            try:
                # Try case-insensitive partial match
                camera_element = page.get_by_text(camera_name, case_sensitive=False)
                camera_element.wait_for(timeout=5000)
                self.logger.info(f"Found camera with partial match - attempting to navigate")
                
                for i in range(2):
                    camera_element.dblclick()
                    time.sleep(2)
                    
            except Exception:
                # List available cameras for debugging
                self.logger.error(f"Could not find camera '{camera_name}'. Available text elements:")
                
                try:
                    all_text_elements = page.locator("text=/[A-Za-z0-9]/").all()
                    available_texts = []
                    
                    for element in all_text_elements[:20]:  # Limit to first 20
                        try:
                            text = element.text_content()
                            if text and 1 < len(text.strip()) < 30:
                                available_texts.append(text.strip())
                        except:
                            continue
                    
                    unique_texts = list(set(available_texts))
                    for text in sorted(unique_texts):
                        self.logger.error(f"  Available: '{text}'")
                        
                except Exception as list_error:
                    self.logger.error(f"Could not list available cameras: {list_error}")
                
                raise Exception(f"Camera '{camera_name}' not found in Provision ISR interface. Check camera name and try again.")

        # Ensure the upload worker is running
        if not self.video_uploader.is_running():
            self.video_uploader.start()

        try:
            while True:
                # Check for shutdown signal
                try:
                    # Check shutdown_requested from main module if it exists
                    main_module = sys.modules.get('__main__')
                    if main_module and hasattr(main_module, 'shutdown_requested') and main_module.shutdown_requested:
                        self.logger.info("Shutdown requested via signal - stopping recording loop")
                        break
                except:
                    pass  # Continue normally if we can't check shutdown flag
                
                self.logger.info("Started recording")
                time.sleep(1)
                page.get_by_title("Client Record On").click()

                self.logger.info(f"Recording for {duration_in_sec} seconds...")
                
                # Sleep in smaller chunks so we can respond to shutdown signals faster
                for i in range(duration_in_sec):
                    time.sleep(1)
                    # Check for shutdown during recording
                    try:
                        if main_module and hasattr(main_module, 'shutdown_requested') and main_module.shutdown_requested:
                            self.logger.info("Shutdown requested during recording - stopping current recording")
                            page.get_by_title("Client Record Off").click()
                            self.logger.info("Recording stopped due to shutdown request")
                            return
                    except:
                        pass

                page.get_by_title("Client Record Off").click()
                self.logger.info("Recording finished")

                # Queue the upload task for background processing
                bucket_name = os.getenv("BUCKET_NAME")
                upload_task = UploadTask(
                    bucket_name=bucket_name,
                    camera_name=camera_name,
                    shop_id=self.shop_id,
                    detection_threshold=self.detection_threshold,
                    analysis_iterations=self.analysis_iterations
                )
                self.video_uploader.add_to_queue(upload_task)
                
        except KeyboardInterrupt:
            self.logger.info("Recording interrupted by user")
