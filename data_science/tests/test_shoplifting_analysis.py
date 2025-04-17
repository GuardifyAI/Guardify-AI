import os
import json
import pytest
import cv2
from pathlib import Path
from data_science.src.azure.extract_frames import extract_frames, process_directory
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
    process_directory(str(TEST_DATASET_DIR), str(TEST_FRAMES_DIR))
    
    # Check that frames were created
    frame_files = list(TEST_FRAMES_DIR.glob("**/*.jpg"))
    assert len(frame_files) > 0, "No frames were extracted"
    
    # Verify frame content
    for frame_path in frame_files:
        img = cv2.imread(str(frame_path))
        assert img is not None, f"Could not read frame {frame_path}"
        assert len(img.shape) == 3, f"Frame {frame_path} should have 3 channels (RGB)"
        assert img.shape[2] == 3, f"Frame {frame_path} should have 3 channels (RGB)"

def test_shoplifting_analysis():
    """Test that shoplifting analysis produces valid JSON output"""
    # Create analyzer instance
    analyzer = ShopliftingAnalyzer()
    
    # Analyze the extracted frames
    analyzer.analyze_shoplifting_directory(str(TEST_FRAMES_DIR), str(TEST_ANALYSIS_DIR))
    
    # Check that analysis files were created
    analysis_files = list(TEST_ANALYSIS_DIR.glob("*.json"))
    assert len(analysis_files) > 0, "No analysis files were created"
    
    # Verify JSON content
    for analysis_file in analysis_files:
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
            
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
            assert field in analysis_data, f"Missing required field: {field}"
        
        # Check field types and formats
        assert isinstance(analysis_data["summary_of_video"], str)
        assert analysis_data["conclusion"] in ["Yes", "No", "Inconclusive", "N/A"]
        assert isinstance(analysis_data["confidence_level"], str)
        assert analysis_data["confidence_level"].endswith("%") or analysis_data["confidence_level"] == "N/A"
        assert isinstance(analysis_data["key_behaviors"], str)
        assert isinstance(analysis_data["sequence_name"], str)
        assert isinstance(analysis_data["frame_count"], int)
        assert isinstance(analysis_data["analyzed_frame_count"], int)
        assert analysis_data["analyzed_frame_count"] <= analysis_data["frame_count"] 