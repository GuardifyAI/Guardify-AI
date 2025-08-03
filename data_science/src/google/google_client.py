import vertexai
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from typing import List, Tuple
from google.cloud import storage
import tempfile
import subprocess
import os

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

        # Only the filename (not path) becomes the GCS blob name
        blob_name = os.path.basename(local_file_path)
        blob = bucket.blob(blob_name)

        # Upload using full local path
        blob.upload_from_filename(local_file_path)

        # Optional: delete after upload
        os.remove(local_file_path)

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
                    subprocess.run(["ffmpeg", "-i", local_original_path, local_converted_path], check=True)

                    # Upload converted file
                    new_blob_name = os.path.splitext(blob.name)[0] + ".mp4"
                    new_blob = bucket.blob(new_blob_name)
                    new_blob.upload_from_filename(local_converted_path)

                    # Delete original file
                    blob.delete()

                    print(f"Converted and replaced: {blob.name} with {new_blob_name}")