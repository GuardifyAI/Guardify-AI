import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import json
from analyze_shoplifting import download_and_analyze_frame

def test_single_frame():
    # Load environment variables
    load_dotenv()
    
    # Get Azure Storage settings
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    frames_container = os.getenv('AZURE_STORAGE_CONTAINER_FRAMES_NAME')
    
    if not connection_string or not frames_container:
        raise ValueError("Required environment variables not found")
    
    # Initialize Azure Storage client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(frames_container)
    
    # Get the first frame from the container
    frames = []
    for blob in container_client.list_blobs():
        if blob.name.lower().endswith('.jpg'):
            frames.append(blob.name)
            break  # Get only the first frame
    
    if not frames:
        raise ValueError(f"No frames found in container '{frames_container}'")
    
    test_frame = frames[0]
    print(f"\nTesting with frame: {test_frame}")
    
    # Analyze the single frame
    try:
        result = download_and_analyze_frame(test_frame, container_client)
        
        # Print results in a readable format
        print("\nAnalysis Results:")
        print("----------------")
        print(f"Frame: {result['frame']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Suspicious Activity: {result['suspicious_activity_detected']}")
        print(f"Confidence Score: {result['confidence_score']}")
        
        if result['detected_objects']:
            print("\nDetected Objects:")
            for obj in result['detected_objects']:
                print(f"  Type: {obj['type']}")
                print(f"  Bounding Box: {obj['bbox']}")
                print(f"  Confidence: {obj['confidence']}")
        
        # Verify JSON serialization
        print("\nTesting JSON serialization...")
        json_str = json.dumps(result, indent=2)
        print("JSON serialization successful!")
        print("\nJSON Output:")
        print(json_str)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    test_single_frame() 