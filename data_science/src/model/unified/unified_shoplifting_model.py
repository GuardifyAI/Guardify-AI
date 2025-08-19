from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, Optional, Tuple, List
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType, \
    GenerationResponse
import os
import json
import logging
import datetime
import pickle
import numpy as np

from data_science.src.model.unified.prompt.unified_prompt import default_response_schema, default_system_instruction, \
    unified_prompt
from data_science.src.utils import UNIFIED_MODEL
from utils import load_env_variables

load_env_variables()


class UnifiedShopliftingModel(GenerativeModel):
    """
    REVOLUTIONARY UNIFIED ARCHITECTURE
    ==================================
    
    This model combines video analysis and shoplifting detection in a single step,
    eliminating information loss and using few-shot learning with real examples.
    """

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

    default_generation_config = GenerationConfig(
        temperature=0.05,  # Much lower for more consistent, conservative responses
        top_p=0.7,  # More focused on high-probability responses
        top_k=10,  # Even more focused responses
        candidate_count=1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=default_response_schema
    )

    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    def __init__(self,
                 model_name: str = os.getenv("DEFAULT_MODEL_ID"),
                 *,
                 generation_config: Optional[GenerationConfigType] = None,
                 safety_settings: Optional[SafetySettingsType] = None,
                 system_instruction: Optional[PartsType] = None,
                 labels: Optional[Dict[str, str]] = None):

        if system_instruction is None:
            system_instruction = default_system_instruction

        if generation_config is None:
            generation_config = self.default_generation_config

        if safety_settings is None:
            safety_settings = self.default_safety_settings

        super().__init__(model_name=model_name,
                         generation_config=generation_config,
                         safety_settings=safety_settings,
                         system_instruction=system_instruction,
                         labels=labels)

    def analyze_video_unified(self, video_file: Part, prompt: str = None) -> Tuple[str, bool, float, dict]:
        """
        UNIFIED analysis: Direct video → detection in single step.
        
        Returns:
            Tuple[str, bool, float, dict]: (full_response, detected, confidence, detailed_analysis)
        """
        if prompt is None:
            prompt = unified_prompt

        contents = [video_file, prompt]

        # Single model call - no information loss!
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings
        )

        # Extract structured results
        detected, confidence, analysis = self._extract_unified_response(response)

        return response.text, detected, confidence, analysis

    def _extract_unified_response(self, response: GenerationResponse) -> Tuple[bool, float, dict]:
        """Extract detection results from unified model response."""
        try:
            response_json = json.loads(response.text)

            detected = response_json["Shoplifting Detected"]
            confidence = response_json["Confidence Level"]

            # Full analysis details
            analysis = {
                "evidence_tier": response_json.get("Evidence Tier", ""),
                "key_behaviors_observed": response_json.get("Key Behaviors Observed", []),
                "concealment_actions": response_json.get("Concealment Actions", []),
                "risk_assessment": response_json.get("Risk Assessment", ""),
                "decision_reasoning": response_json.get("Decision Reasoning", ""),
            }

            return detected, confidence, analysis

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback for malformed responses
            return False, 0.0, {"error": f"Response parsing failed: {e}"}

    def analyze_video(self, video_part: Part, video_identifier: str, iterations: int, detection_threshold: float,
                      logger: logging.Logger = None, pickle_analysis: bool = True) -> Dict:
        """
        Comprehensive unified strategy analysis method using UnifiedShopliftingModel.
        This is the main analysis method moved from ShopliftingAnalyzer.

        Args:
            video_part (Part): Video part object
            video_identifier (str): Video identifier
            iterations (int): Number of analysis iterations
            detection_threshold (float): Detection confidence threshold
            logger (logging.Logger, optional): Logger instance
            pickle_analysis (bool): Whether to save results

        Returns:
            Dict: Analysis results
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"Starting UNIFIED analysis of '{video_identifier}' with {iterations} iterations")

        # Process multiple iterations
        iteration_results, all_confidences, all_detections = self._process_unified_iterations(
            video_part, video_identifier, iterations, logger
        )

        # Make final decision
        final_confidence, final_detection, decision_reasoning = self._make_unified_final_decision(
            all_confidences, all_detections, detection_threshold, logger
        )

        # Compile and log results
        analysis_results = self._compile_results_schema(
            video_identifier, iterations, iteration_results, all_confidences,
            all_detections, final_confidence, final_detection, decision_reasoning, logger
        )

        # Save if requested
        if pickle_analysis:
            self._save_analysis_to_pickle(analysis_results, logger)

        return analysis_results

    def _process_unified_iterations(self, video_part: Part, video_identifier: str, iterations: int,
                                    logger: logging.Logger) -> Tuple[List[Dict], List[float], List[bool]]:
        """
        Process multiple analysis iterations and collect results.
        
        Args:
            video_part (Part): Video part object
            video_identifier (str): Video identifier
            iterations (int): Number of iterations to process
            logger (logging.Logger): Logger instance
            
        Returns:
            Tuple[List[Dict], List[float], List[bool]]: (iteration_results, confidences, detections)
        """
        iteration_results = []
        all_confidences = []
        all_detections = []

        for i in range(iterations):
            logger.info(f"Iteration {i + 1}/{iterations}")

            # Single unified model call - direct video→detection!
            full_response, detected, confidence, detailed_analysis = self.analyze_video_unified(video_part)

            # Log and analyze this iteration
            self._log_iteration_analysis(i + 1, video_identifier, detected, confidence, detailed_analysis, logger)

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

        return iteration_results, all_confidences, all_detections

    def _log_iteration_analysis(self, iteration: int, video_identifier: str, detected: bool,
                                confidence: float, detailed_analysis: Dict, logger: logging.Logger):
        """
        Log detailed analysis for a single iteration.
        
        Args:
            iteration (int): Current iteration number
            video_identifier (str): Video identifier
            detected (bool): Whether theft was detected
            confidence (float): Confidence level
            detailed_analysis (Dict): Detailed analysis results
            logger (logging.Logger): Logger instance
        """
        logger.info(f"[CONFIDENCE] Using original unified model confidence: {confidence:.3f}")

        # ENHANCED DIAGNOSTIC LOGGING
        logger.info(f"=== DIAGNOSTIC ANALYSIS - Iteration {iteration} ===")
        logger.info(f"Video: {video_identifier}")
        logger.info(f"Detected: {detected}")
        logger.info(f"Confidence: {confidence:.3f}")

        # Log behavioral patterns identified
        observed_behavior = detailed_analysis.get('observed_behavior', '')
        reasoning = detailed_analysis.get('reasoning', '')

        if observed_behavior:
            logger.info(f"MODEL OBSERVATIONS: {observed_behavior}")

        if reasoning:
            logger.info(f"REASONING: {reasoning}")

        # ENHANCED PATTERN ANALYSIS
        if observed_behavior or reasoning:
            self._analyze_behavioral_patterns(observed_behavior, reasoning, logger)

        logger.info(f"=== END ENHANCED DIAGNOSTIC - Iteration {iteration} ===")

    def _analyze_behavioral_patterns(self, observed_behavior: str, reasoning: str, logger: logging.Logger):
        """
        Analyze and log behavioral patterns from model observations.
        
        Args:
            observed_behavior (str): Observed behavior description
            reasoning (str): Model reasoning text
            logger (logging.Logger): Logger instance
        """
        combined_text = f"{observed_behavior} {reasoning}".lower()

        # Check for theft behavior indicators
        found_theft_indicators = [ind for ind in self.THEFT_INDICATORS if ind in combined_text]
        found_normal_indicators = [ind for ind in self.NORMAL_INDICATORS if ind in combined_text]

        if found_theft_indicators:
            logger.info(f"THEFT INDICATORS DETECTED: {found_theft_indicators}")
        if found_normal_indicators:
            logger.info(f"NORMAL INDICATORS DETECTED: {found_normal_indicators}")

    def _make_unified_final_decision(self, all_confidences: List[float], all_detections: List[bool],
                                     detection_threshold: float, logger: logging.Logger) -> Tuple[float, bool, str]:
        """
        Make final decision based on all iterations and apply threshold check.
        
        Args:
            all_confidences (List[float]): All confidence scores
            all_detections (List[bool]): All detection results
            detection_threshold (float): Detection confidence threshold
            logger (logging.Logger): Logger instance
            
        Returns:
            Tuple[float, bool, str]: (final_confidence, final_detection, decision_reasoning)
        """
        # SURVEILLANCE-REALISTIC DECISION ALGORITHM for unified
        final_confidence, final_detection, decision_reasoning = self._make_surveillance_realistic_decision_unified(
            all_confidences, all_detections, logger
        )

        # Apply threshold check
        if final_detection and final_confidence < detection_threshold:
            final_detection = False
            decision_reasoning += f" | THRESHOLD: Below detection threshold {detection_threshold:.3f}"
        elif not final_detection and final_confidence >= detection_threshold:
            final_detection = True
            decision_reasoning += f" | THRESHOLD: Meets detection threshold {detection_threshold:.3f}"

        return final_confidence, final_detection, decision_reasoning

    def _make_surveillance_realistic_decision_unified(self, confidences: List[float], detections: List[bool],
                                                      logger: logging.Logger) -> Tuple[float, bool, str]:
        """
        Simple decision logic for unified model based on iteration statistics.
        """
        # Calculate confidence statistics
        avg_confidence = np.mean(confidences)
        max_confidence = np.max(confidences)
        detection_count = sum(detections)
        total_iterations = len(detections)

        logger.info(f"UNIFIED DECISION inputs: avg_conf={avg_confidence:.3f}, max_conf={max_confidence:.3f}, "
                    f"detections={detection_count}/{total_iterations}")

        # Simple logic: Use the maximum confidence and trust the model's decisions
        final_confidence = max_confidence
        final_detection = detection_count > 0  # If any iteration detected theft, consider it detected

        # Create reasoning based on statistics
        if detection_count == 0:
            reasoning = (f"NORMAL BEHAVIOR: No theft detected across {total_iterations} iterations (max confidence: "
                         f"{max_confidence:.3f})")
        elif detection_count == total_iterations:
            reasoning = (f"CONSISTENT THEFT: Detected in all {total_iterations} iterations (max confidence: "
                         f"{max_confidence:.3f})")
        else:
            reasoning = (f"PARTIAL DETECTION: Detected in {detection_count}/{total_iterations} iterations (max "
                         f"confidence: {max_confidence:.3f})")

        logger.info(f"UNIFIED DECISION: conf={final_confidence:.3f}, detected={final_detection}")
        logger.info(f"Reasoning: {reasoning}")

        return final_confidence, final_detection, reasoning

    def _compile_results_schema(self, video_identifier: str, iterations: int, iteration_results: List[Dict],
                                all_confidences: List[float], all_detections: List[bool],
                                final_confidence: float, final_detection: bool, decision_reasoning: str,
                                logger: logging.Logger) -> Dict:
        """
        Compile comprehensive analysis results and log final decision.
        
        Args:
            video_identifier (str): Video identifier
            iterations (int): Number of iterations performed
            iteration_results (List[Dict]): All iteration results
            all_confidences (List[float]): All confidence scores
            all_detections (List[bool]): All detection results
            final_confidence (float): Final confidence score
            final_detection (bool): Final detection decision
            decision_reasoning (str): Decision reasoning text
            logger (logging.Logger): Logger instance
            
        Returns:
            Dict: Comprehensive analysis results
        """
        # Enhanced logging for decision process
        self._log_decision_analysis(video_identifier, all_confidences, all_detections, logger)

        # Compile comprehensive results
        analysis_results = {
            "video_identifier": video_identifier,
            "analysis_approach": UNIFIED_MODEL,
            "iterations": iterations,
            "iteration_results": iteration_results,
            "confidence_levels": all_confidences,
            "detection_results": all_detections,
            "final_confidence": final_confidence,
            "final_detection": final_detection,
            "decision_reasoning": decision_reasoning,
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }

        # Log final decision with enhanced context
        self._log_final_decision(final_confidence, final_detection, decision_reasoning, logger)

        return analysis_results

    def _log_decision_analysis(self, video_identifier: str, all_confidences: List[float],
                               all_detections: List[bool], logger: logging.Logger):
        """
        Log enhanced decision process information.
        
        Args:
            video_identifier (str): Video identifier
            all_confidences (List[float]): All confidence scores
            all_detections (List[bool]): All detection results
            logger (logging.Logger): Logger instance
        """
        logger.info(f"UNIFIED DECISION ANALYSIS for {video_identifier}:")
        logger.info(f"  All confidences: {all_confidences}")
        logger.info(f"  All detections: {all_detections}")
        logger.info(f"  Average confidence: {np.mean(all_confidences):.3f}")
        logger.info(f"  Max confidence: {np.max(all_confidences):.3f}")
        logger.info(f"  Detection count: {sum(all_detections)}/{len(all_detections)}")

    def _log_final_decision(self, final_confidence: float, final_detection: bool,
                            decision_reasoning: str, logger: logging.Logger):
        """
        Log final decision with enhanced context.
        
        Args:
            final_confidence (float): Final confidence score
            final_detection (bool): Final detection decision
            decision_reasoning (str): Decision reasoning text
            logger (logging.Logger): Logger instance
        """
        logger.info(f"UNIFIED ANALYSIS COMPLETE:")
        logger.info(f"  Final Confidence: {final_confidence:.3f}")
        logger.info(f"  Final Detection: {final_detection}")
        logger.info(f"  Reasoning: {decision_reasoning}")

    def _save_analysis_to_pickle(self, analysis: Dict, logger: logging.Logger) -> None:
        """
        Save analysis results to pickle file.

        Args:
            analysis (Dict): Analysis results to save
            logger (logging.Logger): Logger instance
        """
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            pkl_path = f"{UNIFIED_MODEL}_analysis_{current_time}.pkl"

            with open(pkl_path, 'wb') as file:
                pickle.dump(analysis, file)

            logger.info(f"Analysis saved to pickle file: {pkl_path}")

        except Exception as e:
            logger.error(f"Failed to save analysis to pickle: {e}")
