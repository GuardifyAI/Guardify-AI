# Shoplifting Detection with Azure OpenAI

This project uses Azure OpenAI's GPT-4o model to analyze surveillance video frames for shoplifting detection.

## Setup

1. Install the required dependencies:
   ```
   pip install -r ../requirements.txt
   ```

2. Set up your Azure OpenAI credentials in a `.env` file in the project root:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_API_BASE=your_azure_endpoint_here
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   ```

3. Make sure you have a deployment of the GPT-4 Vision model set up in your Azure OpenAI service.

## Usage

### Step 1: Extract Frames from Videos

To extract frames from your videos at 4 frames per second:

```bash
python data-science/src/extract_frames.py --input data-science/shoplifting_dataset --output data-science/extracted_frames
```

This will process all MP4 files in the `shoplifting_dataset` directory and its subdirectories, and save the extracted frames in the `extracted_frames` directory.

### Step 2: Analyze Frames for Shoplifting

To analyze the extracted frames for shoplifting detection:

```bash
python src/analyze_shoplifting.py --frames extracted_frames --output analysis_results
```

This will analyze all frame sets in the `extracted_frames` directory and save the analysis results in the `analysis_results` directory.

## Understanding the Results

The analysis results are saved as JSON files, one for each video sequence. Each file contains:

- `sequence_name`: Name of the video sequence
- `frame_count`: Total number of frames in the sequence
- `analyzed_frame_count`: Number of frames used for analysis
- `analysis`: Detailed analysis from the GPT-4 Vision model, including:
  - Frame-by-frame observations
  - Patterns of behavior
  - Conclusion with shoplifting determination and confidence level

## Notes

- The analysis uses a maximum of 8 frames per video to stay within token limits.
- For longer videos, frames are sampled evenly throughout the sequence.
- The GPT-4 Vision model provides a detailed analysis and conclusion about whether shoplifting is occurring. 