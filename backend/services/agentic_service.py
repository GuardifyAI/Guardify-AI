import subprocess
import os
import signal
import time
import sys
from typing import Dict, Any
import threading
from pathlib import Path
from datetime import datetime

from utils.logger_utils import create_logger
from data_science.src.model.pipeline.shoplifting_analyzer import create_agentic_analyzer
from google_client.google_client import GoogleClient
from backend.app.dtos.analysis_result_dto import AnalysisResultDTO


class AgenticService:
    """
    Service to manage agentic model processes for cameras in shops.

    This service handles starting and stopping agentic model processes
    that monitor and analyze videos from specific cameras starting from
    a given timestamp.
    """

    def __init__(self, shops_service):
        """Initialize the agentic service with process tracking."""
        # Dictionary to track running processes: {shop_id_camera_name: process_info}
        self.active_processes: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self.shops_service = shops_service
        self.logger = create_logger("AgenticService", "agentic_service.log")
        
        # Initialize Google client for single video analysis
        self.google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )

    def _get_process_key(self, shop_id: str, camera_name: str) -> str:
        """Generate a unique key for tracking processes."""
        return f"{shop_id}_{camera_name.lower().replace(' ', '_')}"

    def _is_process_running(self, process: subprocess.Popen) -> bool:
        """Check if a process is still running."""
        return process.poll() is None

    def analyze_single_video(self, video_url: str) -> AnalysisResultDTO:
        """
        Analyze a single video using the agentic strategy (synchronous).

        Args:
            video_url (str): Google Cloud Storage URI of the video to analyze

        Returns:
            AnalysisResultDTO: Analysis result containing:
                - video_url: str
                - final_confidence: float  
                - final_detection: str
                - decision_reasoning: str
                - iteration_results: List[Any]

        Raises:
            Exception: If analysis fails or video is invalid
        """
        try:
            self.logger.info(f"Starting single video analysis for: {video_url}")
            
            # Create agentic analyzer
            shoplifting_analyzer = create_agentic_analyzer(
                detection_threshold=0.45,  # Default threshold
                logger=self.logger
            )
            
            # Analyze the video
            analysis_result = shoplifting_analyzer.analyze_video_from_bucket(
                video_url,
                iterations=3,  # Default iterations
                pickle_analysis=False  # Don't save pickle for API calls
            )
            
            # Extract required fields from analysis result
            result = AnalysisResultDTO(
                video_url=video_url,
                final_confidence=analysis_result.get("final_confidence", 0.0),
                final_detection=str(analysis_result.get("final_detection", False)),
                decision_reasoning=analysis_result.get("decision_reasoning", "No reasoning provided"),
                iteration_results=analysis_result.get("iteration_results", [])  # Include iteration data
            )
            
            self.logger.info(f"Single video analysis completed for: {video_url}")
            self.logger.info(f"Result: detected={result.final_detection}, confidence={result.final_confidence:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze video {video_url}: {str(e)}")
            raise Exception(f"Video analysis failed: {str(e)}")

    def start_agentic_analysis(self, shop_id: str, camera_name: str, start_timestamp: datetime) -> None:
        """
        Start agentic model analysis for a specific camera in a shop.

        Args:
            shop_id (str): The shop ID
            camera_name (str): Name of the camera to analyze videos from
            start_timestamp (datetime): Timestamp to start monitoring from

        Raises:
            ValueError: If analysis is already active for this camera
            Exception: If failed to start the agentic process
        """
        # Verify shop exists using shops service
        self.shops_service.verify_shop_exists(shop_id)

        process_key = self._get_process_key(shop_id, camera_name)

        with self.lock:
            # Check if analysis is already active for this camera
            if process_key in self.active_processes:
                active_process = self.active_processes[process_key]
                if self._is_process_running(active_process['process']):
                    raise ValueError(f"Agentic analysis already active for camera '{camera_name}' in shop '{shop_id}'")
                else:
                    # Clean up dead process
                    del self.active_processes[process_key]

            try:
                # Build command to run agentic model
                data_science_dir = Path(__file__).resolve().parent.parent.parent / 'data_science' / 'src'
                main_py_path = data_science_dir / 'main.py'

                # Format timestamp for command line in simple format (2025-08-14 15:18:28)
                timestamp_str = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')

                # Set working directory to project root
                project_root = Path(__file__).resolve().parent.parent.parent

                cmd = [
                    sys.executable,  # Use the same Python executable as the current process
                    str(main_py_path),  # Convert Path to string for subprocess
                    '--strategy', 'agentic',
                    '--camera-name', camera_name,
                    '--start-timestamp', timestamp_str,
                    '--continuous-mode'
                ]

                self.logger.info(f"Starting agentic analysis for camera '{camera_name}' in shop '{shop_id}'")
                self.logger.info(f"Command: {' '.join(cmd)}")

                # Set up environment for subprocess
                env = os.environ.copy()
                # Add project root to PYTHONPATH
                pythonpath = env.get('PYTHONPATH', '')
                if pythonpath:
                    env['PYTHONPATH'] = f"{project_root}{os.pathsep}{pythonpath}"
                else:
                    env['PYTHONPATH'] = str(project_root)

                # Start the process with correct working directory and environment
                # Use process group to isolate subprocess and prevent signal propagation
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=str(project_root),  # Set working directory to project root
                    env=env,  # Pass modified environment
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
                    preexec_fn=None if os.name == 'nt' else os.setsid  # Create new session on Unix
                )

                # Set up output forwarding in a separate thread
                def forward_output():
                    """Forward subprocess output to our logger."""
                    try:
                        for line in iter(process.stdout.readline, ''):
                            if line.strip():
                                self.logger.info(f"[AGENTIC-{camera_name}] {line.strip()}")
                    except Exception as e:
                        self.logger.error(f"Error forwarding output: {e}")

                output_thread = threading.Thread(target=forward_output, daemon=True)
                output_thread.start()

                # Store process information
                self.active_processes[process_key] = {
                    'process': process,
                    'shop_id': shop_id,
                    'camera_name': camera_name,
                    'start_timestamp': start_timestamp,
                    'started_at': time.time(),
                    'cmd': cmd
                }

                # Brief validation that process started
                time.sleep(2)
                if not self._is_process_running(process):
                    if process_key in self.active_processes:
                        del self.active_processes[process_key]
                    raise Exception(f"Agentic process failed to start for camera '{camera_name}'")

                self.logger.info(
                    f"Agentic analysis started successfully for camera '{camera_name}' in shop '{shop_id}' (PID: {process.pid})")

            except Exception as e:
                if process_key in self.active_processes:
                    del self.active_processes[process_key]
                raise Exception(f"Failed to start agentic analysis: {str(e)}")

    def stop_agentic_analysis(self, shop_id: str, camera_name: str) -> None:
        """
        Stop agentic model analysis for a specific camera in a shop.
        
        Args:
            shop_id (str): The shop ID
            camera_name (str): Name of the camera to stop analysis for
            
        Raises:
            ValueError: If no active analysis found for this camera
            Exception: If failed to stop the agentic process
        """
        # Verify shop exists using shops service
        self.shops_service.verify_shop_exists(shop_id)

        process_key = self._get_process_key(shop_id, camera_name)

        with self.lock:
            if process_key not in self.active_processes:
                self.logger.warning(f"No active agentic analysis found for camera '{camera_name}' in shop '{shop_id}' - may have already stopped")
                return  # Don't raise error, just return silently

            process_info = self.active_processes[process_key]
            process = process_info['process']

            self.logger.info(f"Found active agentic process for camera '{camera_name}' (PID: {process.pid})")

            try:
                self.logger.info(f"Stopping agentic analysis for camera '{camera_name}' in shop '{shop_id}' (PID: {process.pid})")

                # Try graceful shutdown first
                if self._is_process_running(process):
                    self.logger.info(f"Process {process.pid} is running, attempting to terminate...")
                    try:
                        if os.name == 'nt':  # Windows
                            # Use terminate() instead of CTRL_C_EVENT to avoid signal propagation
                            self.logger.info(f"Sending terminate signal to Windows process {process.pid}")
                            process.terminate()
                        else:  # Unix/Linux
                            # Send SIGTERM to the process group to avoid affecting parent
                            self.logger.info(f"Sending SIGTERM to Unix process group {process.pid}")
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                        # Wait for graceful shutdown - reasonable timeout for responsive stopping
                        graceful_timeout = 15  # 15 seconds for graceful shutdown
                        self.logger.info(f"Waiting up to {graceful_timeout} seconds for agentic analysis to stop gracefully...")

                        try:
                            process.wait(timeout=graceful_timeout)
                            self.logger.info(f"Agentic process stopped gracefully for camera '{camera_name}'")
                        except subprocess.TimeoutExpired:
                            # Force kill if graceful shutdown failed
                            self.logger.warning(f"Graceful shutdown timeout after {graceful_timeout}s, force killing agentic process for camera '{camera_name}'")
                            if os.name == 'nt':
                                process.kill()
                            else:
                                # Kill the entire process group on Unix
                                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                            process.wait()
                            self.logger.info(f"Agentic process force killed for camera '{camera_name}'")
                    except ProcessLookupError:
                        # Process already terminated
                        self.logger.info(f"Agentic process for camera '{camera_name}' already terminated")
                    except Exception as e:
                        self.logger.error(f"Error stopping agentic process for camera '{camera_name}': {e}")
                        # Try basic kill as fallback
                        try:
                            process.kill()
                            process.wait()
                        except:
                            pass

                # Verify process is actually stopped
                if self._is_process_running(process):
                    self.logger.warning(f"Process {process.pid} is still running after stop attempt!")
                else:
                    self.logger.info(f"Process {process.pid} confirmed stopped")

                # Clean up process tracking
                del self.active_processes[process_key]
                self.logger.info(f"Agentic analysis stopped successfully for camera '{camera_name}' in shop '{shop_id}'")

            except Exception as e:
                # Still clean up the process tracking even if stopping failed
                if process_key in self.active_processes:
                    del self.active_processes[process_key]
                raise Exception(f"Failed to stop agentic analysis: {str(e)}")

    def get_active_analyses(self) -> Dict[str, Dict]:
        """
        Get information about all currently active agentic analyses.
        
        Returns:
            Dict[str, Dict]: Dictionary of active processes with their information
        """
        with self.lock:
            # Clean up any dead processes first
            dead_processes = []
            for process_key, process_info in self.active_processes.items():
                if not self._is_process_running(process_info['process']):
                    dead_processes.append(process_key)

            for process_key in dead_processes:
                self.logger.info(f"Cleaning up dead agentic process: {process_key}")
                del self.active_processes[process_key]

            # Return copy of active processes (without the actual process objects for safety)
            return {
                key: {
                    'shop_id': info['shop_id'],
                    'camera_name': info['camera_name'],
                    'start_timestamp': info['start_timestamp'],
                    'started_at': info['started_at'],
                    'pid': info['process'].pid,
                    'is_running': self._is_process_running(info['process'])
                }
                for key, info in self.active_processes.items()
            }

    def is_analysis_active(self, shop_id: str, camera_name: str) -> bool:
        """
        Check if agentic analysis is currently active for a specific camera.
        
        Args:
            shop_id (str): The shop ID
            camera_name (str): Name of the camera
            
        Returns:
            bool: True if analysis is active, False otherwise
        """
        process_key = self._get_process_key(shop_id, camera_name)
        
        with self.lock:
            if process_key not in self.active_processes:
                return False
            
            process_info = self.active_processes[process_key]
            if not self._is_process_running(process_info['process']):
                # Clean up dead process
                del self.active_processes[process_key]
                return False
            
            return True
