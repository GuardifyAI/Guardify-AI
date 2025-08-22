from data_science.src.model.agentic.analysis_model import AnalysisModel
from data_science.src.model.agentic.computer_vision_model import ComputerVisionModel
from data_science.src.model.unified.unified_shoplifting_model import UnifiedShopliftingModel
import logging
from data_science.src.utils import get_video_extension, AGENTIC_MODEL, UNIFIED_MODEL
import os
from vertexai.generative_models import Part
from typing import List, Dict, Any
from utils import create_logger

import numpy as np
import pickle
import datetime


def create_unified_analyzer(detection_threshold: float, logger: logging.Logger = None):
    """
    Factory function to create a unified strategy analyzer.

    Args:
        detection_threshold (float): Detection confidence threshold
        logger (logging.Logger, optional): Logger instance

    Returns:
        ShopliftingAnalyzer: Configured for unified strategy
    """
    # Create the unified model instance
    unified_model = UnifiedShopliftingModel()

    return ShopliftingAnalyzer(
        detection_strictness=detection_threshold,
        logger=logger,
        strategy=UNIFIED_MODEL,
        unified_model=unified_model
    )


def create_agentic_analyzer(detection_threshold: float, logger: logging.Logger = None):
    """
    Factory function to create an agentic strategy analyzer.

    Args:
        detection_threshold (float): Detection confidence threshold
        logger (logging.Logger, optional): Logger instance

    Returns:
        ShopliftingAnalyzer: Configured for agentic strategy
    """
    # Create the required model instances for agentic strategy
    cv_model = ComputerVisionModel()
    analysis_model = AnalysisModel()

    return ShopliftingAnalyzer(
        detection_strictness=detection_threshold,
        logger=logger,
        strategy=AGENTIC_MODEL,
        cv_model=cv_model,
        analysis_model=analysis_model
    )


