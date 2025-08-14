import os
import sys
import time
import signal
from datetime import datetime, timezone

# Add the project root to Python path FIRST - more robust approach
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate from data_science/src to project root (Guardify-AI)
project_root = os.path.dirname(os.path.dirname(current_dir))

# Add project root to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import load_env_variables using absolute path to avoid conflict with local utils.py
import importlib.util
spec = importlib.util.spec_from_file_location("env_utils", os.path.join(project_root, "utils", "env_utils.py"))
env_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env_utils)
load_env_variables = env_utils.load_env_variables

from google_client.google_client import GoogleClient
from data_science.src.model.pipeline.shoplifting_analyzer import create_unified_analyzer, create_agentic_analyzer

from data_science.src.utils import UNIFIED_MODEL, AGENTIC_MODEL
# Import create_logger using absolute path to avoid conflict with local utils.py
logger_spec = importlib.util.spec_from_file_location("logger_utils", os.path.join(project_root, "utils", "logger_utils.py"))
logger_utils = importlib.util.module_from_spec(logger_spec)
logger_spec.loader.exec_module(logger_utils)
create_logger = logger_utils.create_logger

load_env_variables()
from data_science.src.model.pipeline.pipeline_manager import PipelineManager
import argparse

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    shutdown_requested = True
    print("\nShutdown signal received. Stopping continuous monitoring gracefully...")

def get_video_creation_time(google_client, bucket_name: str, video_name: str) -> datetime:
    """Get the creation time of a video in the bucket."""
    try:
        bucket = google_client.storage_client.bucket(bucket_name)
        blob = bucket.blob(video_name)
        blob.reload()  # Refresh metadata

        # Ensure the datetime is timezone-aware in UTC
        creation_time = blob.time_created
        if creation_time.tzinfo is None:
            creation_time = creation_time.replace(tzinfo=timezone.utc)
        else:
            creation_time = creation_time.astimezone(timezone.utc)

        return creation_time
    except Exception as e:
        print(f"DEBUG: Error getting creation time for {video_name}: {e}")
        # If we can't get the creation time, return a very old timestamp
        # so the video won't be filtered out
        return datetime.min.replace(tzinfo=timezone.utc)

def run_continuous_monitoring(args, logger, google_client, bucket_name: str, start_timestamp: datetime):
    """
    Run continuous monitoring mode that watches for new videos from a specific camera.
    """
    global shutdown_requested

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(f"Starting continuous monitoring for camera '{args.camera_name}'")
    logger.info(f"Monitoring videos created after: {start_timestamp}")

    # Create analyzer based on strategy
    if args.strategy == UNIFIED_MODEL:
        shoplifting_analyzer = create_unified_analyzer(
            detection_threshold=args.threshold,
            logger=logger
        )
    else:  # AGENTIC_MODEL
        shoplifting_analyzer = create_agentic_analyzer(
            detection_threshold=args.threshold,
            logger=logger
        )

    # Create pipeline manager
    pipeline_manager = PipelineManager(google_client, shoplifting_analyzer, logger=logger)

    # Keep track of processed videos to avoid reprocessing
    processed_videos = set()

    logger.info(f"Starting monitoring loop (polling every {args.polling_interval} seconds)")

    while not shutdown_requested:
        try:
            # Get all video URIs from bucket
            video_uris = pipeline_manager._get_video_uris_from_bucket(bucket_name)

            # Filter videos by camera name and timestamp
            new_videos = []
            for video_uri in video_uris:
                # Extract video name from URI
                video_name = video_uri.split('/')[-1]

                # Skip if already processed
                if video_name in processed_videos:
                    continue

                # Check if video name starts with camera name
                if not video_name.lower().startswith(args.camera_name.lower()):
                    continue

                # Check if video was created after start timestamp
                video_creation_time = get_video_creation_time(google_client, bucket_name, video_name)
                if video_creation_time < start_timestamp:
                    continue

                new_videos.append(video_uri)
                processed_videos.add(video_name)

            # Process new videos
            if new_videos:
                logger.info(f"Found {len(new_videos)} new videos to process")
                for video_uri in new_videos:
                    if shutdown_requested:
                        logger.info("Shutdown requested - stopping before processing new video")
                        break

                    logger.info(f"Processing new video: {video_uri}")
                    try:
                        # Analyze the video
                        result = shoplifting_analyzer.analyze_video_from_bucket(
                            video_uri,
                            iterations=args.iterations,
                            pickle_analysis=args.diagnostic
                        )

                        # Log results
                        final_detection = result.get('final_detection', False)
                        final_confidence = result.get('final_confidence', 0.0)
                        logger.info(f"Analysis result for {video_uri}: detected={final_detection}, confidence={final_confidence:.3f}")

                        # If theft detected, log with high priority
                        if final_detection:
                            logger.warning(f"THEFT DETECTED in {video_uri} with confidence {final_confidence:.3f}")

                    except Exception as e:
                        logger.error(f"Failed to analyze {video_uri}: {e}")

                    # Check for shutdown after each video
                    if shutdown_requested:
                        logger.info("Shutdown requested - stopping video processing")
                        break
            else:
                logger.debug("No new videos found")

            # Check for shutdown before waiting
            if shutdown_requested:
                logger.info("Shutdown requested - exiting monitoring loop")
                break

            # Wait before next poll
            for _ in range(args.polling_interval):
                if shutdown_requested:
                    logger.info("Shutdown requested during polling wait - exiting")
                    break
                time.sleep(1)

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(5)  # Brief pause before retrying

    logger.info("Continuous monitoring stopped gracefully")


