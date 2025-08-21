import vertexai
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from typing import List, Tuple
from google.cloud import storage
import tempfile
import subprocess
import os
from datetime import datetime, timedelta
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = "ffmpeg"  # Fall back to system ffmpeg

class GoogleClient:
    def __init__(self, project: str, location: str, service_account_json_path: str):
        """
        Initialize the GoogleClient with project and location settings.
        
        Args:
            project: Google Cloud project ID
            location: Google Cloud location/region
            service_account_json_path: Path to the service account JSON file
        """
        self.project = project
        self.location = location
        self.service_account_json_path = service_account_json_path
        self.credentials = self._get_credentials()
        self._init_vertex_ai()
        self.storage_client = storage.Client(project=project, credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        """Get Google Cloud credentials from service account file."""
        credentials = Credentials.from_service_account_file(
            self.service_account_json_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform'])
        if credentials.expired:
            credentials.refresh(Request())
        return credentials

    def _init_vertex_ai(self):
        """Initialize Vertex AI with project settings."""
        vertexai.init(project=self.project, location=self.location, credentials=self.credentials)

    def get_videos_uris_and_names_from_buckets(self, bucket_name: str) -> Tuple[List[str], List[str]]:
        """
        Get URIs and names of all MP4 videos in a Google Cloud Storage bucket.
        
        Args:
            bucket_name: Name of the GCS bucket
            
        Returns:
            Tuple[List[str], List[str]]: Lists of video URIs and names
        """
        # Get the bucket object
        bucket = self.storage_client.get_bucket(bucket_name)
        
        # List all objects in the bucket and filter by .mp4 extension
        names_blobs = bucket.list_blobs()
        uris_blobs = bucket.list_blobs()
        
        names = [blob.name for blob in names_blobs if blob.name.endswith('.mp4') or blob.name.endswith('.MP4')]
        uris = [f"gs://{bucket_name}/{blob.name}" for blob in uris_blobs if blob.name.endswith('.mp4') or blob.name.endswith('.MP4')]

        return uris, names

    def _find_files_starting_with(self, directory, prefix):
        """
        Find all files in a directory that start with a specific prefix.

        Args:
            directory (str): Path to the directory to search in. Must be a valid
                           directory path that exists and is accessible.
            prefix (str): The prefix string to match against filenames. Files whose
                        names start with this exact string will be included in results.
        
        Returns:
            List[str]: A list of full file paths (directory + filename) for all files
                      that match the prefix. Returns an empty list if no matches are found.
        """
        matching_files = []
        for filename in os.listdir(directory):
            if filename.startswith(prefix):
                matching_files.append(os.path.join(directory, filename))
        return matching_files

    def export_camera_recording_to_bucket(self, bucket_name: str, camera_name: str):
        """
        Upload a camera recording file from local storage to a Google Cloud Storage bucket.
        If the video is not in MP4 format, it will be converted to MP4 before upload.
        
        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket to upload to.
                             The bucket must already exist and be accessible with current credentials.
            camera_name (str): Name/prefix of the camera used to identify the recording file.
                             This is used as a prefix to search for matching files in the
                             local videos directory.
        
        Environment Variables Required:
            - PROVISION_VIDEOS_SOURCE: Local directory path where camera recordings are stored
        """
        bucket = self.storage_client.bucket(bucket_name)

        # Full path to local video file
        local_file_path = self._find_files_starting_with(
            os.getenv("PROVISION_VIDEOS_SOURCE"), camera_name
        )[0]

        # Check if file needs conversion to MP4
        file_extension = os.path.splitext(local_file_path)[1].lower()
        upload_file_path = local_file_path
        converted_file_created = False
        
        if file_extension != '.mp4':
            print(f"Converting {local_file_path} to MP4 format...")
            print(f"Using ffmpeg path: {FFMPEG_PATH}")
            # Create temporary MP4 file path
            base_name = os.path.splitext(local_file_path)[0]
            converted_file_path = base_name + ".mp4"
            
            try:
                # Convert to MP4 using ffmpeg
                result = subprocess.run(
                    [FFMPEG_PATH, "-i", local_file_path, converted_file_path], 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
                
                # Verify the converted file was actually created
                if os.path.exists(converted_file_path):
                    upload_file_path = converted_file_path
                    converted_file_created = True
                    print(f"Conversion completed: {converted_file_path}")
                else:
                    print(f"ERROR: Converted file was not created: {converted_file_path}")
                    print("Using original file instead")
                    upload_file_path = local_file_path
                    
            except subprocess.CalledProcessError as e:
                print(f"ERROR: ffmpeg conversion failed: {e}")
                print(f"stdout: {e.stdout}")
                print(f"stderr: {e.stderr}")
                print("Using original file instead")
                upload_file_path = local_file_path
            except FileNotFoundError as e:
                print(f"ERROR: ffmpeg not found at {FFMPEG_PATH}: {e}")
                print("Using original file instead")
                upload_file_path = local_file_path

        # Verify the file to upload actually exists
        if not os.path.exists(upload_file_path):
            raise FileNotFoundError(f"File to upload does not exist: {upload_file_path}")
        
        # Only the filename (not path) becomes the GCS blob name
        # Ensure the blob name has .mp4 extension if conversion was attempted
        original_blob_name = os.path.basename(upload_file_path)
        if converted_file_created and not original_blob_name.lower().endswith('.mp4'):
            blob_name = os.path.splitext(original_blob_name)[0] + '.mp4'
        else:
            blob_name = original_blob_name
            
        blob = bucket.blob(blob_name)

        # Upload using the file path (original or converted)
        print(f"Uploading file: {upload_file_path} as {blob_name}")
        blob.upload_from_filename(upload_file_path)
        print(f"Uploaded to bucket: {blob_name}")

        # Delete the original file locally
        os.remove(local_file_path)
        
        # Delete the converted file locally if it was created
        if converted_file_created and upload_file_path != local_file_path:
            os.remove(upload_file_path)

    def convert_all_videos_in_bucket_to_mp4(self, bucket_name: str, extensions: List[str] = None):
        """
        Convert all videos with specified extensions in the given bucket to MP4.
        The original video files will be replaced by their MP4 versions.

        Args:
            bucket_name: Name of the Google Cloud Storage bucket
            extensions: List of video file extensions to convert (default ["avi"])
        """
        extensions = extensions or ["avi"]
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            if any(blob.name.lower().endswith(ext.lower()) for ext in extensions):
                print(f"Converting: {blob.name}")
                with tempfile.TemporaryDirectory() as tmpdir:
                    local_original_path = os.path.join(tmpdir, os.path.basename(blob.name))
                    local_converted_path = os.path.join(tmpdir,
                                                        os.path.splitext(os.path.basename(blob.name))[0] + ".mp4")

                    # Download original file
                    blob.download_to_filename(local_original_path)

                    # Convert to MP4 using ffmpeg
                    subprocess.run([FFMPEG_PATH, "-i", local_original_path, local_converted_path], check=True)

                    # Upload converted file
                    new_blob_name = os.path.splitext(blob.name)[0] + ".mp4"
                    new_blob = bucket.blob(new_blob_name)
                    new_blob.upload_from_filename(local_converted_path)

                    # Delete original file
                    blob.delete()

                    print(f"Converted and replaced: {blob.name} with {new_blob_name}")

    def generate_signed_url(self, bucket_name: str, blob_name: str, expiration_hours: int = 1) -> str:
        """
        Generate a signed URL for accessing a file in Google Cloud Storage.
        
        Args:
            bucket_name (str): Name of the GCS bucket
            blob_name (str): Name of the blob/file in the bucket
            expiration_hours (int): How many hours the signed URL should be valid (default: 1)
            
        Returns:
            str: A signed URL that can be used to access the file directly
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Generate signed URL valid for the specified hours
        expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        
        return signed_url
    
    def extract_bucket_and_blob_from_gs_url(self, gs_url: str) -> Tuple[str, str]:
        """
        Extract bucket name and blob name from a gs:// URL.
        
        Args:
            gs_url (str): A GCS URL in format gs://bucket-name/path/to/file
            
        Returns:
            Tuple[str, str]: (bucket_name, blob_name)
            
        Raises:
            ValueError: If the URL is not in the expected gs:// format
        """
        if not gs_url.startswith("gs://"):
            raise ValueError(f"Invalid GCS URL format: {gs_url}. Expected format: gs://bucket-name/path/to/file")
        
        # Remove gs:// prefix
        path = gs_url[5:]
        
        # Split into bucket and blob
        parts = path.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URL format: {gs_url}. Expected format: gs://bucket-name/path/to/file")
        
        bucket_name, blob_name = parts
        return bucket_name, blob_name