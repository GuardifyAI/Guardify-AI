from azure.storage.blob import BlobServiceClient
from typing import List
import os


class AzureBlobHelper:
    def __init__(self, connection_string: str):
        """
        Initialize Azure Blob Helper with a connection string.
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def ensure_container_exists(self, container_name: str):
        """
        Ensure that a container exists, create it if it doesn't.
        """
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            container_client.get_container_properties()
        except Exception:
            container_client = self.blob_service_client.create_container(container_name)
        return container_client

    def list_blobs(self, container_name: str, prefix: str = '') -> List[str]:
        """
        List all blobs in a container, optionally under a prefix (folder).
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        for blob in container_client.list_blobs(name_starts_with=prefix):
            blobs.append(blob.name)
        return blobs

    def download_blob_as_file(self, container_name: str, blob_name: str, save_path: str) -> None:
        """
        Download a blob and save it locally.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())

    def download_blob_as_bytes(self, container_name: str, blob_name: str) -> bytes:
        """
        Download a blob and return its contents as bytes.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        return download_stream.readall()

    def upload_file_as_blob(self, container_name: str, local_path: str, blob_path: str) -> None:
        """
        Upload a local file to a blob container.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def upload_bytes_as_blob(self, container_name: str, data: bytes, blob_path: str) -> None:
        """
        Upload bytes directly to a blob container.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(data, overwrite=True)

    def upload_json_object(self, container_name: str, blob_name: str, data: dict):
        """
        Upload a Python dict as a JSON blob.
        """
        import json
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.upload_blob(name=blob_name, data=json.dumps(data, indent=2), overwrite=True)

    def does_video_frames_exist(self, container_name: str, video_name: str) -> bool:
        """
        Check if any frames already exist in Azure Blob Storage under the given video name.
        """
        existing_blobs = self.list_blobs(container_name, prefix=f"{video_name}/")
        return len(existing_blobs) > 0
