# Video Recording and Upload System

A modular video recording system that captures camera streams from Provision ISR platform and uploads them concurrently to Google Cloud Storage.

## Architecture

### Components

- **`VideoRecorder`** (`video_recorder.py`): Handles camera authentication and recording process
- **`VideoUploader`** (`video_uploader.py`): Manages concurrent upload operations in background threads  
- **`main.py`**: Command-line interface and orchestration logic

### Key Features

- **Separation of Concerns**: Recording and uploading are handled by separate, focused classes
- **Concurrent Processing**: Uploads happen in background threads while recording continues
- **Modular Design**: Components can be used independently or together
- **Comprehensive Logging**: Each component has its own logger for debugging
- **Graceful Shutdown**: Proper cleanup ensures no uploads are lost

## Usage

### Command Line

```bash
# Basic usage
python -m backend.video.main --camera "Camera Name" --duration 30

# Get help
python -m backend.video.main --help
```

## Environment Variables

Required environment variables:

```bash
# Provision ISR Authentication
PROVISION_QR_CODE=your_qr_code
PROVISION_USERNAME=your_username  
PROVISION_PASSWORD=your_password

# Google Cloud Configuration
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_PROJECT_LOCATION=your_location
SERVICE_ACCOUNT_FILE=path/to/service_account.json
BUCKET_NAME=your_storage_bucket

# Video Storage
PROVISION_VIDEOS_SOURCE=path/to/local/videos
```

## Threading Model

1. **Main Thread**: Handles recording process (start/stop recording, camera navigation)
2. **Upload Worker Thread**: Processes upload queue in background
3. **Thread-Safe Communication**: Uses Queue and Event objects for coordination

## Error Handling

- Upload failures don't interrupt recording process
- Graceful shutdown ensures pending uploads complete
- Comprehensive logging helps with debugging
- Timeout mechanisms prevent hanging during shutdown