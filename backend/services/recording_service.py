import subprocess
import os
import signal
import time
import sys
from typing import Dict
import threading
from queue import Queue


class RecordingService:
    """
    Service to manage video recording processes for cameras in shops.
    
    This service handles starting and stopping video recording processes
    by managing subprocess calls to the main.py video recording script.
    """
    
    def __init__(self):
        """Initialize the recording service with process tracking."""
        # Dictionary to track running processes: {shop_id_camera_name: process_info}
        self.active_processes: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._dependencies_checked = False
    
    def _get_process_key(self, shop_id: str, camera_name: str) -> str:
        """Generate a unique key for tracking processes."""
        return f"{shop_id}_{camera_name.lower().replace(' ', '_')}"
    
    def _check_and_install_dependencies(self) -> None:
        """
        Check if required dependencies are installed and install them if missing.
        This method is called once per service instance to ensure dependencies are available.
        
        Raises:
            Exception: If dependency installation fails
        """
        if self._dependencies_checked:
            return
            
        try:
            # Check if playwright is installed
            import playwright
            print("Playwright already installed")
        except ImportError:
            print("Installing playwright...")
            try:
                # Install playwright
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 'playwright==1.54.0'
                ])
                print("Playwright installed successfully")
                
                # Install browser binaries
                print("Installing Chromium browser...")
                subprocess.check_call([
                    sys.executable, '-m', 'playwright', 'install', 'chromium'
                ])
                print("Chromium browser installed successfully")
                
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to install dependencies: {e}")
        
        # Always check and install critical dependencies
        critical_deps = [
            'python-dotenv>=1.0.0',
            'google-auth>=2.25.2'
        ]
        
        try:
            print("Ensuring critical dependencies are installed...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + critical_deps)
            print("Critical dependencies verified/installed")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install critical dependencies: {e}")
        
        self._dependencies_checked = True
        print("All video recording dependencies are available")
    
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
            raise Exception(f"Missing required environment variables for video recording: {', '.join(missing_vars)}. Please configure these in your .env file or environment.")
    
    def start_recording(self, shop_id: str, camera_name: str, duration: int = 30) -> None:
        """
        Start video recording for a specific camera in a shop.
        
        Args:
            shop_id (str): The shop ID
            camera_name (str): The camera name as it appears in Provision ISR
            duration (int): Recording duration in seconds (default: 30)
            
        Raises:
            ValueError: If recording is already active for this camera
            Exception: If failed to start the recording process
        """
        # Check and install dependencies if needed (only runs once)
        self._check_and_install_dependencies()
        
        # Check required environment variables
        self._check_environment_variables()
        
        process_key = self._get_process_key(shop_id, camera_name)
        
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
                # Build command to run main.py
                video_dir = os.path.join(os.path.dirname(__file__), '..', 'video')
                main_py_path = os.path.join(video_dir, 'main.py')
                
                cmd = [
                    sys.executable,  # Use the same Python executable as the current process
                    main_py_path,
                    '--camera', camera_name,
                    '--duration', str(duration)
                ]
                
                # Start the process with output forwarding
                process = subprocess.Popen(
                    cmd,
                    cwd=video_dir,
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
                                    if "Node.js v" in line_content or (line_content.strip() == "" and "}" in line_content):
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
                                
                                print(f"[RECORDING:{camera_name}] {line_content}")
                                
                    except Exception as e:
                        # Only log non-pipe related errors
                        if "EPIPE" not in str(e) and "broken pipe" not in str(e):
                            print(f"[RECORDING:{camera_name}] Output forwarding error: {e}")
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
                print(f"[RECORDING SERVICE] Validating camera '{camera_name}' in Provision ISR...")
                
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
                        
                        # Check if it's a camera not found error based on exit code
                        if exit_code == 2:
                            raise Exception(f"Camera '{camera_name}' not found in Provision ISR interface. Please check the camera name and ensure it exists.")
                        elif exit_code == 1:
                            raise Exception(f"Recording process failed due to a general error. Check console output above for details.")
                        else:
                            raise Exception(f"Recording process failed to start. Process exited with code {exit_code}. Check console output above for details.")
                    
                    # Update progress
                    if elapsed_time == 10:
                        print(f"[RECORDING SERVICE] Still validating... (authentication in progress)")
                    elif elapsed_time == 20:
                        print(f"[RECORDING SERVICE] Still validating... (searching for camera)")
                
                # If we get here, the process is still running after validation period
                print(f"[RECORDING SERVICE] Recording process started successfully for camera '{camera_name}' in shop '{shop_id}' (PID: {process.pid})")
                print(f"[RECORDING SERVICE] Camera validation passed - recording should be active now")
                
            except Exception as e:
                if process_key in self.active_processes:
                    del self.active_processes[process_key]
                raise Exception(f"Failed to start recording: {str(e)}")
    
    def stop_recording(self, shop_id: str, camera_name: str) -> None:
        """
        Stop video recording for a specific camera in a shop.
        
        Args:
            shop_id (str): The shop ID
            camera_name (str): The camera name
            
        Raises:
            ValueError: If no active recording found for this camera
            Exception: If failed to stop the recording process
        """
        process_key = self._get_process_key(shop_id, camera_name)
        
        with self.lock:
            if process_key not in self.active_processes:
                raise ValueError(f"No active recording found for camera '{camera_name}' in shop '{shop_id}'")
            
            process_info = self.active_processes[process_key]
            process = process_info['process']
            
            try:
                if self._is_process_running(process):
                    print(f"[RECORDING SERVICE] Stopping recording process for camera '{camera_name}' (PID: {process.pid})")
                    
                    # For Playwright processes, use a gentler approach
                    if os.name == 'nt':  # Windows
                        try:
                            # First try graceful termination
                            print(f"[RECORDING SERVICE] Sending graceful termination signal to process {process.pid}")
                            process.terminate()
                            
                            # Give extra time for Playwright to clean up (20 seconds)
                            print(f"[RECORDING SERVICE] Waiting for Playwright cleanup...")
                            process.wait(timeout=20)
                            print(f"[RECORDING SERVICE] Process {process.pid} stopped gracefully")
                            
                        except subprocess.TimeoutExpired:
                            print(f"[RECORDING SERVICE] Process {process.pid} didn't stop gracefully after 20s, force killing...")
                            try:
                                process.kill()
                                process.wait(timeout=5)
                                print(f"[RECORDING SERVICE] Process {process.pid} force killed")
                            except:
                                print(f"[RECORDING SERVICE] Force kill completed for process {process.pid}")
                        except Exception as e:
                            print(f"[RECORDING SERVICE] Terminate failed: {e}, trying force kill")
                            try:
                                process.kill()
                                process.wait()
                            except:
                                pass
                    else:  # Unix/Linux
                        try:
                            process.send_signal(signal.SIGINT)
                            process.wait(timeout=20)
                            print(f"[RECORDING SERVICE] Process {process.pid} stopped gracefully")
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                            print(f"[RECORDING SERVICE] Process {process.pid} force killed")
                            
                    # Give a moment for any remaining cleanup
                    time.sleep(1)
                
                # Clean up
                del self.active_processes[process_key]
                print(f"[RECORDING SERVICE] Recording stopped successfully for camera '{camera_name}'")
                
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
