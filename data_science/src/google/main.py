from GoogleClient import GoogleClient
import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from data_science.src.utils import load_env_variables, create_logger, UNIFIED_MODEL, AGENTIC_MODEL, BOTH_MODELS

load_env_variables()
from PipelineManager import PipelineManager
import argparse


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
    parser.add_argument('--strategy', choices=[UNIFIED_MODEL, AGENTIC_MODEL, BOTH_MODELS],
                        default='unified', help='Analysis strategy to use')
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

    args = parser.parse_args()

    # Create logger for debugging
    logger = create_logger('AdvancedShopliftingAnalysis', 'advanced_main_analysis.log')
    logger.info(f"Starting ADVANCED DUAL-STRATEGY shoplifting analysis pipeline")
    logger.info(f"Strategy: {args.strategy.upper()}")
    logger.info(f"Max videos: {args.max_videos}")
    logger.info(f"Iterations: {args.iterations}")
    logger.info(f"Threshold: {args.threshold}")
    logger.info(f"Diagnostic mode: {args.diagnostic}")
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

    # Create consolidated pipeline manager for both strategies
    pipeline_manager = PipelineManager(google_client, logger=logger)

    # Execute based on strategy using consolidated manager
    if args.strategy == UNIFIED_MODEL:
        logger.info(f"[{UNIFIED_MODEL.upper()}] Using enhanced unified single-model approach")
        results = pipeline_manager.run_unified_analysis(
            bucket_name, args.max_videos, args.iterations,
            args.threshold, args.diagnostic, args.export, args.labels_csv_path
        )

    elif args.strategy == AGENTIC_MODEL:
        logger.info(f"[{AGENTIC_MODEL.upper()}] Using enhanced agentic model approach")
        results = pipeline_manager.run_agentic_analysis(
            bucket_name, args.max_videos, args.iterations,
            args.threshold, args.diagnostic, args.export, args.labels_csv_path
        )

    logger.info("[SUCCESS] Advanced pipeline analysis completed successfully!")


if __name__ == "__main__":
    main()
