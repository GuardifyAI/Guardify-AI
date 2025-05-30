from data_science.src.google.AnalysisModel import AnalysisModel
from data_science.src.google.ComputerVisionModel import ComputerVisionModel
import logging
from data_science.src.utils import create_logger, get_video_extension, AGENTIC_MODEL, UNIFIED_MODEL
from vertexai.generative_models import Part
from typing import List, Tuple, Dict, Any
import numpy as np
import pickle
import datetime
import os


def create_unified_analyzer(detection_threshold: float = 0.45, logger: logging.Logger = None):
    """
    Factory function to create a unified strategy analyzer.

    Args:
        detection_threshold (float): Detection confidence threshold
        logger (logging.Logger, optional): Logger instance

    Returns:
        ShopliftingAnalyzer: Configured for unified strategy
    """
    return ShopliftingAnalyzer(
        detection_strictness=detection_threshold,
        logger=logger,
        strategy=UNIFIED_MODEL
    )


def create_agentic_analyzer(detection_threshold: float = 0.50, logger: logging.Logger = None):
    """
    Factory function to create an agentic strategy analyzer.

    Args:
        detection_threshold (float): Detection confidence threshold
        logger (logging.Logger, optional): Logger instance

    Returns:
        ShopliftingAnalyzer: Configured for agentic strategy
    """
    return ShopliftingAnalyzer(
        detection_strictness=detection_threshold,
        logger=logger,
        strategy=AGENTIC_MODEL
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

    ANALYSIS_DICT = {
        "video_identifier": str(),
        "confidence_levels": list(),
        "shoplifting_detected_results": list(),
        "cv_model_responses": list(),
        "analysis_model_responses": list(),
        "stats": dict(),
        "shoplifting_probability": float(),
        "shoplifting_determination": bool()
    }

    def __init__(self, cv_model: ComputerVisionModel = None, analysis_model: AnalysisModel = None,
                 detection_strictness: float = 0.45, logger: logging.Logger = None,
                 strategy: str = "unified"):
        """
        Initialize the ShopliftingAnalyzer with support for both unified and agentic strategies.

        Args:
            cv_model (ComputerVisionModel, optional): Computer vision model for video analysis
            analysis_model (AnalysisModel, optional): Analysis model for interpreting observations
            detection_strictness (float): Confidence threshold (0-1) for shoplifting detection
            logger (logging.Logger, optional): Logger instance
            strategy (str): "unified" or AGENTIC_MODEL analysis strategy
        """
        self.strategy = strategy

        # Initialize models based on strategy
        if strategy == "unified":
            # Import here to avoid circular imports
            from UnifiedShopliftingModel import UnifiedShopliftingModel
            self.unified_model = UnifiedShopliftingModel()
            self.cv_model = None
            self.analysis_model = None
        else:
            # Agentic strategy uses separate models
            self.cv_model = cv_model or ComputerVisionModel()
            self.analysis_model = analysis_model or AnalysisModel()
            self.unified_model = None

        # Validation
        if detection_strictness < 0 or detection_strictness > 1:
            raise ValueError("Detection strictness must be between 0 and 1.")
        self.shoplifting_detection_threshold = detection_strictness

        # Initialize logger
        if logger is None:
            strategy_suffix = f"_{strategy}" if strategy != "unified" else ""
            self.logger = create_logger(f'ShopliftingAnalyzer{strategy_suffix}', f'{strategy}_analysis.log')
        else:
            self.logger = logger

        # Set logger on analysis model for enhanced debugging (agentic only)
        if self.analysis_model and hasattr(self.analysis_model, 'logger'):
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

    def analyze_video_from_bucket(self, video_uri: str,
                                  iterations: int = None, pickle_analysis: bool = True) -> Dict:
        """
        Unified method to analyze video from GCS bucket using current strategy.

        Args:
            video_uri (str): GCS URI of the video
            iterations (int, optional): Number of iterations (agentic strategy)
            pickle_analysis (bool): Whether to save analysis results

        Returns:
            Dict: Analysis results
        """
        try:
            # Validate video format
            extension = self._validate_video_format(video_uri)
            video_part = Part.from_uri(uri=video_uri, mime_type=self.VIDEO_MIME_TYPES[extension])

            # Route to appropriate analysis method
            if self.strategy == AGENTIC_MODEL:
                iterations = iterations or 2
                return self.analyze_video_agentic(video_part, video_uri, iterations, pickle_analysis)
            else:
                iterations = iterations or 2  # Unified uses iterations, not max_api_calls
                return self.analyze_video_unified(video_part, video_uri, iterations, pickle_analysis)

        except Exception as e:
            self.logger.error(f"Failed to analyze {video_uri}: {e}")
            return self._create_error_result(video_uri, str(e))

    def analyze_local_video(self, video_path: str,
                            iterations: int = None, pickle_analysis: bool = True) -> Dict:
        """
        Unified method to analyze local video file using current strategy.

        Args:
            video_path (str): Path to local video file
            iterations (int, optional): Number of iterations (agentic strategy)
            pickle_analysis (bool): Whether to save analysis results

        Returns:
            Dict: Analysis results
        """
        # Validate file existence and format
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found at path: {video_path}")
            return self.ANALYSIS_DICT

        extension = self._validate_video_format(video_path)

        # Create video part
        video_part = Part.from_data(
            mime_type=self.VIDEO_MIME_TYPES[extension],
            data=open(video_path, "rb").read()
        )

        # Route to appropriate analysis method
        if self.strategy == AGENTIC_MODEL:
            iterations = iterations or 3
            return self.analyze_video_agentic(video_part, video_path, iterations, pickle_analysis)
        else:
            iterations = iterations or 3  # Unified uses iterations
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
            "final_detection": False,
            "final_confidence": 0.0,
            "analysis_approach": f"{self.strategy.upper()}_ENHANCED",
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
        self.logger.info(f"Starting UNIFIED analysis of '{video_identifier}' with {iterations} iterations")

        if self.strategy != "unified" or not self.unified_model:
            raise ValueError("Unified analysis requires unified strategy and UnifiedShopliftingModel")

        # Store results from multiple iterations
        iteration_results = []
        all_confidences = []
        all_detections = []

        for i in range(iterations):
            self.logger.info(f"Iteration {i + 1}/{iterations}")

            # Single unified model call - direct video→detection!
            full_response, detected, confidence, detailed_analysis = self.unified_model.analyze_video_unified(
                video_part)

            self.logger.info(f"[CONFIDENCE] Using original unified model confidence: {confidence:.3f}")

            # ENHANCED DIAGNOSTIC LOGGING
            self.logger.info(f"=== ENHANCED DIAGNOSTIC ANALYSIS - Iteration {i + 1} ===")
            self.logger.info(f"Video: {video_identifier}")
            self.logger.info(f"Detected: {detected}")
            self.logger.info(f"Confidence: {confidence:.3f}")

            # Log behavioral patterns identified
            observed_behavior = detailed_analysis.get('observed_behavior', '')
            reasoning = detailed_analysis.get('reasoning', '')

            if observed_behavior:
                self.logger.info(f"MODEL OBSERVATIONS: {observed_behavior}")

            if reasoning:
                self.logger.info(f"REASONING: {reasoning}")

            # ENHANCED PATTERN ANALYSIS
            if observed_behavior or reasoning:
                combined_text = f"{observed_behavior} {reasoning}".lower()

                # Check for theft behavior indicators
                theft_indicators = [
                    'pocket', 'bag', 'waist', 'concealed', 'hidden', 'tucked',
                    'clothing adjustment', 'hand movement', 'body area', 'conceal'
                ]
                normal_indicators = [
                    'browsing', 'examining', 'looking', 'normal', 'casual',
                    'no clear', 'no visible', 'ambiguous', 'consistent with normal'
                ]

                found_theft_indicators = [ind for ind in theft_indicators if ind in combined_text]
                found_normal_indicators = [ind for ind in normal_indicators if ind in combined_text]

                if found_theft_indicators:
                    self.logger.info(f"THEFT INDICATORS DETECTED: {found_theft_indicators}")
                if found_normal_indicators:
                    self.logger.info(f"NORMAL INDICATORS DETECTED: {found_normal_indicators}")

                # Analyze the decision pattern
                if detected and confidence >= 0.6:
                    self.logger.info(f"[THEFT PATTERN] High confidence theft behavior detected")
                elif detected and confidence < 0.6:
                    self.logger.info(f"[BORDERLINE THEFT] Low confidence theft flag")
                elif not detected and confidence <= 0.3:
                    self.logger.info(f"[NORMAL BEHAVIOR] Correctly identified as normal")
                elif not detected and confidence > 0.3:
                    self.logger.info(f"[MIXED SIGNALS] Not detected but moderate confidence")

            # Flag potential missed thefts on shoplifting videos
            if confidence <= 0.3 and (
                    'shop_lifter' in video_identifier.lower() and 'shop_lifter_n' not in video_identifier.lower()):
                self.logger.warning(f"[POTENTIAL MISSED THEFT] Shoplifting video with very low confidence")
                self.logger.warning(f"  This may indicate the model is missing behavioral patterns")
                self.logger.warning(f"  Review: Does the reasoning show theft patterns that were dismissed?")

            self.logger.info(f"=== END ENHANCED DIAGNOSTIC - Iteration {i + 1} ===")

            # Store iteration results
            iteration_result = {
                "iteration": i + 1,
                "detected": detected,
                "confidence": confidence,
                "detailed_analysis": detailed_analysis,
                "full_response": full_response
            }
            iteration_results.append(iteration_result)
            all_confidences.append(confidence)
            all_detections.append(detected)

        # SURVEILLANCE-REALISTIC DECISION ALGORITHM for unified
        final_confidence, final_detection, decision_reasoning = self._make_surveillance_realistic_decision_unified(
            all_confidences, all_detections, iteration_results)

        # Apply threshold check
        if final_detection and final_confidence < self.shoplifting_detection_threshold:
            final_detection = False
            decision_reasoning += f" | THRESHOLD: Below detection threshold {self.shoplifting_detection_threshold:.3f}"
        elif not final_detection and final_confidence >= self.shoplifting_detection_threshold:
            final_detection = True
            decision_reasoning += f" | THRESHOLD: Meets detection threshold {self.shoplifting_detection_threshold:.3f}"

        # Enhanced logging for decision process
        self.logger.info(f"UNIFIED DECISION ANALYSIS for {video_identifier}:")
        self.logger.info(f"  All confidences: {all_confidences}")
        self.logger.info(f"  All detections: {all_detections}")
        self.logger.info(f"  Average confidence: {np.mean(all_confidences):.3f}")
        self.logger.info(f"  Max confidence: {np.max(all_confidences):.3f}")
        self.logger.info(f"  Detection count: {sum(all_detections)}/{len(all_detections)}")

        # Compile comprehensive results
        analysis_results = {
            "video_identifier": video_identifier,
            "analysis_approach": "UNIFIED_SINGLE_MODEL",
            "iterations": iterations,
            "iteration_results": iteration_results,
            "confidence_levels": all_confidences,
            "detection_results": all_detections,
            "final_confidence": final_confidence,
            "final_detection": final_detection,
            "decision_reasoning": decision_reasoning,
            "detection_threshold": self.shoplifting_detection_threshold,
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }

        # Log final decision with enhanced context
        self.logger.info(f"UNIFIED ANALYSIS COMPLETE:")
        self.logger.info(f"  Final Confidence: {final_confidence:.3f}")
        self.logger.info(f"  Final Detection: {final_detection}")
        self.logger.info(f"  Reasoning: {decision_reasoning}")

        # Only flag actual concerning cases - not based on filename
        if final_confidence >= 0.35 and not final_detection:
            self.logger.warning(f"BORDERLINE CASE: {video_identifier}")
            self.logger.warning(f"  Moderate confidence ({final_confidence:.3f}) but below detection threshold")
            self.logger.warning(f"  Consider reviewing if this represents a detection threshold issue")

        if pickle_analysis:
            self._save_analysis_to_pickle(analysis_results)

        return analysis_results

    def _make_surveillance_realistic_decision_unified(self, confidences: List[float], detections: List[bool],
                                                      iteration_results: List[Dict]) -> Tuple[float, bool, str]:
        """
        SURVEILLANCE-REALISTIC DECISION LOGIC for unified model - Balance theft detection with false positive avoidance
        """
        # Calculate confidence statistics
        avg_confidence = np.mean(confidences)
        max_confidence = np.max(confidences)
        detection_count = sum(detections)
        total_iterations = len(detections)

        self.logger.info(f"UNIFIED DECISION inputs: avg_conf={avg_confidence:.3f}, max_conf={max_confidence:.3f}, "
                         f"detections={detection_count}/{total_iterations}")

        # Case 1: No detection by model - likely normal behavior
        if detection_count == 0:
            final_confidence = avg_confidence
            final_detection = False
            reasoning = f"NORMAL BEHAVIOR: No theft patterns detected (confidence: {avg_confidence:.3f})"

        # Case 2: Model detected theft - but carefully examine if it's actually normal behavior
        else:
            # IMPROVED OVERRIDE LOGIC: Only apply normal shopping override if confidence is already low or context
            # suggests normal behavior
            normal_shopping_indicators = []
            strong_theft_evidence = []

            for result in iteration_results:
                analysis = result.get('detailed_analysis', {})
                obs = analysis.get('observed_behavior', '').lower()
                reasoning_text = analysis.get('reasoning', '').lower()
                combined_text = f"{obs} {reasoning_text}"

                # Strong theft evidence that should NOT be overridden
                strong_theft_patterns = [
                    'classic', 'grab and stuff', 'concealment', 'theft pattern',
                    'shoplifting', 'deliberately concealed', 'strong indicator of theft',
                    'clear pattern of shoplifting', 'obvious concealment', 'definitive concealment',
                    'classic concealment sequence', 'clear act of concealment'
                ]

                # Normal shopping patterns (only apply if NO strong theft evidence)
                weak_normal_patterns = [
                    'normal browsing', 'typical browsing', 'browsing behavior',
                    'normal customer behavior', 'casual browsing'
                ]

                # Check for strong theft evidence first
                for pattern in strong_theft_patterns:
                    if pattern in combined_text:
                        strong_theft_evidence.append(f"theft_evidence: {pattern}")

                # Only check for normal patterns if NO strong theft evidence
                if not strong_theft_evidence:
                    for pattern in weak_normal_patterns:
                        if pattern in combined_text:
                            normal_shopping_indicators.append(f"normal_pattern: {pattern}")

            # CONTEXTUAL OVERRIDE DECISION
            if strong_theft_evidence:
                # Strong theft evidence - do NOT override, trust the model
                self.logger.info(f"STRONG THEFT EVIDENCE: {strong_theft_evidence} - NO OVERRIDE")
                if max_confidence >= 0.8:
                    final_confidence = max_confidence
                    final_detection = True
                    reasoning = f"CONFIRMED THEFT: Strong evidence ({max_confidence:.3f}) with clear patterns: {strong_theft_evidence}"
                elif max_confidence >= 0.6:
                    final_confidence = max_confidence
                    final_detection = True
                    reasoning = f"PROBABLE THEFT: Good evidence ({max_confidence:.3f}) with patterns: {strong_theft_evidence}"
                else:
                    final_confidence = max_confidence
                    final_detection = final_confidence >= self.shoplifting_detection_threshold
                    reasoning = f"BORDERLINE THEFT: Moderate evidence ({max_confidence:.3f}) with some patterns"

            elif normal_shopping_indicators and max_confidence < 0.6:
                # Normal shopping indicators AND low confidence - apply override
                self.logger.info(f"NORMAL SHOPPING OVERRIDE: Found indicators: {normal_shopping_indicators}")
                final_confidence = max_confidence * 0.4  # Reduce but not as dramatically
                final_detection = final_confidence >= self.shoplifting_detection_threshold
                reasoning = f"NORMAL SHOPPING OVERRIDE: Original confidence {max_confidence:.3f} reduced due to normal indicators: {normal_shopping_indicators}"

            else:
                # Standard theft detection logic - no override needed
                if max_confidence >= 0.8:
                    final_confidence = max_confidence
                    final_detection = True
                    reasoning = f"CONFIRMED THEFT: Very high confidence ({max_confidence:.3f}) behavioral evidence"
                elif max_confidence >= 0.6:
                    final_confidence = max_confidence
                    final_detection = True
                    reasoning = f"PROBABLE THEFT: High confidence ({max_confidence:.3f}) behavioral pattern detected"
                else:
                    final_confidence = max_confidence
                    final_detection = final_confidence >= self.shoplifting_detection_threshold
                    reasoning = f"MODERATE CONFIDENCE: Detected ({max_confidence:.3f}) requires threshold validation"

        self.logger.info(f"UNIFIED DECISION: conf={final_confidence:.3f}, detected={final_detection}")
        self.logger.info(f"Reasoning: {reasoning}")

        return final_confidence, final_detection, reasoning

    # ===== AGENTIC STRATEGY METHODS =====

    def analyze_video_agentic(self, video_part: Part, video_identifier: str, iterations: int = 3,
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
        if self.strategy != AGENTIC_MODEL or not self.cv_model or not self.analysis_model:
            raise ValueError("Agentic analysis requires agentic strategy and both CV and Analysis models")

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
            cv_response = self.cv_model.analyze_video(video_part)
            cv_observations.append(cv_response)

            # Get structured observations for better analysis
            structured_obs = self.cv_model.analyze_video_structured(video_part)

            self.logger.info(f"CV Model Observations Length: {len(cv_response)} characters")
            self.logger.debug(f"CV Observations Preview: {cv_response[:200]}...")

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
                'cv_observations': cv_response,
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
            all_confidences, all_detections, analysis_details
        )

        self.logger.info(f"Final Decision:")
        self.logger.info(f"  Shoplifting Detected: {final_detection}")
        self.logger.info(f"  Final Confidence: {final_confidence:.3f}")
        self.logger.info(f"  Decision Reasoning: {decision_reasoning}")

        # Check against threshold
        threshold_decision = final_confidence >= self.shoplifting_detection_threshold
        if threshold_decision != final_detection:
            self.logger.warning(
                f"Threshold adjustment: {final_detection} -> {threshold_decision} (threshold: {self.shoplifting_detection_threshold})")

        # Compile comprehensive results
        results = {
            "video_identifier": video_identifier,
            "analysis_approach": "AGENTIC_ENHANCED",
            "iterations": iterations,
            "detection_threshold": self.shoplifting_detection_threshold,

            # Final results
            "final_detection": threshold_decision,
            "final_confidence": final_confidence,
            "decision_reasoning": decision_reasoning,

            # Iteration data
            "confidence_levels": all_confidences,
            "detection_results": all_detections,
            "iteration_results": iteration_results,

            # Summary statistics
            "avg_confidence": np.mean(all_confidences),
            "detection_consistency": sum(all_detections) / len(all_detections),
            "confidence_std": np.std(all_confidences),

            # Enhanced analysis summary
            "cv_observations_summary": self._summarize_cv_observations(cv_observations),
            "analysis_summary": self._summarize_analysis_results(analysis_details),

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
        self.logger.info(f"Final Result: detected={threshold_decision}, confidence={final_confidence:.3f}")

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

        # Key behavioral indicators
        suspicious_keywords = [
            'pocket', 'bag', 'concealed', 'hidden', 'tucked', 'waist',
            'nervous', 'furtive', 'quick', 'suspicious', 'concealment'
        ]
        normal_keywords = [
            'browsing', 'examining', 'normal', 'casual', 'returned',
            'shelf', 'checkout', 'natural', 'regular'
        ]

        suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in all_text)
        normal_count = sum(1 for keyword in normal_keywords if keyword in all_text)

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
            strategy_prefix = self.strategy if self.strategy != "unified" else "unified"
            pkl_path = f"{strategy_prefix}_analysis_{current_time}.pkl"

            with open(pkl_path, 'wb') as file:
                pickle.dump(analysis, file)

            self.logger.info(f"Analysis saved to pickle file: {pkl_path}")

        except Exception as e:
            self.logger.error(f"Failed to save analysis to pickle: {e}")
