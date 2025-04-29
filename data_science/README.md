# Shoplifting Detection with Azure OpenAI

This project uses Azure OpenAI's GPT-4 Vision model to analyze surveillance video frames for shoplifting detection.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Azure OpenAI credentials in a `.env` file in the project root:
   ```
    # Azure Blob Storage connection
    AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
   
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here

   # Azure Blob Storage Configuration
   AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
   AZURE_STORAGE_CONTAINER_DATASET_NAME=your_dataset_container_name
   AZURE_STORAGE_CONTAINER_FRAMES_NAME=your_frames_container_name
   AZURE_STORAGE_CONTAINER_OUTPUT_NAME=your_results_container_name
   
   # Azure Whisper API settings
    AZURE_WHISPER_ENDPOINT=your_azure_endpoint_here
    AZURE_WHISPER_API_KEY=your_real_azure_api_key
    AZURE_WHISPER_DEPLOYMENT=whisper

   ```
3. Make sure you have a deployment of the GPT-4 Vision model set up in your Azure OpenAI service.

## Usage

To run the analysis from the base Guardify-AI directory:

```bash
python -m data_science.src.azure.manager
```

This command executes the complete pipeline:
1. Downloads videos from Azure Blob Storage to `dataset_local/`
2. Extracts frames from videos to `extracted_frames_local/`
3. Uploads extracted frames back to Azure Storage
4. Analyzes all frames in batches of 10 frames each
5. Combines batch results into a comprehensive analysis
6. Uploads final analysis results to Azure Storage
7. Displays a summary of the analysis results

### Analysis Process
- Each video's frames are processed in batches of 10 frames
- Every batch receives its own analysis with determination and confidence level
- All batch results are combined into a final analysis that includes:
  - Overall shoplifting determination
  - Average confidence level
  - Shoplifting probability (ratio of positive detections)
  - Top 5 most significant behaviors observed
  - Comprehensive summary of all observations
  - Individual batch results for reference

### Directory Structure
- `dataset_local/`: Local storage for downloaded videos
- `extracted_frames_local/`: Local storage for extracted video frames
- Each video will have its own subdirectory containing the extracted frames
- Analysis results are uploaded as `{video_name}_analysis.json` files

### Performance Notes
- All frames from each video are analyzed (not just a sample)
- Processing is done in batches of 10 frames for optimal performance
- The system skips processing for videos that have already been analyzed
- All intermediate results are cached locally and in Azure Storage
- Progress bars show the status of each operation and batch

## Understanding the Results

The analysis results are saved as JSON files, one for each video sequence. Each file contains:

- `sequence_name`: Name of the video sequence
- `total_batches_analyzed`: Number of batches processed for this video
- `shoplifting_determination`: Final Yes/No determination
- `confidence_level`: Average confidence across all batches
- `shoplifting_probability`: Ratio of positive detections across batches
- `key_behaviors`: Top 5 most significant behaviors observed
- `summary_of_video`: Comprehensive summary of all observations
- `batch_results`: Individual results from each batch of 10 frames

## Notes

- Each batch analyzes exactly 10 frames for consistent analysis
- The final determination is based on majority voting across all batches
- Confidence levels are averaged across all batches
- The system preserves all batch-level analyses for detailed review

## Running Whisper Audio Transcription Test
This project also includes a Whisper-based audio transcription test, which extracts audio from videos and sends it to Azure OpenAI Whisper for transcription.
To run the audio transcription (from the Guardify-AI base directory):
- python data_science/src/azure/test_audio_transcription.py
This script will:
- Extract the audio track from a sample video located in dataset_local/. 
- Preprocess and normalize the audio for better transcription quality. 
- Send the cleaned audio to Azure Whisper using the configured deployment. 
- Print the transcribed text result in the terminal.