def main():
    """
    🚀 ADVANCED DUAL-STRATEGY SHOPLIFTING DETECTION SYSTEM
    =======================================================
    
    This main file supports both analysis strategies using consolidated architecture:
    
    **UNIFIED STRATEGY:**
    - Single-model direct video→detection analysis
    - Eliminates information loss from multi-step pipeline
    - Faster processing with direct confidence assessment
    - Uses few-shot learning with real theft examples
    
    **AGENTIC STRATEGY:**
    - Two-step Enhanced CV→Analysis pipeline
    - Detailed observational layer with specialized decision layer
    - Enhanced debugging and transparency
    - Independent fine-tuning of observation vs decision components
    - Clear separation between observation and interpretation
    
    USAGE:
    python main.py --strategy unified   # Use unified single-model approach
    python main.py --strategy agentic    # Use agentic model approach
    python main.py --strategy both      # Compare both approaches (diagnostic)
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Shoplifting Detection Analysis System')
    parser.add_argument('--strategy', choices=[UNIFIED_MODEL, AGENTIC_MODEL],
                        default=UNIFIED_MODEL, help='Analysis strategy to use')
    parser.add_argument('--max-videos', type=int, default=20,
                        help='Maximum number of videos to analyze')
    parser.add_argument('--iterations', type=int, default=3,
                        help='Number of analysis iterations per video')
    parser.add_argument('--threshold', type=float, default=0.45,
                        help='Detection confidence threshold')
    parser.add_argument('--diagnostic', action='store_true',
                        help='Enable diagnostic mode with enhanced logging', default=True)
    parser.add_argument('--export', action='store_true',
                        help='Export results to CSV')
    parser.add_argument('--labels-csv-path', type=str, default=None,
                        help='Path to CSV file containing ground truth labels for accuracy comparison')

    # New arguments for continuous monitoring mode
    parser.add_argument('--continuous-mode', action='store_true',
                        help='Enable continuous monitoring mode for real-time analysis')
    parser.add_argument('--camera-name', type=str, default=None,
                        help='Camera name to filter videos by (only process videos from this camera)')
    parser.add_argument('--start-timestamp', type=str, default=None,
                        help='ISO timestamp to start monitoring from (only process videos created after this time)')
    parser.add_argument('--polling-interval', type=int, default=30,
                        help='Polling interval in seconds for continuous mode (default: 30)')

    args = parser.parse_args()

    # Create logger for debugging
    logger = create_logger('AdvancedShopliftingAnalysis', 'advanced_main_analysis.log')
    logger.info(f"Starting ADVANCED DUAL-STRATEGY shoplifting analysis pipeline")
    logger.info(f"Strategy: {args.strategy.upper()}")
    logger.info(f"Max videos: {args.max_videos}")
    logger.info(f"Iterations: {args.iterations}")
    logger.info(f"Threshold: {args.threshold}")
    logger.info(f"Diagnostic mode: {args.diagnostic}")
    logger.info(f"Continuous mode: {args.continuous_mode}")
    if args.continuous_mode:
        logger.info(f"Camera name filter: {args.camera_name}")
        logger.info(f"Start timestamp: {args.start_timestamp}")
        logger.info(f"Polling interval: {args.polling_interval} seconds")
    logger.info(
        f"Ground truth labels: {args.labels_csv_path if args.labels_csv_path else 'None (no accuracy comparison)'}")

    # Initialize GoogleClient with your existing authentication
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

    # Get bucket name
    bucket_name = os.getenv("BUCKET_NAME")
    logger.info(f"[TARGET] Starting analysis of videos in bucket: {bucket_name}")

    # Check if continuous mode is enabled
    if args.continuous_mode:
        if not args.camera_name:
            logger.error("Camera name is required for continuous mode")
            sys.exit(1)
        if not args.start_timestamp:
            logger.error("Start timestamp is required for continuous mode")
            sys.exit(1)

        # Parse start timestamp - handle both simple format (2025-08-14 15:18:28) and ISO format
        try:
            # Clean up the timestamp string
            timestamp_str = args.start_timestamp.replace('Z', '+00:00')

            # Try to parse as ISO format first
            try:
                start_timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                # If that fails, try parsing as simple format and assume local timezone
                start_timestamp = datetime.strptime(args.start_timestamp, '%Y-%m-%d %H:%M:%S')

            # If timezone-naive, assume it's local time and convert to UTC
            if start_timestamp.tzinfo is None:
                # Assume local timezone (you can adjust this offset as needed)
                # Based on the bucket timestamps, it looks like you're UTC+3
                import datetime as dt
                local_offset = dt.timedelta(hours=3)  # Adjust this to your timezone
                start_timestamp = start_timestamp.replace(tzinfo=timezone.utc) - local_offset
                logger.info(f"Parsed naive timestamp as local time, converted to UTC: {start_timestamp}")
            else:
                # Convert to UTC if it has a different timezone
                start_timestamp = start_timestamp.astimezone(timezone.utc)
                logger.info(f"Parsed timezone-aware timestamp, converted to UTC: {start_timestamp}")

        except ValueError as e:
            logger.error(f"Invalid start timestamp format: {e}")
            logger.error(f"Expected format: '2025-08-14 15:18:28' or ISO format")
            sys.exit(1)

        # Run continuous monitoring
        run_continuous_monitoring(
            args, logger, google_client, bucket_name, start_timestamp
        )
    else:
        # Execute based on strategy using consolidated manager (original behavior)
        if args.strategy == UNIFIED_MODEL:
            logger.info(f"[{UNIFIED_MODEL.upper()}] Using enhanced unified single-model approach")

            # Create unified analyzer
            shoplifting_analyzer = create_unified_analyzer(
                detection_threshold=args.threshold,
                logger=logger
            )

            # Create pipeline manager
            pipeline_manager = PipelineManager(google_client, shoplifting_analyzer, logger=logger)

            results = pipeline_manager.run_unified_analysis(
                bucket_name, args.max_videos, args.iterations, args.diagnostic, args.export, args.labels_csv_path
            )

        elif args.strategy == AGENTIC_MODEL:
            logger.info(f"[{AGENTIC_MODEL.upper()}] Using enhanced agentic model approach")

            # Create agentic analyzer
            shoplifting_analyzer = create_agentic_analyzer(
                detection_threshold=args.threshold,
                logger=logger
            )

            # Create pipeline manager
            pipeline_manager = PipelineManager(google_client, shoplifting_analyzer, logger=logger)

            results = pipeline_manager.run_agentic_analysis(
                bucket_name, args.max_videos, args.iterations, args.diagnostic, args.export, args.labels_csv_path
            )

        logger.info("[SUCCESS] Advanced pipeline analysis completed successfully!")


if __name__ == "__main__":
    main()
