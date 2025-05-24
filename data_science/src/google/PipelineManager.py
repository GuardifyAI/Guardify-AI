from GoogleClient import GoogleClient
from ShopliftingAnalyzer import ShopliftingAnalyzer
import pandas as pd
import datetime
import os
import logging
import numpy as np
from typing import List, Dict, Any

class PipelineManager:
    """
    UNIFIED PIPELINE MANAGER FOR DUAL-STRATEGY SYSTEM
    ==================================================
    
    This manager handles both unified and hybrid analysis strategies,
    providing flexible execution with comprehensive result comparison.
    Consolidates all pipeline management functionality in one place.
    """
    
    MAX_API_CALLS = 2

    def __init__(self, google_client: GoogleClient, shoplifting_analyzer: ShopliftingAnalyzer = None, logger: logging.Logger = None):
        """
        Initialize unified pipeline manager.
        
        Args:
            google_client (GoogleClient): Google Cloud client for video access
            shoplifting_analyzer (ShopliftingAnalyzer, optional): Legacy analyzer for compatibility
            logger (logging.Logger, optional): Logger instance
        """
        self.google_client = google_client
        self.shoplifting_analyzer = shoplifting_analyzer  # For backward compatibility
        self.logger = logger

    # ===== LEGACY COMPATIBILITY METHOD =====
    def analyze_all_videos_in_bucket(self, bucket_name: str, max_api_calls_per_video: int = None, export_results: bool = False):
        """
        Legacy method for backward compatibility.
        Analyze all videos in a specified bucket and optionally export results to CSV.
        """
        max_api_calls_per_video = max_api_calls_per_video or self.MAX_API_CALLS
        # Get video URIs and names
        uris, names = self.google_client.get_videos_uris_and_names_from_buckets(bucket_name)

        final_predictions = {}
        for uri, name in zip(uris, names):
            analysis = self.shoplifting_analyzer.analyze_video_from_bucket(uri,
                                                                           max_api_calls=max_api_calls_per_video,
                                                                           pickle_analysis=True)
            final_predictions[name] = analysis

        if export_results:
            self._export_results(final_predictions)

        return final_predictions

    # ===== ADVANCED PIPELINE MANAGEMENT =====
    
    def run_unified_analysis(self, bucket_name: str, max_videos: int, iterations: int, 
                           threshold: float, diagnostic: bool, export: bool) -> List[Dict]:
        """
        Run unified analysis strategy.
        
        Args:
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            threshold (float): Detection confidence threshold
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            
        Returns:
            List[Dict]: Analysis results
        """
        self.logger.info("=== INITIALIZING UNIFIED STRATEGY ===")
        
        # Use consolidated ShopliftingAnalyzer with unified strategy
        unified_analyzer = ShopliftingAnalyzer.create_unified_analyzer(
            detection_threshold=threshold,
            logger=self.logger
        )
        
        # Run analysis
        results = self._analyze_videos_with_strategy(
            unified_analyzer, bucket_name, max_videos, iterations, 
            diagnostic, export, "UNIFIED"
        )
        
        self._log_strategy_summary("UNIFIED", results)
        return results
    
    def run_hybrid_analysis(self, bucket_name: str, max_videos: int, iterations: int,
                          threshold: float, diagnostic: bool, export: bool) -> List[Dict]:
        """
        Run hybrid analysis strategy.
        
        Args:
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            threshold (float): Detection confidence threshold
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            
        Returns:
            List[Dict]: Analysis results
        """
        self.logger.info("=== INITIALIZING HYBRID STRATEGY ===")
        
        # Create hybrid analyzer directly in ShopliftingAnalyzer
        hybrid_analyzer = ShopliftingAnalyzer.create_hybrid_analyzer(
            detection_threshold=threshold,
            logger=self.logger
        )
        
        # Run analysis
        results = self._analyze_videos_with_strategy(
            hybrid_analyzer, bucket_name, max_videos, iterations, 
            diagnostic, export, "HYBRID"
        )
        
        self._log_strategy_summary("HYBRID", results)
        return results
    
    def run_comparative_analysis(self, bucket_name: str, max_videos: int, iterations: int,
                               threshold: float, diagnostic: bool, export: bool) -> Dict:
        """
        Run both strategies for comparative analysis.
        
        Args:
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            threshold (float): Detection confidence threshold
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            
        Returns:
            Dict: Comparative analysis results
        """
        self.logger.info("=== RUNNING COMPARATIVE ANALYSIS ===")
        
        # Run unified analysis
        self.logger.info("--- Running Unified Analysis ---")
        unified_results = self.run_unified_analysis(
            bucket_name, max_videos, iterations, threshold, diagnostic, False
        )
        
        # Run hybrid analysis
        self.logger.info("--- Running Hybrid Analysis ---")
        hybrid_results = self.run_hybrid_analysis(
            bucket_name, max_videos, iterations, threshold, diagnostic, False
        )
        
        # Compare results
        comparison = self._compare_strategies(unified_results, hybrid_results)
        
        # Export comparison if requested
        if export:
            self._export_comparative_results(unified_results, hybrid_results, comparison)
        
        return {
            "unified_results": unified_results,
            "hybrid_results": hybrid_results,
            "comparison": comparison
        }

    # ===== CORE ANALYSIS ENGINE =====
    
    def _analyze_videos_with_strategy(self, analyzer, bucket_name: str, max_videos: int, 
                                    iterations: int, diagnostic: bool, export: bool, 
                                    strategy_name: str) -> List[Dict]:
        """
        Core analysis engine that works with any analyzer strategy.

        Args:
            analyzer: The analyzer instance (unified or hybrid)
            bucket_name (str): GCS bucket containing videos
            max_videos (int): Maximum number of videos to analyze
            iterations (int): Number of analysis iterations
            diagnostic (bool): Enable diagnostic mode
            export (bool): Export results to CSV
            strategy_name (str): Name of the strategy for logging

        Returns:
            List[Dict]: Analysis results
        """
        # Determine analysis parameters based on mode
        mode_label = "DIAGNOSTIC" if diagnostic else "FULL"
        video_limit_text = f"first {max_videos}" if max_videos else "all"
        
        self.logger.info(f"[{mode_label}] Starting {strategy_name.lower()} analysis of {video_limit_text} videos in bucket: {bucket_name}")
        
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
            self._log_full_analysis_summary(all_results, successful_analyses, failed_analyses, len(video_uris), strategy_name)
        
        # Export results if requested
        if export and all_results:
            self._export_strategy_results(all_results, strategy_name)
        
        return all_results

    # ===== COMPARISON AND ANALYSIS =====
    
    def _compare_strategies(self, unified_results: List[Dict], hybrid_results: List[Dict]) -> Dict:
        """
        Compare results between unified and hybrid strategies.
        """
        self.logger.info("=== STRATEGY COMPARISON ANALYSIS ===")
        
        # Create video-based comparison
        comparison = {
            "total_videos": len(unified_results),
            "agreement_analysis": {},
            "performance_comparison": {},
            "confidence_analysis": {},
            "detailed_comparisons": []
        }
        
        agreements = 0
        disagreements = 0
        unified_detections = 0
        hybrid_detections = 0
        
        unified_confidences = []
        hybrid_confidences = []
        
        for i, (unified, hybrid) in enumerate(zip(unified_results, hybrid_results)):
            # Skip error results
            if 'error' in unified or 'error' in hybrid:
                continue
                
            unified_detected = unified.get('final_detection', False)
            hybrid_detected = hybrid.get('final_detection', False)
            unified_conf = unified.get('final_confidence', 0.0)
            hybrid_conf = hybrid.get('final_confidence', 0.0)
            
            unified_confidences.append(unified_conf)
            hybrid_confidences.append(hybrid_conf)
            
            if unified_detected:
                unified_detections += 1
            if hybrid_detected:
                hybrid_detections += 1
                
            if unified_detected == hybrid_detected:
                agreements += 1
                agreement_type = "agree_detected" if unified_detected else "agree_normal"
            else:
                disagreements += 1
                agreement_type = "disagree"
                
            # Detailed comparison for each video
            video_comparison = {
                "video": unified.get('video_identifier', f'video_{i}'),
                "unified_detected": unified_detected,
                "hybrid_detected": hybrid_detected,
                "unified_confidence": unified_conf,
                "hybrid_confidence": hybrid_conf,
                "confidence_diff": abs(unified_conf - hybrid_conf),
                "agreement": agreement_type
            }
            comparison["detailed_comparisons"].append(video_comparison)
        
        # Agreement analysis
        total_valid = agreements + disagreements
        comparison["agreement_analysis"] = {
            "total_agreements": agreements,
            "total_disagreements": disagreements,
            "agreement_rate": agreements / total_valid if total_valid > 0 else 0,
            "disagreement_rate": disagreements / total_valid if total_valid > 0 else 0
        }
        
        # Performance comparison
        comparison["performance_comparison"] = {
            "unified_detection_rate": unified_detections / total_valid if total_valid > 0 else 0,
            "hybrid_detection_rate": hybrid_detections / total_valid if total_valid > 0 else 0,
            "unified_total_detections": unified_detections,
            "hybrid_total_detections": hybrid_detections
        }
        
        # Confidence analysis
        if unified_confidences and hybrid_confidences:
            comparison["confidence_analysis"] = {
                "unified_avg_confidence": np.mean(unified_confidences),
                "hybrid_avg_confidence": np.mean(hybrid_confidences),
                "unified_confidence_std": np.std(unified_confidences),
                "hybrid_confidence_std": np.std(hybrid_confidences),
                "avg_confidence_difference": np.mean([abs(u - h) for u, h in zip(unified_confidences, hybrid_confidences)])
            }
        
        # Log comparison summary
        self.logger.info(f"Strategy Agreement Rate: {comparison['agreement_analysis']['agreement_rate']:.1%}")
        self.logger.info(f"Unified Detection Rate: {comparison['performance_comparison']['unified_detection_rate']:.1%}")
        self.logger.info(f"Hybrid Detection Rate: {comparison['performance_comparison']['hybrid_detection_rate']:.1%}")
        
        return comparison

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
        if strategy_name == "HYBRID":
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
    
    def _log_full_analysis_summary(self, results: List[Dict], successful: int, failed: int, total_videos: int, strategy_name: str):
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
        
        self.logger.info(f"[{strategy_name} SUMMARY] Videos: {len(results)}, Detections: {detection_count}, Avg Confidence: {np.mean([r.get('final_confidence', 0.0) for r in valid_results]):.3f}")

    # ===== EXPORT METHODS =====
    
    def _export_results(self, final_predictions: dict) -> str:
        """
        Legacy export method for backward compatibility.
        Export analysis results to a CSV file.
        """
        # Create DataFrame from results
        results_data = []
        for name, analysis in final_predictions.items():
            results_data.append({
                'video_uri': analysis['video_identifier'],
                'video_name': name,
                'shoplifting_determination': analysis['shoplifting_determination']
            })

        df = pd.DataFrame(results_data)

        # Create timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"shoplifting_analysis_{timestamp}.csv"

        # Create results directory if it doesn't exist
        results_dir = "analysis_results"
        os.makedirs(results_dir, exist_ok=True)

        # Save to CSV
        csv_path = os.path.join(results_dir, csv_filename)
        df.to_csv(csv_path, index=False)

        return csv_path
    
    def _export_strategy_results(self, results: List[Dict], strategy_name: str):
        """Export strategy-specific analysis results to CSV."""
        try:
            export_data = []
            for result in results:
                row = {
                    'video_identifier': result.get('video_identifier', ''),
                    'analysis_approach': result.get('analysis_approach', f'{strategy_name}_ENHANCED'),
                    'final_detection': result.get('final_detection', False),
                    'final_confidence': result.get('final_confidence', 0.0),
                    'decision_reasoning': result.get('decision_reasoning', ''),
                    'iterations': result.get('iterations', 0),
                    'detection_threshold': result.get('detection_threshold', 0.45),
                    'error': result.get('error', ''),
                    'analysis_timestamp': result.get('analysis_timestamp', '')
                }
                
                # Add strategy-specific data
                if strategy_name == "HYBRID":
                    if 'cv_observations_summary' in result:
                        cv_summary = result['cv_observations_summary']
                        row['cv_behavioral_tone'] = cv_summary.get('behavioral_tone', '')
                        row['cv_suspicious_indicators'] = cv_summary.get('suspicious_indicators', 0)
                        row['cv_normal_indicators'] = cv_summary.get('normal_indicators', 0)
                    
                    if 'analysis_summary' in result:
                        analysis_summary = result['analysis_summary']
                        row['most_common_evidence_tier'] = analysis_summary.get('most_common_tier', '')
                        row['has_concealment_evidence'] = analysis_summary.get('has_concealment_evidence', False)
                
                export_data.append(row)
            
            df = pd.DataFrame(export_data)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_filename = f"{strategy_name.lower()}_shoplifting_results_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)
            self.logger.info(f"📄 {strategy_name} results exported to: {csv_filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to export {strategy_name} results: {e}")
    
    def _export_comparative_results(self, unified_results: List[Dict], 
                                  hybrid_results: List[Dict], comparison: Dict):
        """
        Export comparative analysis results to CSV.
        """
        try:
            # Create comparison DataFrame
            comparison_data = []
            
            for detail in comparison["detailed_comparisons"]:
                comparison_data.append({
                    'video': detail['video'],
                    'unified_detected': detail['unified_detected'],
                    'hybrid_detected': detail['hybrid_detected'],
                    'unified_confidence': detail['unified_confidence'],
                    'hybrid_confidence': detail['hybrid_confidence'],
                    'confidence_difference': detail['confidence_diff'],
                    'strategies_agree': detail['agreement'] != "disagree",
                    'agreement_type': detail['agreement']
                })
            
            df = pd.DataFrame(comparison_data)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_filename = f"strategy_comparison_{timestamp}.csv"
            
            df.to_csv(csv_filename, index=False)
            self.logger.info(f"📄 Comparative results exported to: {csv_filename}")
            
            # Log summary statistics
            agreement_rate = comparison["agreement_analysis"]["agreement_rate"]
            unified_detection_rate = comparison["performance_comparison"]["unified_detection_rate"]
            hybrid_detection_rate = comparison["performance_comparison"]["hybrid_detection_rate"]
            
            self.logger.info(f"📈 Comparison Summary:")
            self.logger.info(f"  Agreement Rate: {agreement_rate:.1%}")
            self.logger.info(f"  Unified Detection Rate: {unified_detection_rate:.1%}")
            self.logger.info(f"  Hybrid Detection Rate: {hybrid_detection_rate:.1%}")
            
        except Exception as e:
            self.logger.error(f"Failed to export comparative results: {e}")
