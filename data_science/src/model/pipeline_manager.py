from data_science.src.google.google_client import GoogleClient
from data_science.src.model.shoplifting_analyzer import ShopliftingAnalyzer
import pandas as pd
import datetime
import os
import logging
import numpy as np
from typing import List, Dict

from data_science.src.utils import UNIFIED_MODEL, AGENTIC_MODEL


class PipelineManager:
    """
    PIPELINE MANAGER FOR DUAL-STRATEGY SYSTEM
    ==================================================
    
    This manager handles both unified and agentic analysis strategies,
    providing flexible execution with comprehensive result comparison.
    Consolidates all pipeline management functionality in one place.
    """

    def __init__(self, google_client: GoogleClient, shoplifting_analyzer: ShopliftingAnalyzer,
                 logger: logging.Logger = None):
        """
        Initialize unified pipeline manager.
        
        Args:
            google_client (GoogleClient): Google Cloud client for video access
            shoplifting_analyzer (ShopliftingAnalyzer, optional): Legacy analyzer for compatibility
            logger (logging.Logger, optional): Logger instance
        """
        self.google_client = google_client
        self.shoplifting_analyzer = shoplifting_analyzer
        self.logger = logger

    def analyze_all_videos_in_bucket(self,
                                     bucket_name: str,
                                     export_results: bool = False,
                                     labels_csv_path: str = None):
        """
        Analyze all videos in a specified bucket and optionally export results to CSV.

        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket
            export_results (bool, optional): Whether to export results to CSV. Defaults to False.
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels for this bucket
        Returns:
            dict: Dictionary containing analysis results for each video
        """

        # Get video URIs and names
        uris, names = self.google_client.get_videos_uris_and_names_from_buckets(bucket_name)

        final_predictions = {}
        for uri, name in zip(uris, names):
            analysis = self.shoplifting_analyzer.analyze_video_from_bucket(uri, pickle_analysis=True)
            final_predictions[name] = analysis

        if export_results:
            self._export_results(final_predictions, labels_csv_path)

        return final_predictions

    def run_unified_analysis(self, bucket_name: str, max_videos: int, iterations: int, diagnostic: bool, export: bool,
                             labels_csv_path: str = None) -> List[Dict]:
        """
        Run unified analysis strategy.
        
        Args:
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels
            
        Returns:
            List[Dict]: Analysis results
        """
        self.logger.info("=== INITIALIZING UNIFIED STRATEGY ===")

        # Validate analyzer strategy
        if self.shoplifting_analyzer.strategy != UNIFIED_MODEL:
            raise ValueError("Analyzer must be configured for unified strategy")

        # Run analysis
        results = self._analyze_videos_with_strategy(
            self.shoplifting_analyzer, bucket_name, max_videos, iterations,
            diagnostic, export, UNIFIED_MODEL.upper(), labels_csv_path
        )

        self._log_strategy_summary(UNIFIED_MODEL.upper(), results)

        return results

    def run_agentic_analysis(self, bucket_name: str, max_videos: int, iterations: int, diagnostic: bool, export: bool,
                             labels_csv_path: str = None) -> List[Dict]:
        """
        Run agentic analysis strategy.
        
        Args:
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels
            
        Returns:
            List[Dict]: Analysis results
        """
        self.logger.info("=== INITIALIZING AGENTIC STRATEGY ===")

        # Validate analyzer strategy
        if self.shoplifting_analyzer.strategy != AGENTIC_MODEL:
            raise ValueError("Analyzer must be configured for agentic strategy")

        # Run analysis
        results = self._analyze_videos_with_strategy(
            self.shoplifting_analyzer, bucket_name, max_videos, iterations,
            diagnostic, export, AGENTIC_MODEL.upper(), labels_csv_path
        )

        self._log_strategy_summary(AGENTIC_MODEL.upper(), results)
        return results

    def _analyze_videos_with_strategy(self, analyzer, bucket_name: str, max_videos: int,
                                      iterations: int, diagnostic: bool, export: bool,
                                      strategy_name: str, labels_csv_path: str = None) -> List[Dict]:
        """
        Core analysis engine that works with any analyzer strategy.

        Args:
            analyzer: The analyzer instance (unified or agentic)
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            strategy_name (str): Name of the strategy for logging
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels

        Returns:
            List[Dict]: Analysis results
        """
        # Determine analysis parameters based on mode
        mode_label = "DIAGNOSTIC" if diagnostic else "FULL"
        video_limit_text = f"first {max_videos}" if max_videos else "all"

        self.logger.info(
            f"[{mode_label}] Starting {strategy_name.lower()} analysis of {video_limit_text} videos in bucket: {bucket_name}")

        # Get list of video files from bucket
        video_uris = self._get_video_uris_from_bucket(bucket_name)

        if not video_uris:
            self.logger.warning("[WARNING] No video files found in bucket")
            return []

        # Determine videos to process
        if max_videos is not None:
            videos_to_process = video_uris[:max_videos]
            self.logger.info(f"[ANALYZING] {len(videos_to_process)} videos (limited from {len(video_uris)} total)")
        else:
            videos_to_process = video_uris
            self.logger.info(f"[ANALYZING] All {len(videos_to_process)} videos")

        # Process videos
        all_results = []
        successful_analyses = 0
        failed_analyses = 0

        for i, video_uri in enumerate(videos_to_process, 1):
            progress_label = f"[VIDEO {i}/{len(videos_to_process)}]" if diagnostic else f"[PROCESSING] Video {i}/{len(videos_to_process)}"
            self.logger.info(f"{progress_label} {video_uri}")

            try:
                # Call appropriate analysis method - both strategies now use iterations
                result = analyzer.analyze_video_from_bucket(
                    video_uri,
                    iterations=iterations,
                    pickle_analysis=diagnostic
                )

                all_results.append(result)
                successful_analyses += 1

                # Enhanced logging
                if diagnostic:
                    self._log_diagnostic_details(result, video_uri, strategy_name)
                else:
                    final_detection = result.get('final_detection', False)
                    final_confidence = result.get('final_confidence', 0.0)
                    self.logger.info(f"  [RESULT] detected={final_detection}, confidence={final_confidence:.3f}")

            except Exception as e:
                self.logger.error(f"[ERROR] Failed to analyze {video_uri}: {e}")
                failed_analyses += 1

                error_result = {
                    "video_identifier": video_uri,
                    "error": str(e),
                    "final_detection": False,
                    "final_confidence": 0.0,
                    "analysis_approach": f"{strategy_name}_ENHANCED"
                }
                all_results.append(error_result)

        # Generate summary
        if diagnostic:
            self._log_diagnostic_summary(all_results, mode_label, strategy_name)
        else:
            self._log_full_analysis_summary(all_results, successful_analyses, failed_analyses, len(video_uris),
                                            strategy_name)

        # Export results if requested
        if export and all_results:
            self._export_strategy_results(all_results, strategy_name, labels_csv_path)

        return all_results

    # ===== UTILITY METHODS =====

    def _get_video_uris_from_bucket(self, bucket_name: str) -> List[str]:
        """Get list of video URIs from GCS bucket using existing GoogleClient authentication."""
        try:
            storage_client = self.google_client.storage_client
            bucket = storage_client.bucket(bucket_name)

            video_extensions = {'.mp4', '.avi'}
            video_uris = []

            self.logger.info(f"Listing blobs in bucket: {bucket_name}")

            for blob in bucket.list_blobs():
                if any(blob.name.lower().endswith(ext) for ext in video_extensions):
                    video_uri = f"gs://{bucket_name}/{blob.name}"
                    video_uris.append(video_uri)
                    if self.logger:
                        self.logger.debug(f"Found video: {video_uri}")

            if self.logger:
                self.logger.info(f"Found {len(video_uris)} video files")
            return video_uris

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to list videos from bucket: {e}")
            return []

    def _log_diagnostic_details(self, result: Dict, video_uri: str, strategy_name: str):
        """Log detailed information for diagnostic mode"""
        final_detection = result.get('final_detection', False)
        final_confidence = result.get('final_confidence', 0.0)
        confidences = result.get('confidence_levels', [])

        self.logger.info(f"[{strategy_name} SUMMARY] {video_uri}:")
        self.logger.info(f"  Final: detected={final_detection}, confidence={final_confidence:.3f}")
        self.logger.info(f"  All confidences: {confidences}")
        self.logger.info(f"  Decision reasoning: {result.get('decision_reasoning', 'N/A')}")

        # Log strategy-specific details
        if strategy_name == AGENTIC_MODEL.upper():
            cv_summary = result.get('cv_observations_summary', {})
            if cv_summary and 'behavioral_tone' in cv_summary:
                self.logger.info(f"  CV behavioral tone: {cv_summary['behavioral_tone']}")
                self.logger.info(f"  CV suspicious indicators: {cv_summary.get('suspicious_indicators', 0)}")

    def _log_diagnostic_summary(self, results: List[Dict], mode_label: str, strategy_name: str):
        """Generate diagnostic summary with detailed analysis"""
        valid_results = [r for r in results if 'error' not in r]
        detection_count = sum(1 for r in valid_results if r.get('final_detection', False))

        self.logger.info(f"[{strategy_name} {mode_label} COMPLETE] Summary:")
        self.logger.info(f"  Videos analyzed: {len(results)}")
        self.logger.info(f"  Detections: {detection_count}/{len(valid_results)}")

        if valid_results:
            avg_confidence = np.mean([r.get('final_confidence', 0.0) for r in valid_results])
            self.logger.info(f"  Average confidence: {avg_confidence:.3f}")

    def _log_full_analysis_summary(self, results: List[Dict], successful: int, failed: int, total_videos: int,
                                   strategy_name: str):
        """Generate summary for full analysis mode"""
        valid_results = [r for r in results if 'error' not in r]
        detection_count = sum(1 for r in valid_results if r.get('final_detection', False))

        self.logger.info(f"[{strategy_name} SUMMARY] Analysis Complete:")
        self.logger.info(f"  Total videos: {total_videos}")
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Failed: {failed}")
        self.logger.info(f"  Shoplifting detected: {detection_count}/{len(valid_results)}")

    def _log_strategy_summary(self, strategy_name: str, results: List[Dict]):
        """Log high-level strategy summary"""
        valid_results = [r for r in results if 'error' not in r]
        detection_count = sum(1 for r in valid_results if r.get('final_detection', False))

        self.logger.info(
            f"[{strategy_name} SUMMARY] Videos: {len(results)}, Detections: {detection_count}, Avg Confidence: {np.mean([r.get('final_confidence', 0.0) for r in valid_results]):.3f}")

    # ===== EXPORT METHODS =====

    def _export_strategy_results(self, results: List[Dict], strategy_name: str, labels_csv_path: str = None):
        """
        Export strategy-specific analysis results to CSV with optional ground truth comparison.
        
        Args:
            results (List[Dict]): Analysis results from strategy
            strategy_name (str): Name of the strategy (UNIFIED/AGENTIC)
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels
        """
        try:
            # Convert results to the format expected by _export_results
            final_predictions = {}

            for result in results:
                # Extract video name from identifier (remove gs://bucket/ prefix)
                video_identifier = result.get('video_identifier', '')
                if '/' in video_identifier:
                    video_name = video_identifier.split('/')[-1]
                else:
                    video_name = video_identifier

                # Remove file extension for comparison with labels
                video_name_without_ext = os.path.splitext(video_name)[0]

                # Create analysis dict in legacy format for compatibility
                analysis = {
                    'video_identifier': video_identifier,
                    'shoplifting_determination': result.get('final_detection', False),
                    'final_confidence': result.get('final_confidence', 0.0),
                    'analysis_approach': result.get('analysis_approach', f'{strategy_name}_ENHANCED'),
                    'decision_reasoning': result.get('decision_reasoning', ''),
                    'iterations': result.get('iterations', 0),
                    'detection_threshold': result.get('detection_threshold', 0.45),
                    'error': result.get('error', ''),
                    'analysis_timestamp': result.get('analysis_timestamp', '')
                }

                # Add strategy-specific data
                if strategy_name == AGENTIC_MODEL.upper():
                    if 'cv_observations_summary' in result:
                        cv_summary = result['cv_observations_summary']
                        analysis['cv_behavioral_tone'] = cv_summary.get('behavioral_tone', '')
                        analysis['cv_suspicious_indicators'] = cv_summary.get('suspicious_indicators', 0)
                        analysis['cv_normal_indicators'] = cv_summary.get('normal_indicators', 0)

                    if 'analysis_summary' in result:
                        analysis_summary = result['analysis_summary']
                        analysis['most_common_evidence_tier'] = analysis_summary.get('most_common_tier', '')
                        analysis['has_concealment_evidence'] = analysis_summary.get('has_concealment_evidence', False)

                final_predictions[video_name_without_ext] = analysis

            self._export_results(final_predictions, labels_csv_path)

        except Exception as e:
            self.logger.error(f"Failed to export {strategy_name} results: {e}")

    def _export_results(self, final_predictions: dict, labels_csv_path: str = None) -> str:
        """
        Export analysis results to a CSV file.

        Args:
            final_predictions (dict): Dictionary containing analysis results for each video
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels for this bucket

        Returns:
            str: Path to the exported CSV file
        """
        # Create DataFrame from results
        results_data = []
        for name, analysis in final_predictions.items():
            results_data.append({
                'video_identifier': analysis['video_identifier'],
                'video_name': name,
                'shoplifting_determination': analysis['shoplifting_determination']
            })

        df = pd.DataFrame(results_data)
        match_percentage = None

        # Compare with labels if provided
        if labels_csv_path:
            df, match_percentage = self._compare_with_labels(df, labels_csv_path)

        # Create timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"shoplifting_analysis_{timestamp}.csv"

        # Create results directory if it doesn't exist
        results_dir = "analysis_results"
        os.makedirs(results_dir, exist_ok=True)

        # Save to CSV
        csv_path = os.path.join(results_dir, csv_filename)

        # Write the main results
        df.to_csv(csv_path, index=False)

        # Append match percentage if available
        if match_percentage is not None:
            with open(csv_path, 'a') as f:
                f.write(f"\nOverall match percentage: {match_percentage:.2f}%")

        return csv_path

    def _compare_with_labels(self, df: pd.DataFrame, labels_csv_path: str) -> tuple[pd.DataFrame, float]:
        """
        Compare predictions with ground truth labels and calculate match percentage.

        Args:
            df (pd.DataFrame): DataFrame containing predictions
            labels_csv_path (str): Path to CSV file containing ground truth labels

        Returns:
            tuple[pd.DataFrame, float]: Updated DataFrame with correctness column and match percentage
        """
        original_df = df.copy()
        
        # Initialize prediction_correct column with False by default
        df['prediction_correct'] = False
        
        try:
            labels_df = pd.read_csv(labels_csv_path)
            required_columns = ['video_name', 'shoplifting_determination']

            if not all(col in labels_df.columns for col in required_columns):
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"Labels file missing required columns: {required_columns}")
                return df, None

            # Remove file extensions from both dataframes for consistent comparison
            df['video_name_clean'] = df['video_name'].apply(lambda x: os.path.splitext(x)[0])
            labels_df['video_name_clean'] = labels_df['video_name'].apply(lambda x: os.path.splitext(x)[0])

            # Merge predictions with labels using left join to keep all predictions
            merged_df = pd.merge(
                df,
                labels_df[['video_name_clean', 'shoplifting_determination']],
                on='video_name_clean',
                how='left',
                suffixes=('_predicted', '_actual')
            )

            # Remove video_name_clean column as it's no longer needed
            merged_df = merged_df.drop(columns=['video_name_clean'])

            # Handle null predictions - set them to False for comparison
            merged_df['shoplifting_determination_predicted'] = merged_df['shoplifting_determination_predicted'].fillna(False)
            
            # Calculate correctness only for videos that have labels (not null)
            has_labels = merged_df['shoplifting_determination_actual'].notna()
            
            # Initialize prediction_correct to False for all rows
            merged_df['prediction_correct'] = False
            
            # Set prediction_correct to True where predictions match labels
            if has_labels.sum() > 0:
                merged_df.loc[has_labels, 'prediction_correct'] = (
                    merged_df.loc[has_labels, 'shoplifting_determination_actual'] == 
                    merged_df.loc[has_labels, 'shoplifting_determination_predicted']
                )
                
                # Calculate match percentage only for videos with labels
                match_percentage = (merged_df.loc[has_labels, 'prediction_correct']).mean() * 100
                
                if hasattr(self, 'logger') and self.logger:
                    correct_count = merged_df.loc[has_labels, 'prediction_correct'].sum()
                    total_with_labels = has_labels.sum()
                    self.logger.info(f"Ground truth comparison: {total_with_labels} videos have labels")
                    self.logger.info(f"Match percentage: {match_percentage:.2f}%")
                
                # Remove shoplifting_determination_actual column as it's no longer needed
                merged_df = merged_df.drop(columns=['shoplifting_determination_actual'])
                
                # Return the merged dataframe with the prediction_correct column
                return merged_df, match_percentage
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning("No videos found with matching ground truth labels")
                
                # Remove shoplifting_determination_actual column as it's no longer needed
                merged_df = merged_df.drop(columns=['shoplifting_determination_actual'])
                
                return merged_df, None
                
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Error comparing with labels: {str(e)}")
            # Ensure prediction_correct column exists even if comparison fails
            df['prediction_correct'] = False
        
        return df, None
