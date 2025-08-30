#!/usr/bin/env python3
"""
Single video analysis script using only the data science module.

This script analyzes a specific video from the Google Cloud Storage bucket
using the Guardify-AI data science module directly.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from utils.env_utils import load_env_variables
load_env_variables()

from google_client.google_client import GoogleClient
from data_science.src.model.pipeline.shoplifting_analyzer import create_agentic_analyzer
from utils.logger_utils import create_logger

def analyze_single_video():
    """Analyze a single video from the bucket using data science module."""
    
    # Configuration for your specific video
    # Since the bucket IS "herzliya_shop", the video is directly in the bucket
    video_file = "Sweets 1_20250824150336.mp4"  # Just the filename
    bucket_name = "michal-only-bucket"  # The actual bucket name
    
    # Analysis parameters
    detection_threshold = 0.8
    iterations = 1
    
    # Setup logging
    logger = create_logger('SingleVideoAnalysis', 'single_video_analysis.log')
    
    logger.info("=" * 70)
    logger.info("🎬 SINGLE VIDEO ANALYSIS - DATA SCIENCE MODULE")
    logger.info("=" * 70)
    logger.info(f"📁 Video: {video_file}")
    logger.info(f"🪣 Bucket: {bucket_name}")
    logger.info(f"🎯 Threshold: {detection_threshold}")
    logger.info(f"🔄 Iterations: {iterations}")
    logger.info("=" * 70)
    
    try:
        # Initialize Google Client
        google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )
        
        # Create video URI - video is directly in the herzliya_shop bucket
        video_uri = f"gs://{bucket_name}/{video_file}"
        logger.info(f"🔗 Video URI: {video_uri}")
        
        # Create agentic analyzer (you can also use create_unified_analyzer)
        logger.info("🤖 Creating agentic analyzer...")
        shoplifting_analyzer = create_agentic_analyzer(
            detection_threshold=detection_threshold,
            logger=logger
        )
        
        # Analyze the video
        logger.info("🔍 Starting video analysis...")
        print(f"\n🔍 Analyzing video: {video_file}")
        print(f"🔗 Full URI: {video_uri}")
        print("⏱️  This may take a few minutes...")
        
        result = shoplifting_analyzer.analyze_video_from_bucket(
            video_uri=video_uri,
            iterations=iterations,
            pickle_analysis=True  # Save results for later review
        )
        
        # Display results
        logger.info("✅ Analysis completed!")
        print("\n" + "=" * 70)
        print("📊 ANALYSIS RESULTS")
        print("=" * 70)
        
        if result:
            print(f"🎬 Video: {video_file}")
            print(f"🚨 Shoplifting Detected: {result.get('final_detection', 'Unknown')}")
            print(f"📈 Confidence: {result.get('final_confidence', 0):.2%}")
            print(f"💭 Reasoning: {result.get('decision_reasoning', 'No reasoning provided')}")
            
            if 'iteration_results' in result:
                print(f"🔄 Iterations completed: {len(result['iteration_results'])}")
            
            # Log detailed results
            logger.info(f"Final Detection: {result.get('final_detection')}")
            logger.info(f"Final Confidence: {result.get('final_confidence')}")
            logger.info(f"Decision Reasoning: {result.get('decision_reasoning')}")
            
            if 'iteration_results' in result:
                for i, iteration in enumerate(result['iteration_results']):
                    logger.info(f"Iteration {i+1}: {iteration}")
        else:
            print("❌ No results returned")
            logger.error("Analysis returned no results")
            
        print("=" * 70)
        print(f"📝 Detailed logs saved to: single_video_analysis.log")
        
    except Exception as e:
        error_msg = f"❌ Analysis failed: {e}"
        print(f"\n{error_msg}")
        logger.error(error_msg)
        logger.exception("Full error details:")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = analyze_single_video()
    sys.exit(exit_code)