class ShopliftingAnalyzer:
    """
    UNIFIED SHOPLIFTING ANALYZER WITH DUAL-STRATEGY SUPPORT
    =======================================================

    This analyzer supports both:
    1. SINGLE STRATEGY: True single-model direct analysis using UnifiedShopliftingModel
    2. AGENTIC STRATEGY: Two-step enhanced pipeline (ComputerVisionModel → AnalysisModel)

    Eliminates code duplication by consolidating video processing, validation,
    statistical analysis, and file operations into shared methods.
    """

    # ===== SHARED CONSTANTS =====
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi'}

    VIDEO_MIME_TYPES = {
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
    }

    # Consolidated behavioral indicators
    THEFT_INDICATORS = [
        'pocket', 'bag', 'waist', 'concealed', 'hidden', 'tucked',
        'clothing adjustment', 'hand movement', 'body area', 'conceal',
        'nervous', 'furtive', 'quick', 'suspicious', 'concealment'
    ]

    NORMAL_INDICATORS = [
        'browsing', 'examining', 'looking', 'normal', 'casual',
        'no clear', 'no visible', 'ambiguous', 'consistent with normal',
        'returned', 'shelf', 'checkout', 'natural', 'regular'
    ]

    ANALYSIS_DICT = {
        "video_identifier": str(),
        "analysis_approach": str(),
        "iterations": int(),
        "final_detection": bool(),
        "final_confidence": float(),
        "decision_reasoning": str(),
        "confidence_levels": list(),
        "detection_results": list(),
        "iteration_results": list(),
        "analysis_timestamp": str()
    }

    def __init__(self, detection_strictness: float, strategy: str = UNIFIED_MODEL,
                 unified_model: UnifiedShopliftingModel = None, cv_model: ComputerVisionModel = None,
                 analysis_model: AnalysisModel = None, logger: logging.Logger = None):
        """
        Initialize the ShopliftingAnalyzer with support for both unified and agentic strategies.

        Args:
            detection_strictness (float): Confidence threshold (0-1) for shoplifting detection
            strategy (str): "unified" or AGENTIC_MODEL analysis strategy
            unified_model (UnifiedShopliftingModel, optional): Unified model for video analysis
            cv_model (ComputerVisionModel, optional): Computer vision model for video analysis
            analysis_model (AnalysisModel, optional): Analysis model for interpreting observations
            logger (logging.Logger, optional): Logger instance
        """
        self.strategy = strategy

        # Initialize models based on strategy
        if strategy == UNIFIED_MODEL:
            self.unified_model = unified_model
        else:
            # Agentic strategy uses separate models
            self.cv_model = cv_model
            self.analysis_model = analysis_model

        # Validation
        if detection_strictness < 0 or detection_strictness > 1:
            raise ValueError("Detection strictness must be between 0 and 1.")
        if self.strategy == AGENTIC_MODEL:
            if (not hasattr(self, 'cv_model') or not self.cv_model or not hasattr(self, 'analysis_model')
                    or not self.analysis_model):
                raise ValueError("Agentic analysis requires both CV and Analysis models")
        elif self.strategy == UNIFIED_MODEL:
            if not hasattr(self, 'unified_model') or not self.unified_model:
                raise ValueError("Unified analysis requires UnifiedShopliftingModel")

        self.shoplifting_detection_threshold = detection_strictness

        # Initialize logger
        if logger is None:
            strategy_suffix = f"_{strategy}" if strategy != UNIFIED_MODEL else ""
            self.logger = create_logger(f'ShopliftingAnalyzer{strategy_suffix}', f'{strategy}_analysis.log')
        else:
            self.logger = logger

        # Set logger on analysis model for enhanced debugging (agentic only)
        if hasattr(self, 'analysis_model') and self.analysis_model and hasattr(self.analysis_model, 'logger'):
            self.analysis_model.logger = self.logger

        # State tracking for unified strategy
        self.current_confidence_levels = []
        self.current_shoplifting_detected_results = []

        self.logger.info(
            f"Initialized ShopliftingAnalyzer with {strategy.upper()} strategy, threshold: {detection_strictness}")

    # ===== SHARED VIDEO PROCESSING METHODS =====

    def _validate_video_format(self, video_identifier: str) -> str:
        """
        Shared method to validate video format and return extension.

        Args:
            video_identifier (str): Video path or URI

        Returns:
            str: Validated file extension
            
        Raises:
            ValueError: If video format is unsupported
        """
        extension = get_video_extension(video_identifier)
        if extension not in self.ALLOWED_VIDEO_EXTENSIONS:
            raise ValueError(
                f"'{extension}' is an unsupported video format. Supported formats are: {self.ALLOWED_VIDEO_EXTENSIONS}")
        return extension

    def analyze_video_from_bucket(self,
                                  video_uri: str,
                                  iterations: int = 3,
                                  pickle_analysis: bool = True) -> Dict:
        """
        Analyze video from GCS bucket using current strategy.

        Args:
            video_uri (str): GCS URI of the video
            iterations (int): Number of iterations (Default: 3)
            pickle_analysis (bool): Whether to save analysis results (Default: True)

        Returns:
            Dict: Analysis results
        """
        try:
            extension = self._validate_video_format(video_uri)
            video_part = Part.from_uri(uri=video_uri, mime_type=self.VIDEO_MIME_TYPES[extension])
            return self._analyze_video(video_uri, video_part, iterations, pickle_analysis)

        except Exception as e:
            self.logger.error(f"Failed to analyze {video_uri}: {e}")
            return self._create_error_result(video_uri, str(e))

    def analyze_local_video(self,
                            video_path: str,
                            iterations: int,
                            pickle_analysis: bool = True) -> Dict:
        """
        Analyze local video file using current strategy.

        Args:
            video_path (str): Path to local video file
            iterations (int): Number of iterations
            pickle_analysis (bool): Whether to save analysis results

        Returns:
            Dict: Analysis results
        """
        # Validate file existence
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found at path: {video_path}")
            return self.ANALYSIS_DICT

        try:
            # Validate video format
            extension = self._validate_video_format(video_path)
            video_part = Part.from_data(mime_type=self.VIDEO_MIME_TYPES[extension], data=open(video_path, "rb").read())
            return self._analyze_video(video_path, video_part, iterations, pickle_analysis)

        except Exception as e:
            self.logger.error(f"Failed to analyze {video_path}: {e}")
            return self._create_error_result(video_path, str(e))

    def _analyze_video(self, video_path: str, video_part: Part, iterations: int, pickle_analysis: bool = True):
        """
        Analyze video file by strategy.

        Args:
            video_path (str): Path to local video file
            video_part (Part): Video part
            iterations (int): Number of iterations (agentic strategy)
            pickle_analysis (bool): Whether to save analysis results

        Returns:
            Dict: Analysis results
        """
        # Route to appropriate analysis method
        if self.strategy == AGENTIC_MODEL:
            return self.analyze_video_agentic(video_part, video_path, iterations, pickle_analysis)
        else:
            return self.analyze_video_unified(video_part, video_path, iterations, pickle_analysis)

    def _create_error_result(self, video_identifier: str, error_message: str) -> Dict:
        """
        Create standardized error result dictionary.

        Args:
            video_identifier (str): Video identifier
            error_message (str): Error description

        Returns:
            Dict: Standardized error result
        """
        return {
            "video_identifier": video_identifier,
            "error": error_message,
            "final_detection": None,
            "final_confidence": 0.0,
            "analysis_approach": self.strategy.upper(),
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }

    # ===== UNIFIED STRATEGY METHODS (TRUE SINGLE MODEL) =====

    def analyze_video_unified(self, video_part: Part, video_identifier: str, iterations: int,
                              pickle_analysis: bool = True) -> Dict:
        """
        TRUE UNIFIED strategy analysis method using UnifiedShopliftingModel.

        Args:
            video_part (Part): Video part object
            video_identifier (str): Video identifier
            iterations (int): Number of analysis iterations
            pickle_analysis (bool): Whether to save results

        Returns:
            Dict: Analysis results
        """
        return self.unified_model.analyze_video(
            video_part=video_part,
            video_identifier=video_identifier,
            iterations=iterations,
            detection_threshold=self.shoplifting_detection_threshold,
            logger=self.logger,
            pickle_analysis=pickle_analysis
        )

    # ===== AGENTIC STRATEGY METHODS =====

    def analyze_video_agentic(self, video_part: Part, video_identifier: str, iterations: int,
                              pickle_analysis: bool = True) -> Dict:
        """
        Agentic strategy analysis method: CV observations → Analysis decision.

        Args:
            video_part (Part): Video part object
            video_identifier (str): Video identifier
            iterations (int): Number of iterations for consistency checking
            pickle_analysis (bool): Whether to save results

        Returns:
            Dict: Comprehensive analysis results
        """
        self.logger.info(f"Starting agentic analysis of '{video_identifier}' with {iterations} iterations")

        # Store results from multiple iterations
        iteration_results = []
        all_confidences = []
        all_detections = []
        cv_observations = []
        analysis_details = []

        for i in range(iterations):
            self.logger.info(f"=== AGENTIC ITERATION {i + 1}/{iterations} ===")

            # Step 1: Computer Vision Model - Get detailed observations
            self.logger.info(f"Step 1: Getting detailed observations from CV model...")

            # Get structured observations for better analysis
            structured_obs = self.cv_model.analyze_video_structured(video_part)
            cv_observations.append(str(structured_obs))  # Store structured obs as string for logging

            self.logger.info(f"CV Model Observations Length: {len(str(structured_obs))} characters")
            self.logger.debug(f"CV Observations Preview: {str(structured_obs)[:200]}...")

            # Step 2: Analysis Model - Make decision based on observations
            self.logger.info(f"Step 2: Analysis model making decision...")
            analysis_response, detected, confidence, detailed_analysis = self.analysis_model.analyze_structured_observations(
                video_part, structured_obs
            )

            analysis_details.append(detailed_analysis)

            self.logger.info(f"Analysis Result - Iteration {i + 1}:")
            self.logger.info(f"  Detected: {detected}")
            self.logger.info(f"  Confidence: {confidence:.3f}")
            self.logger.info(f"  Evidence Tier: {detailed_analysis.get('evidence_tier', 'N/A')}")
            self.logger.info(f"  Key Behaviors: {detailed_analysis.get('key_behaviors', [])}")

            if detailed_analysis.get('concealment_actions'):
                self.logger.info(f"  Concealment Actions: {detailed_analysis['concealment_actions']}")

            # Store iteration results
            iteration_result = {
                'iteration': i + 1,
                'cv_observations': str(structured_obs),
                'structured_observations': structured_obs,
                'analysis_response': analysis_response,
                'detected': detected,
                'confidence': confidence,
                'detailed_analysis': detailed_analysis,
                'timestamp': datetime.datetime.now().isoformat()
            }

            iteration_results.append(iteration_result)
            all_confidences.append(confidence)
            all_detections.append(detected)

        # Enhanced final decision using AnalysisModel's surveillance-realistic logic
        self.logger.info("=== MAKING FINAL DECISION ===")
        final_confidence, final_detection, decision_reasoning = self.analysis_model.make_surveillance_realistic_decision(
            confidences=all_confidences,
            detections=all_detections,
            shoplifting_detection_threshold=self.shoplifting_detection_threshold,
            detailed_analyses=analysis_details
        )

        self.logger.info(f"Final Decision:")
        self.logger.info(f"  Shoplifting Detected: {final_detection}")
        self.logger.info(f"  Final Confidence: {final_confidence:.3f}")
        self.logger.info(f"  Decision Reasoning: {decision_reasoning}")

        # Compile comprehensive results
        results = {
            "video_identifier": video_identifier,
            "analysis_approach": AGENTIC_MODEL,
            "iterations": iterations,
            "final_detection": final_detection,
            "final_confidence": final_confidence,
            "decision_reasoning": decision_reasoning,
            "confidence_levels": all_confidences,
            "detection_results": all_detections,
            "iteration_results": iteration_results,
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }

        # Save results if requested
        if pickle_analysis:
            self._save_analysis_to_pickle(results)

        # Performance summary
        self.logger.info(f"=== AGENTIC ANALYSIS COMPLETE ===")
        self.logger.info(f"Video: {video_identifier}")
        self.logger.info(f"Iterations: {iterations}")
        self.logger.info(f"Confidence Range: {min(all_confidences):.3f} - {max(all_confidences):.3f}")
        self.logger.info(f"Detection Consistency: {sum(all_detections)}/{len(all_detections)}")

        return results

    # ===== AGENTIC STRATEGY SUMMARY METHODS =====

    def _summarize_cv_observations(self, observations: List[str]) -> Dict[str, Any]:
        """
        Summarize computer vision observations across iterations.

        Args:
            observations (List[str]): List of CV observation strings

        Returns:
            Dict[str, Any]: Summary of observations
        """
        if not observations:
            return {"error": "No observations available"}

        # Analyze common themes across observations
        all_text = " ".join(observations).lower()

        # Use consolidated behavioral indicators from class constants
        suspicious_count = sum(1 for keyword in self.THEFT_INDICATORS if keyword in all_text)
        normal_count = sum(1 for keyword in self.NORMAL_INDICATORS if keyword in all_text)

        return {
            "total_observations": len(observations),
            "avg_length": np.mean([len(obs) for obs in observations]),
            "suspicious_indicators": suspicious_count,
            "normal_indicators": normal_count,
            "behavioral_tone": "suspicious" if suspicious_count > normal_count else "normal",
            "consistency": "high" if len(set(observations)) < len(observations) * 0.7 else "variable"
        }

    def _summarize_analysis_results(self, analysis_details: List[Dict]) -> Dict[str, Any]:
        """
        Summarize analysis results across iterations.

        Args:
            analysis_details (List[Dict]): List of detailed analysis results

        Returns:
            Dict[str, Any]: Summary of analysis results
        """
        if not analysis_details:
            return {"error": "No analysis details available"}

        # Extract evidence tiers
        evidence_tiers = [detail.get('evidence_tier', 'UNKNOWN') for detail in analysis_details]
        tier_counts = {tier: evidence_tiers.count(tier) for tier in set(evidence_tiers)}

        # Collect all key behaviors
        all_behaviors = []
        all_concealment_actions = []

        for detail in analysis_details:
            all_behaviors.extend(detail.get('key_behaviors', []))
            all_concealment_actions.extend(detail.get('concealment_actions', []))

        return {
            "total_analyses": len(analysis_details),
            "evidence_tier_distribution": tier_counts,
            "most_common_tier": max(tier_counts, key=tier_counts.get) if tier_counts else "NONE",
            "unique_behaviors": list(set(all_behaviors)),
            "concealment_actions": list(set(all_concealment_actions)),
            "has_concealment_evidence": len(all_concealment_actions) > 0
        }

    # ===== SHARED FILE OPERATIONS =====

    def _save_analysis_to_pickle(self, analysis: Dict) -> None:
        """
        Shared method to save analysis results to pickle file.

        Args:
            analysis (Dict): Analysis results to save
        """
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            strategy_prefix = self.strategy if self.strategy != UNIFIED_MODEL else UNIFIED_MODEL
            pkl_path = f"{strategy_prefix}_analysis_{current_time}.pkl"

            with open(pkl_path, 'wb') as file:
                pickle.dump(analysis, file)

            self.logger.info(f"Analysis saved to pickle file: {pkl_path}")

        except Exception as e:
            self.logger.error(f"Failed to save analysis to pickle: {e}")
