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


@pytest.fixture(scope="session")
def frames_extractor():
    """Fixture to create a FrameExtractor instance"""
    return FrameExtractor(every_n_frames=5)


@pytest.fixture(scope="session")
def shoplifting_analyzer():
    """Fixture to create a ShopliftingAnalyzer instance"""
    return ShopliftingAnalyzer()


def test_frame_extraction(frames_extractor):
    """Test that video frames are correctly extracted from test test_dataset"""
    # Process all videos in the test test_dataset
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


def test_shoplifting_analysis(shoplifting_analyzer):
    """Test that shoplifting analysis produces valid JSON output with enhanced checks."""
    # Analyze the extracted frames
    video_analysis = shoplifting_analyzer.analyze_single_video("test_frames", str(Path(__file__).parent))

    # New top-level required fields
    top_level_fields = [
        "sequence_name",
        "total_batches_analyzed",
        "shoplifting_determination",
        "confidence_level",
        "shoplifting_probability",
        "total_summary",
        "batch_results"
    ]

    for field in top_level_fields:
        assert field in video_analysis, f"Missing top-level required field: {field}"

    # Validate field types and formats at top-level
    assert isinstance(video_analysis["sequence_name"], str)
    assert isinstance(video_analysis["total_batches_analyzed"], int)
    assert video_analysis["shoplifting_determination"] in ["Yes", "No", "Inconclusive", "N/A"]
    assert isinstance(video_analysis["confidence_level"], str)
    assert video_analysis["confidence_level"].endswith("%") or video_analysis["confidence_level"] == "N/A"
    assert isinstance(video_analysis["shoplifting_probability"], str)
    assert isinstance(video_analysis["total_summary"], str)
    assert isinstance(video_analysis["batch_results"], list)

    # Validate batch_results structure
    for batch in video_analysis["batch_results"]:
        required_batch_fields = [
            "confidence_level",
            "key_behaviors",
            "summary_of_video",
            "shoplifting_determination",
            "sequence_name"
        ]
        for field in required_batch_fields:
            assert field in batch, f"Missing batch required field: {field}"

        # Validate field types within each batch
        assert isinstance(batch["confidence_level"], str)
        assert batch["confidence_level"].endswith("%") or batch["confidence_level"] == "N/A"
        assert isinstance(batch["key_behaviors"], str)
        assert isinstance(batch["summary_of_video"], str)
        assert batch["shoplifting_determination"] in ["Yes", "No", "Inconclusive", "N/A"]
        assert isinstance(batch["sequence_name"], str)

    # Additional logical consistency checks
    assert video_analysis["total_batches_analyzed"] == len(video_analysis["batch_results"]), \
        "Mismatch in total_batches_analyzed and actual batch_results count"

    # Probability checks
    probability = float(video_analysis["shoplifting_probability"])
    assert 0.0 <= probability <= 100.0, "Invalid shoplifting_probability range"

    # Ensure confidence_level percentages are valid
    top_confidence_level = video_analysis["confidence_level"]
    if top_confidence_level != "N/A":
        top_confidence = float(top_confidence_level.rstrip('%'))
        assert 0 <= top_confidence <= 100, "Invalid confidence_level range at top level"
