import vertexai
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from typing import List, Tuple
from google.cloud import storage

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