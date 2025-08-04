import pytest
from pathlib import Path
from data_science.src.model.pipeline.shoplifting_analyzer import ShopliftingAnalyzer, create_unified_analyzer, create_agentic_analyzer
from data_science.src.model.agentic.analysis_model import AnalysisModel
from data_science.src.model.agentic.computer_vision_model import ComputerVisionModel
from data_science.src.model.pipeline.pipeline_manager import PipelineManager
import shutil
import os
from data_science.src.utils import load_env_variables, UNIFIED_MODEL, AGENTIC_MODEL, create_logger
from google_client.google_client import GoogleClient

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
    cv_model = ComputerVisionModel()
    analysis_model = AnalysisModel(model_name="projects/397795663248/locations/us-central1/endpoints/2744395316580057088")
    return ShopliftingAnalyzer(cv_model=cv_model,
                               analysis_model=analysis_model,
                               detection_strictness=0.7)

@pytest.fixture(scope="session")
def google_client():
    return GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

@pytest.fixture(scope="session")
def logger():
    return create_logger('TestShopliftingAnalysis', 'test_analysis.log')

def test_unified_strategy_analysis(google_client, logger):
    """
    Test the unified strategy analysis on a single video from the bucket.
    Verifies that the unified strategy produces valid results with the expected structure.
    """
    # Create unified analyzer
    shoplifting_analyzer = create_unified_analyzer(
        detection_threshold=0.45,
        logger=logger
    )

    # Create pipeline manager
    pipeline_manager = PipelineManager(google_client, shoplifting_analyzer, logger=logger)

    # Get bucket name from environment
    bucket_name = os.getenv("BUCKET_NAME")

    # Run unified analysis with max_videos=1
    results = pipeline_manager.run_unified_analysis(
        bucket_name=bucket_name,
        max_videos=1,
        iterations=1,
        diagnostic=True,
        export=False,
        labels_csv_path=None
    )

    # Verify results structure
    assert len(results) == 1, "Should analyze exactly one video"
    result = results[0]
    result_assertions(result, UNIFIED_MODEL)

def test_agentic_strategy_analysis(google_client, logger):
    """
    Test the agentic strategy analysis on a single video from the bucket.
    Verifies that the agentic strategy produces valid results with the expected structure.
    """
    # Create agentic analyzer
    shoplifting_analyzer = create_agentic_analyzer(
        detection_threshold=0.45,
        logger=logger
    )

    # Create pipeline manager
    pipeline_manager = PipelineManager(google_client, shoplifting_analyzer, logger=logger)

    # Get bucket name from environment
    bucket_name = os.getenv("BUCKET_NAME")

    # Run agentic analysis with max_videos=1
    results = pipeline_manager.run_agentic_analysis(
        bucket_name=bucket_name,
        max_videos=1,
        iterations=1,
        diagnostic=True,
        export=False,
        labels_csv_path=None
    )

    # Verify results structure
    assert len(results) == 1, "Should analyze exactly one video"
    result = results[0]
    result_assertions(result, AGENTIC_MODEL)

def result_assertions(result: dict, analysis_approach: str):
    result_keys = set(result.keys())
    expected_keys = set(ShopliftingAnalyzer.ANALYSIS_DICT.keys())
    missing_keys = expected_keys - result_keys
    extra_keys = result_keys - expected_keys

    assert not missing_keys, f"Missing keys in result: {missing_keys}"
    assert not extra_keys, f"Extra keys in result: {extra_keys}"

    # Verify confidence and detection values are valid
    assert result["analysis_approach"] == analysis_approach
    assert 0 <= result["final_confidence"] <= 1
    assert isinstance(result["final_detection"], bool)
    assert len(result["confidence_levels"]) == result["iterations"]
    assert len(result["detection_results"]) == result["iterations"]
