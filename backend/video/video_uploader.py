import threading
import queue

from google_client import google_client
from data_science.src.utils import create_logger


class VideoUploader:
    """
    A video upload system that handles concurrent uploading of recorded videos to Google Cloud Storage.
    """

    def __init__(self, gc: google_client):
        """
        Initialize the VideoUploader with Google Cloud client and threading components.
        
        Args:
            gc (GoogleClient): An instance of GoogleClient for handling
                                        uploads to Google Cloud Storage buckets.
        """
        self.logger = create_logger("video_uploader", "video_uploader.log")
        self.google_client = gc

        # A thread-safe queue for passing upload tasks between threads
        self.upload_queue = queue.Queue()

        # An event to signal when the upload thread should stop
        self.stop_upload_thread = threading.Event()

        # Reference to the upload worker thread
        self.upload_thread = None

    def start(self) -> None:
        """
        Start the background upload worker thread.
        
        This method initializes and starts the upload worker thread that will
        continuously process upload tasks from the queue until stopped.
        
        Behavior:
            - Clears any previous stop signals
            - Creates a new daemon thread for upload processing
            - Starts the thread immediately
        
        Note:
            This method should be called before queuing any upload tasks.
            The thread runs as a daemon thread and will automatically terminate
            when the main program exits.
        """
        self.logger.info("Starting upload worker thread...")
        self.stop_upload_thread.clear()
        self.upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()
        self.logger.info("Upload worker thread started successfully")

    def stop(self) -> None:
        """
        Stop the upload worker thread and wait for all pending uploads to complete.
        
        This method performs graceful shutdown of the upload worker thread by:
        1. Signaling the upload thread to stop processing new tasks
        2. Waiting for all pending upload tasks in the queue to complete
        3. Waiting for the upload thread to finish with a timeout
        4. Logging warnings if the thread doesn't stop gracefully
        
        The cleanup process ensures no uploads are lost during shutdown while
        preventing the application from hanging indefinitely.
        
        Note:
            This method should be called when shutting down the application
            to ensure proper cleanup of resources and completion of pending uploads.
        """
        self.logger.info("Stopping upload worker thread...")
        
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
        
        self.logger.info("Upload worker thread stopped successfully")

    def add_to_queue(self, bucket_name: str, camera_name: str) -> None:
        """
        Add an upload task to the processing queue.
        
        This method queues a new upload task that will be processed by the background
        upload worker thread. The task will be processed in FIFO order along with
        other queued uploads.
        
        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket to upload to.
                             The bucket must already exist and be accessible.
            camera_name (str): Name/prefix of the camera used to identify the recording file.
                             Used to find the corresponding local video file.
        
        Behavior:
            - Adds task to thread-safe queue immediately
            - Does not block - returns immediately after queuing
            - Task will be processed by background thread in order
            - Logs the queuing action for monitoring
        
        Note:
            The upload worker thread must be started (via start()) before
            calling this method, otherwise tasks will queue but not be processed.
        """
        self.logger.info(f"Queuing upload task for camera {camera_name} to bucket {bucket_name}")
        self.upload_queue.put((bucket_name, camera_name))

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

    def get_queue_size(self) -> int:
        """
        Get the current number of pending upload tasks in the queue.
        
        Returns:
            int: Number of upload tasks currently waiting to be processed.
        """
        return self.upload_queue.qsize()

    def is_running(self) -> bool:
        """
        Check if the upload worker thread is currently running.
        
        Returns:
            bool: True if the upload thread is alive and running, False otherwise.
        """
        return self.upload_thread is not None and self.upload_thread.is_alive()
