import subprocess
import os
import signal
import time
import sys
from typing import Dict
import threading
from pathlib import Path
from datetime import datetime

from utils.logger_utils import create_logger


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

    def _get_process_key(self, shop_id: str, camera_name: str) -> str:
        """Generate a unique key for tracking processes."""
        return f"{shop_id}_{camera_name.lower().replace(' ', '_')}"

    def _is_process_running(self, process: subprocess.Popen) -> bool:
        """Check if a process is still running."""
        return process.poll() is None

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

                # Format timestamp for command line
                timestamp_str = start_timestamp.isoformat()

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
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=str(project_root),  # Set working directory to project root
                    env=env  # Pass modified environment
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
                raise ValueError(f"No active agentic analysis found for camera '{camera_name}' in shop '{shop_id}'")

            process_info = self.active_processes[process_key]
            process = process_info['process']

            try:
                self.logger.info(f"Stopping agentic analysis for camera '{camera_name}' in shop '{shop_id}' (PID: {process.pid})")

                # Try graceful shutdown first
                if self._is_process_running(process):
                    if os.name == 'nt':  # Windows
                        process.send_signal(signal.CTRL_C_EVENT)
                    else:  # Unix/Linux
                        process.send_signal(signal.SIGTERM)

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        self.logger.info(f"Agentic process stopped gracefully for camera '{camera_name}'")
                    except subprocess.TimeoutExpired:
                        # Force kill if graceful shutdown failed
                        self.logger.warning(f"Graceful shutdown timeout, force killing agentic process for camera '{camera_name}'")
                        process.kill()
                        process.wait()
                        self.logger.info(f"Agentic process force killed for camera '{camera_name}'")

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
