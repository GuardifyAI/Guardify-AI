import pytest
from pathlib import Path
from data_science.src.google.ShopliftingAnalyzer import ShopliftingAnalyzer
from data_science.src.google.GoogleClient import GoogleClient
import shutil
import os
from data_science.src.utils import load_env_variables
load_env_variables()

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

@pytest.fixture(scope="session")
def shoplifting_analyzer():
    """Fixture to create a ShopliftingAnalyzer instance"""
    return ShopliftingAnalyzer(detection_strictness=0.7)

@pytest.fixture(scope="session")
def google_client():
    return GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

def test_analyze_video_from_bucket_no_shoplifting(google_client, shoplifting_analyzer):
    """
    Test analyzing a video that does not contain shoplifting.
    This test verifies that the analyzer correctly identifies a video without shoplifting activity.
    """
    non_shoplifting_video_uri = "gs://guardify-test-videos/Shoplifting001_x264_4.mp4"
    # Analyze the video
    results = shoplifting_analyzer.analyze_video_from_bucket(
        video_uri=non_shoplifting_video_uri,
        max_api_calls=1,
        pickle_analysis=False
    )

    # Assert that shoplifting was not detected
    assert not results["shoplifting_determination"], "Shoplifting was incorrectly detected in a video without shoplifting"
    
    # Assert that the probability is low
    assert results["shoplifting_probability"] < 0.5, "Shoplifting probability should be low for a video without shoplifting"
    
    # Assert that we have the expected structure in the results
    assert "confidence_levels" in results
    assert "shoplifting_detected_results" in results
    assert "cv_model_responses" in results
    assert "analysis_model_responses" in results
    assert "stats" in results


def test_analyze_video_from_bucket_with_shoplifting(google_client, shoplifting_analyzer):
    """
    Test analyzing a video that contains shoplifting.
    This test verifies that the analyzer correctly identifies a video with shoplifting activity.
    """
    shoplifting_video_uri = "gs://guardify-test-videos/43dd8387-28ad-4a64-bda1-9c566c526b82 (1).mp4"
    # Analyze the video
    results = shoplifting_analyzer.analyze_video_from_bucket(
        video_uri=shoplifting_video_uri,
        max_api_calls=1,
        pickle_analysis=False
    )

    # Assert that shoplifting was detected
    assert results["shoplifting_determination"], "Shoplifting was not detected in a video with shoplifting"
    
    # Assert that the probability is high
    assert results["shoplifting_probability"] > 0.7, "Shoplifting probability should be high for a video with shoplifting"
    
    # Assert that we have the expected structure in the results
    assert "confidence_levels" in results
    assert "shoplifting_detected_results" in results
    assert "cv_model_responses" in results
    assert "analysis_model_responses" in results
    assert "stats" in results
    
    # Additional assertions for shoplifting case
    assert any(results["shoplifting_detected_results"]), "At least one analysis should detect shoplifting"
    assert results["stats"]["True Count"] > 0, "Should have at least one true detection"

@pytest.mark.parametrize("video_file", ["shop_video_2.mp4"])
def test_analyze_local_video(google_client, shoplifting_analyzer, video_file):
    # Analyze the video
    results = shoplifting_analyzer.analyze_local_video(
        video_path=str(TEST_DATASET_DIR) + "/" + video_file,
        max_api_calls=1,
        pickle_analysis=False
    )
    # Assert that we have the expected structure in the results
    assert "confidence_levels" in results
    assert "shoplifting_detected_results" in results
    assert "cv_model_responses" in results
    assert "analysis_model_responses" in results
    assert "stats" in results
