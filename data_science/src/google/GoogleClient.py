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

    def download_bucket_content(self, bucket_name: str, local_path: str):
        """
        Download all contents from a Google Cloud Storage bucket to a local directory.

        Args:
            bucket_name: Name of the GCS bucket.
            local_path: Local directory path to download the bucket's contents into.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        os.makedirs(local_path, exist_ok=True)

        for blob in blobs:
            # Make sure the local subdirectory exists
            local_file_path = os.path.join(local_path, blob.name)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            print(f"Downloading {blob.name} to {local_file_path}")
            blob.download_to_filename(local_file_path)

    def num_of_files_in_bucket_path(self, bucket_name: str, path: str = None) -> int:
        """
        Count the number of files in a specific path inside a Google Cloud Storage bucket.
        If path is None, counts all files in the bucket.

        Args:
            bucket_name: Name of the GCS bucket.
            path: Path inside the bucket to count files (prefix). If None, counts all files.

        Returns:
            int: Number of files in the specified path or the whole bucket.
        """
        bucket = self.storage_client.bucket(bucket_name)
        if path:
            blobs = list(bucket.list_blobs(prefix=path))
        else:
            blobs = list(bucket.list_blobs())
        return len(blobs)