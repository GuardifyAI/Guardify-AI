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
from data_science.src.utils import load_env_variables, UNIFIED_MODEL

load_env_variables()


class UnifiedShopliftingModel(GenerativeModel):
    """
    REVOLUTIONARY UNIFIED ARCHITECTURE
    ==================================
    
    This model combines video analysis and shoplifting detection in a single step,
    eliminating information loss and using few-shot learning with real examples.
    """

    # Consolidated behavioral indicators (moved from ShopliftingAnalyzer)
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

    default_system_instruction = [
        "You are an elite retail loss prevention expert with 15+ years of experience in shoplifting detection.",
        "You have analyzed thousands of surveillance videos and can instantly recognize theft patterns.",
        "Your expertise lies in detecting even subtle concealment behaviors in short video clips.",
        "You understand that modern shoplifters use sophisticated techniques to avoid detection.",
        "Your analysis is direct, accurate, and based on proven behavioral indicators.",
        "You excel at distinguishing between normal shopping and theft with high precision."
    ]

    unified_prompt = """
    You are an expert shoplifting detection system that BALANCES normal shopping protection with theft pattern recognition.

    🛍️ CRITICAL UNDERSTANDING: 95% of customer interactions are NORMAL SHOPPING behaviors.

    ✅ NORMAL SHOPPING BEHAVIORS (CONFIDENCE 0.1-0.2, DO NOT FLAG):

    **Normal Hand Movements:**
    • Touching/examining items and walking away empty-handed
    • Hand movements for clothing adjustment (pulling shirt, fixing jacket) 
    • Reaching to pocket/purse for phone, keys, or wallet while shopping
    • Natural hand gestures while browsing or thinking
    • Casual touching of body/clothing during normal shopping
    • Looking at price tags, examining merchandise

    **Normal Shopping Patterns:**
    • Customer approaches → examines items → walks away (no purchase)
    • Brief interaction with merchandise followed by continued browsing
    • Hand movements clearly for comfort/convenience
    • Casual browsing with natural body language

    🚨 THEFT BEHAVIORAL PATTERNS (CONFIDENCE 0.6-0.8, FLAG THESE):

    **Classic Theft Sequences:**
    • **"Grab and Stuff"**: Item pickup → immediate hand movement to pocket/waist/bag → departure
    • **Sequential Concealment**: Multiple items moved to concealment areas in succession
    • **Pick and Hide**: Item selected → deliberate insertion into clothing/bag → covering motion

    **Behavioral Pattern Indicators:**
    • Item interaction followed by hand movement to typical concealment zones (waist, pocket, bag)
    • Object appears to vanish during hand-to-body movement
    • Immediate departure after suspicious hand movements
    • Multiple concealment motions in short timeframe
    • Adjustment of clothing after hand movements to concealment areas

    **Trust Behavioral Sequences:**
    • Surveillance cameras can detect behavioral patterns even without perfect item visibility
    • Look for the SEQUENCE: pickup → concealment motion → departure
    • Hand movements to pocket/waist AFTER handling merchandise are significant
    • Multiple quick concealment-like motions indicate theft attempts

    ⚠️ CONTEXTUAL DETECTION (CONFIDENCE 0.4-0.6):
    • Hand movement to body after item interaction (unclear if concealment)
    • Quick movements that could be concealment but partially obscured
    • Suspicious timing but not definitive visual evidence
    • Pattern suggests concealment but visual confirmation limited

    🔍 CRITICAL DISTINCTION:

    **NOT THEFT (Normal):** Hand to body for comfort, phone, adjustment BEFORE or WITHOUT handling merchandise
    **LIKELY THEFT:** Hand to pocket/waist AFTER picking up/handling merchandise

    **NOT THEFT (Normal):** Casual body touching during general browsing
    **LIKELY THEFT:** Body movements specifically after merchandise interaction

    **NOT THEFT (Normal):** Examining items and clearly placing back
    **LIKELY THEFT:** Item handled then hand moves to concealment area and item not visible

    📋 SURVEILLANCE-REALISTIC ANALYSIS:
    1. **Focus on behavioral sequences** rather than requiring perfect item visibility
    2. **Trust the pattern**: merchandise interaction → concealment motion → departure
    3. **Consider context** - hand to pocket AFTER handling items vs. general browsing
    4. **Behavioral evidence** is valid even if item visibility is limited

    🎯 EVIDENCE TIER CLASSIFICATION:
    • **TIER_1_HIGH**: Clear concealment sequence with strong theft indicators (0.75-0.95)
    • **TIER_2_MODERATE**: Strong behavioral pattern suggesting concealment (0.55-0.75)
    • **TIER_3_LOW**: Limited evidence suggesting possible concealment (0.35-0.55)
    • **NORMAL_BEHAVIOR**: Normal shopping behavior patterns (0.05-0.35)

    📊 STRUCTURED RESPONSE REQUIREMENTS:
    • **Shoplifting Detected**: True/False based on evidence
    • **Confidence Level**: Precise 0.0-1.0 rating
    • **Evidence Tier**: Classification based on strength of evidence
    • **Key Behaviors Observed**: List specific behavioral indicators you noticed
    • **Concealment Actions**: List any specific concealment behaviors (if observed)
    • **Risk Assessment**: Brief summary of the security risk level
    • **Decision Reasoning**: Detailed explanation of your analysis and decision

    Focus on BEHAVIORAL PATTERNS that indicate theft intention, not just perfect visual evidence of concealment.
    """

    default_response_schema = {
        "type": "object",
        "properties": {
            "Shoplifting Detected": {
                "type": "boolean",
                "description": "Whether shoplifting behavior was detected (true/false)"
            },
            "Confidence Level": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Confidence level from 0.0 to 1.0"
            },
            "Evidence Tier": {
                "type": "string",
                "enum": ["TIER_1_HIGH", "TIER_2_MODERATE", "TIER_3_LOW", "NORMAL_BEHAVIOR"],
                "description": "Classification of evidence strength"
            },
            "Key Behaviors Observed": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key behavioral indicators observed"
            },
            "Concealment Actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific concealment behaviors identified"
            },
            "Risk Assessment": {
                "type": "string",
                "maxLength": 300,
                "description": "Summary risk assessment and reasoning"
            },
            "Decision Reasoning": {
                "type": "string",
                "maxLength": 500,
                "description": "Detailed explanation of the decision logic"
            }
        },
        "required": [
            "Shoplifting Detected",
            "Confidence Level",
            "Evidence Tier",
            "Key Behaviors Observed",
            "Risk Assessment",
            "Decision Reasoning"
        ]
    }

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
            system_instruction = self.default_system_instruction

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
            prompt = self.unified_prompt

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
