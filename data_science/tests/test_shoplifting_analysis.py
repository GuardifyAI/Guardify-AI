import os
import json
import pytest
import cv2
from pathlib import Path
from data_science.src.azure.extract_frames import FrameExtractor
from data_science.src.azure.analyze_shoplifting import ShopliftingAnalyzer
import shutil

# Test data paths
TEST_DATASET_DIR = Path(__file__).parent.parent / "test_dataset"
TEST_FRAMES_DIR = Path(__file__).parent / "test_frames"
TEST_ANALYSIS_DIR = Path(__file__).parent / "test_analysis"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment by creating necessary directories"""
    # Verify test test_dataset exists
    assert TEST_DATASET_DIR.exists(), f"Test test_dataset directory not found at {TEST_DATASET_DIR}"
    assert any(TEST_DATASET_DIR.glob("*.avi")), "No video files found in test test_dataset"
    
    # Create output directories
    TEST_FRAMES_DIR.mkdir(exist_ok=True)
    TEST_ANALYSIS_DIR.mkdir(exist_ok=True)
    yield
    
    # Cleanup (optional, comment out if you want to keep test data)
    if TEST_FRAMES_DIR.exists():
        shutil.rmtree(TEST_FRAMES_DIR)
    if TEST_ANALYSIS_DIR.exists():
        shutil.rmtree(TEST_ANALYSIS_DIR)

def test_frame_extraction():
    """Test that video frames are correctly extracted from test test_dataset"""
    # Process all videos in the test test_dataset
    frames_extractor = FrameExtractor()
    video_files = sorted(
        file
        for ext in frames_extractor.ALLOWED_VIDEO_EXTENSIONS
        for file in TEST_DATASET_DIR.glob(f"**/*{ext}")
    )

    # Get the first video file, if any
    first_video_path = str(video_files[0].resolve()) if video_files else None
    frames_extractor.extract_frames(first_video_path, str(TEST_FRAMES_DIR))
    # Check that frames were created
    frame_files = list(TEST_FRAMES_DIR.glob("**/*.jpg"))
    assert len(frame_files) > 0, "No frames were extracted"
    
    # Verify frame content
    for frame_path in frame_files:
        img = cv2.imread(str(frame_path))
        assert img is not None, f"Could not read frame {frame_path}"
        assert len(img.shape) == 3, f"Frame {frame_path} should have 3 channels (RGB)"
        assert img.shape[2] == 3, f"Frame {frame_path} should have 3 channels (RGB)"

    print(3)

def test_shoplifting_analysis():
    """Test that shoplifting analysis produces valid JSON output"""
    # Create analyzer instance
    analyzer = ShopliftingAnalyzer()
    
    # Analyze the extracted frames
    video_analysis = analyzer.analyze_single_video("test_frames", str(Path(__file__).parent))
    
    # Check that analysis files were created
    assert len(video_analysis) > 0, "No analysis was created"

    # Check required fields
    required_fields = [
            "summary_of_video",
            "conclusion",
            "confidence_level",
            "key_behaviors",
            "sequence_name",
            "frame_count",
            "analyzed_frame_count"
        ]
        
    for field in required_fields:
        assert field in video_analysis, f"Missing required field: {field}"
        
    # Check field types and formats
    assert isinstance(video_analysis["summary_of_video"], str)
    assert video_analysis["conclusion"] in ["Yes", "No", "Inconclusive", "N/A"]
    assert isinstance(video_analysis["confidence_level"], str)
    assert video_analysis["confidence_level"].endswith("%") or video_analysis["confidence_level"] == "N/A"
    assert isinstance(video_analysis["key_behaviors"], str)
    assert isinstance(video_analysis["sequence_name"], str)
    assert isinstance(video_analysis["frame_count"], int)
    assert isinstance(video_analysis["analyzed_frame_count"], int)
    assert video_analysis["analyzed_frame_count"] <= video_analysis["frame_count"]