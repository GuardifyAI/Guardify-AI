import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any
from google.cloud import storage
from google.oauth2.service_account import Credentials

from backend.app.request_bodies.recording_request_body import StartRecordingRequestBody, StopRecordingRequestBody
from backend.video.main import EXIT_CAMERA_NOT_FOUND, EXIT_GENERAL_ERROR, get_exit_code_description
from utils.logger_utils import create_logger


class RecordingService:
    """
    Service to manage video recording processes for cameras in shops.

    This service handles starting and stopping video recording processes
    by managing subprocess calls to the main.py video recording script.
    """

    def __init__(self, shops_service, agentic_service=None):
        """Initialize the recording service with process tracking."""
        # Dictionary to track running processes: {shop_id_camera_name: process_info}
        self.active_processes: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._dependencies_checked = False
        self.shops_service = shops_service
        self.agentic_service = agentic_service
        self.logger = create_logger("RecordingService", "recording_service.log")

        # Initialize Google Cloud Storage client for querying uploaded videos
        try:
            service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
            if service_account_file:
                credentials = Credentials.from_service_account_file(service_account_file)
                project_id = os.getenv("GOOGLE_PROJECT_ID")
                self.storage_client = storage.Client(project=project_id, credentials=credentials)
            else:
                # Fall back to default credentials
                self.storage_client = storage.Client()
        except Exception as e:
            self.logger.warning(f"Failed to initialize Google Cloud Storage client: {e}")
            self.storage_client = None

    def _check_request_params(self,
                              request_body: StartRecordingRequestBody | StopRecordingRequestBody) -> ValueError | None:
        """Check if request body is valid."""
        if not request_body.camera_name:
            raise ValueError("camera_name is required")

    def _get_process_key(self, shop_id: str, camera_name: str) -> str:
        """Generate a unique key for tracking processes."""
        return f"{shop_id}_{camera_name.lower().replace(' ', '_')}"

    def _check_environment_variables(self) -> None:
        """
        Check if all required environment variables are set for video recording.

        Raises:
            Exception: If required environment variables are missing
        """
        required_env_vars = [
            'BUCKET_NAME',
            'GOOGLE_PROJECT_ID',
            'GOOGLE_PROJECT_LOCATION',
            'SERVICE_ACCOUNT_FILE',
            'PROVISION_QR_CODE',
            'PROVISION_USERNAME',
            'PROVISION_PASSWORD'
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables for video recording: {', '.join(missing_vars)}. Please configure these in your .env file or environment.")

    def start_recording(self, shop_id: str, req_body: StartRecordingRequestBody) -> Dict[str, Any]:
        """
        Start video recording for a specific camera in a shop (non-blocking).

        Args:
            shop_id (str): The shop ID
            req_body (StartRecordingRequestBody): The start recording request body

        Returns:
            Dict[str, Any]: Immediate response containing:
                - recording_started: bool
                - shop_id: str
                - camera_id: str
                - camera_name: str

        Raises:
            ValueError: If recording is already active for this camera
            Exception: If failed to start the recording process
        """
        self._check_request_params(req_body)

        # Check required environment variables
        self._check_environment_variables()

        # Verify shop exists using shops service
        self.shops_service.verify_shop_exists(shop_id)

        camera_name = req_body.camera_name
        duration = req_body.duration
        detection_threshold = req_body.detection_threshold
        iterations = req_body.analysis_iterations

        process_key = self._get_process_key(shop_id, camera_name)

        # Get camera_id for this camera name in this shop
        cameras = self.shops_service.get_shop_cameras(shop_id)
        camera_id = None
        for camera in cameras:
            if camera.camera_name == camera_name:
                camera_id = camera.camera_id
                break

        if not camera_id:
            self.logger.warning(f"Could not find camera_id for camera '{camera_name}' in shop '{shop_id}'")
            camera_id = camera_name  # Fallback to camera name

        with self.lock:
            # Check if recording is already active for this camera
            if process_key in self.active_processes:
                active_process = self.active_processes[process_key]
                if self._is_process_running(active_process['process']):
                    raise ValueError(f"Recording already active for camera '{camera_name}' in shop '{shop_id}'")
                else:
                    # Clean up dead process
                    del self.active_processes[process_key]

            try:
                # Build command to run main.py using module syntax from project root
                video_dir = Path(__file__).resolve().parent.parent / 'video'
                main_py_path = video_dir / 'main.py'
                project_root = Path(__file__).resolve().parent.parent.parent  # Go up to project root

                # Build command to run main.py using module syntax from project root
                project_root = Path(__file__).resolve().parent.parent.parent

                cmd = [
                    sys.executable,  # Use the same Python executable as the current process
                    str(main_py_path),  # Convert Path to string for subprocess
                    '--camera', camera_name,
                    '--duration', str(duration),
                    '--shop-id', shop_id,
                    '--detection-threshold', str(detection_threshold),
                    '--analysis-iterations', str(iterations)
                ]

                # Set up environment with correct Python path
                env = os.environ.copy()
                current_pythonpath = env.get('PYTHONPATH', '')
                if current_pythonpath:
                    env['PYTHONPATH'] = f"{project_root}{os.pathsep}{current_pythonpath}"
                else:
                    env['PYTHONPATH'] = str(project_root)

                # Start the process with output forwarding
                process = subprocess.Popen(
                    cmd,
                    cwd=str(video_dir),  # Convert Path to string for subprocess
                    env=env,  # Use modified environment with correct PYTHONPATH
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Combine stderr with stdout
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
                    start_new_session=True if os.name != 'nt' else False
                )

                # Start a thread to forward output to console
                def forward_output():
                    in_error_block = False
                    try:
                        for line in iter(process.stdout.readline, ''):
                            if line:
                                line_content = line.rstrip()

                                # Detect start of Node.js error block
                                if any(start_pattern in line_content for start_pattern in [
                                    "node:events:", "throw er;", "Error: EPIPE", "broken pipe"
                                ]):
                                    in_error_block = True
                                    continue

                                # Skip all lines while in error block
                                if in_error_block:
                                    # Check if error block is ending (Node.js version line typically ends it)
                                    if "Node.js v" in line_content or (
                                            line_content.strip() == "" and "}" in line_content):
                                        in_error_block = False
                                    continue

                                # Also skip standalone error patterns
                                if any(error_pattern in line_content for error_pattern in [
                                    "at Socket._write", "at writeOrBuffer", "at _write",
                                    "at Writable.write", "PipeTransport.send",
                                    "dispatcherConnection.onmessage", "DispatcherConnection.sendEvent",
                                    "WebSocketDispatcher._dispatchEvent", "WebSocket.<anonymous>",
                                    "Emitted 'error' event", "at emitErrorNT", "at emitErrorCloseNT",
                                    "at processTicksAndRejections", "at runNextTicks", "at process.processImmediate",
                                    "errno: -4047", "syscall: 'write'", "code: 'EPIPE'",
                                    "    ^", "} {"
                                ]):
                                    continue

                                # Skip lines that are just stack trace formatting
                                if line_content.strip() in ["^", "", "}", "} {"] or line_content.startswith("    at "):
                                    continue

                                # Extract just the message part from the log line
                                # Format: "YYYY-MM-DD HH:MM:SS,mmm - logger_name - LEVEL - message"
                                parts = line_content.split(" - ")
                                if len(parts) >= 4:
                                    # Take only the message part (everything after the 3rd " - ")
                                    message = " - ".join(parts[3:])
                                    self.logger.info(f"[RECORDING:{camera_name}] {message}")
                                else:
                                    # If format doesn't match expected pattern, log the whole line
                                    self.logger.info(f"[RECORDING:{camera_name}] {line_content}")

                    except Exception as e:
                        # Only log non-pipe related errors
                        if "EPIPE" not in str(e) and "broken pipe" not in str(e):
                            self.logger.error(f"[RECORDING:{camera_name}] Output forwarding error: {e}")
                    finally:
                        if process.stdout:
                            try:
                                process.stdout.close()
                            except:
                                pass  # Ignore close errors

                output_thread = threading.Thread(target=forward_output, daemon=True)
                output_thread.start()

                # Store process information
                self.active_processes[process_key] = {
                    'process': process,
                    'shop_id': shop_id,
                    'camera_name': camera_name,
                    'duration': duration,
                    'started_at': time.time(),
                    'cmd': cmd
                }

                # Poll the process periodically to catch errors early
                self.logger.info(f"Validating camera '{camera_name}' in Provision ISR...")

                # Check process status every 2 seconds for up to 30 seconds
                max_wait_time = 30
                check_interval = 2

                for elapsed_time in range(0, max_wait_time, check_interval):
                    time.sleep(check_interval)

                    if not self._is_process_running(process):
                        # Process died, wait a bit for output thread to process any final output
                        time.sleep(1)
                        exit_code = process.returncode
                        del self.active_processes[process_key]

                        # Log the exit code for debugging
                        description = get_exit_code_description(exit_code)
                        self.logger.error(f"Recording process exited with code {exit_code}: {description}")

                        # Check the specific error based on exit code
                        if exit_code == EXIT_CAMERA_NOT_FOUND:
                            raise Exception(
                                f"Camera '{camera_name}' not found in Provision ISR interface. Please check the camera name and ensure it exists.")
                        elif exit_code == EXIT_GENERAL_ERROR:
                            raise Exception(
                                f"Recording process failed due to a general error. Check console output above for details.")
                        else:
                            # Unknown exit code - provide both the code and description
                            description = get_exit_code_description(exit_code)
                            raise Exception(
                                f"Recording process failed with exit code {exit_code} ({description}). Check console output above for details.")

                    # Update progress
                    if elapsed_time == 10:
                        self.logger.info("Still validating... (authentication in progress)")
                    elif elapsed_time == 20:
                        self.logger.info("Still validating... (searching for camera)")

                # If we get here, the process is still running after validation period
                self.logger.info(
                    f"Recording process started successfully for camera '{camera_name}' in shop '{shop_id}' (PID: {process.pid})")
                self.logger.info("Camera validation passed - recording is now active")

                # Return immediately - don't wait for recording to complete
                return {
                    "recording_started": True,
                    "shop_id": shop_id,
                    "camera_id": camera_id,
                    "camera_name": camera_name,
                }

            except Exception as e:
                if process_key in self.active_processes:
                    del self.active_processes[process_key]
                raise Exception(f"Failed to start recording: {str(e)}")

    def stop_recording(self, shop_id: str, req_body: StopRecordingRequestBody) -> None:
        """
        Stop video recording for a specific camera in a shop.
        
        Args:
            shop_id (str): The shop ID
            req_body (StopRecordingRequestBody): Stop recording request body
            
        Raises:
            ValueError: If no active recording found for this camera
            Exception: If failed to stop the recording process
        """
        self._check_request_params(req_body)

        # Verify shop exists using shops service
        self.shops_service.verify_shop_exists(shop_id)

        camera_name = req_body.camera_name

        process_key = self._get_process_key(shop_id, camera_name)

        with self.lock:
            if process_key not in self.active_processes:
                raise ValueError(f"No active recording found for camera '{camera_name}' in shop '{shop_id}'")

            process_info = self.active_processes[process_key]
            process = process_info['process']

            try:
                if self._is_process_running(process):
                    self.logger.info(f"Stopping recording process for camera '{camera_name}' (PID: {process.pid})")

                    # For Playwright processes, use a gentler approach
                    if os.name == 'nt':  # Windows
                        try:
                            # First try graceful termination
                            self.logger.info(f"Sending graceful termination signal to process {process.pid}")
                            process.terminate()

                            # Give extra time for Playwright to clean up (20 seconds)
                            self.logger.info("Waiting for Playwright cleanup...")
                            process.wait(timeout=20)
                            self.logger.info(f"Process {process.pid} stopped gracefully")

                        except subprocess.TimeoutExpired:
                            self.logger.warning(
                                f"Process {process.pid} didn't stop gracefully after 20s, force killing...")
                            try:
                                process.kill()
                                process.wait(timeout=5)
                                self.logger.info(f"Process {process.pid} force killed")
                            except:
                                self.logger.info(f"Force kill completed for process {process.pid}")
                        except Exception as e:
                            self.logger.warning(f"Terminate failed: {e}, trying force kill")
                            try:
                                process.kill()
                                process.wait()
                            except:
                                pass
                    else:  # Unix/Linux
                        try:
                            process.send_signal(signal.SIGINT)
                            process.wait(timeout=20)
                            self.logger.info(f"Process {process.pid} stopped gracefully")
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                            self.logger.info(f"Process {process.pid} force killed")

                    # Give a moment for any remaining cleanup
                    time.sleep(1)


                # Clean up
                del self.active_processes[process_key]

                self.logger.info(f"Recording stopped successfully for camera '{camera_name}'")

            except Exception as e:
                # Clean up even if stopping failed
                if process_key in self.active_processes:
                    del self.active_processes[process_key]
                raise Exception(f"Failed to stop recording: {str(e)}")

    def _is_process_running(self, process: subprocess.Popen) -> bool:
        """
        Check if a process is still running.
        
        Args:
            process (subprocess.Popen): The process to check
            
        Returns:
            bool: True if process is running, False otherwise
        """
        try:
            return process.poll() is None
        except:
            return False

    def get_active_recordings(self, shop_id: str) -> list[dict]:
        """
        Get all active recordings for a specific shop.

        Args:
            shop_id (str): The shop ID to get active recordings for

        Returns:
            list[dict]: List of active recording information
        """
        # Verify shop exists using shops service
        self.shops_service.verify_shop_exists(shop_id)

        # Clean up any dead processes first
        self.cleanup_dead_processes()

        active_recordings = []
        with self.lock:
            for key, process_info in self.active_processes.items():
                if process_info['shop_id'] == shop_id and self._is_process_running(process_info['process']):
                    active_recordings.append({
                        'camera_name': process_info['camera_name'],
                        'started_at': process_info['started_at'],
                        'duration': process_info['duration']
                    })

        return active_recordings

    def cleanup_dead_processes(self) -> None:
        """
        Clean up any dead processes from the tracking dictionary.
        This method can be called periodically to maintain clean state.
        """
        with self.lock:
            dead_keys = []
            for key, process_info in self.active_processes.items():
                if not self._is_process_running(process_info['process']):
                    dead_keys.append(key)

            for key in dead_keys:
                del self.active_processes[key]
