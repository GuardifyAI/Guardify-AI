from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, List, Optional
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType, \
    GenerationResponse
from typing import Tuple
import os
import json

from data_science.src.model.agentic.prompt_and_scheme.analysis_prompt import (default_system_instruction,
                                                                              enhanced_prompt, enhanced_response_schema)
from data_science.src.model.agentic.prompt_and_scheme.computer_vision_prompt import cv_observations_prompt
from utils import load_env_variables

load_env_variables()


class AnalysisModel(GenerativeModel):
    """
    ENHANCED ANALYSIS MODEL FOR AGENTIC ARCHITECTURE
    ===============================================
    
    This upgraded Analysis model processes detailed CV observations to make 
    intelligent theft detection decisions with enhanced accuracy.
    
    Key Improvements:
    - Enhanced decision logic with surveillance-realistic approach
    - Better integration with structured CV observations
    - Improved confidence calibration
    - Contextual override protection for strong evidence
    - Balanced approach preventing both false positives and false negatives
    """

    default_generation_config = GenerationConfig(
        temperature=0.05,  # Very low for consistent, analytical decisions
        top_p=0.8,  # Focused responses for decision-making
        top_k=20,  # Conservative vocabulary for analytical precision
        candidate_count=1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=enhanced_response_schema  # Output response schema of the generated candidate text
    )

    # Set safety settings.
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    def __init__(self,
                 # default to the DEFAULT_ANALYSIS_MODEL_ID environment variable if not provided. if also this is not provided, default to DEFAULT_MODEL_ID.
                 model_name: str = os.getenv("DEFAULT_ANALYSIS_MODEL_ID", os.getenv("DEFAULT_MODEL_ID")),
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

    def analyze_structured_observations(self, video_file: Part, structured_observations: Dict[str, str]) -> Tuple[
        str, bool, float, Dict]:
        """
        The main analyzer function - analyze structured observations from enhanced CV model.
        
        Args:
            video_file (Part): Video file part object
            structured_observations (Dict): Structured observations from CV model
            
        Returns:
            Tuple[str, bool, float, Dict]: (response_text, detected, confidence, detailed_analysis)
        """
        # Format structured observations for analysis
        formatted_observations = self._format_structured_observations(structured_observations)

        # Use enhanced analysis prompt_and_scheme with formatted observations
        updated_enhanced_prompt = (enhanced_prompt + "\n\n" + cv_observations_prompt + "\n\n" + formatted_observations)
        contents = [video_file, updated_enhanced_prompt]

        # Generate analysis
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        # Extract detailed results from model
        detected, confidence, detailed_analysis = self._extract_enhanced_response(response)

        return response.text, detected, confidence, detailed_analysis

    def _format_structured_observations(self, cv_structured_obs: Dict[str, str]) -> str:
        """
        Format structured observations for analysis prompt_and_scheme.
        
        Args:
            cv_structured_obs (Dict): Structured observations from CV model
            
        Returns:
            str: Formatted observations text
        """
        formatted = []

        section_mapping = {
            "person_description": "PERSON DESCRIPTION & MOVEMENTS",
            "item_interactions": "ITEM INTERACTION ANALYSIS",
            "hand_movements": "HAND MOVEMENT & BODY BEHAVIOR",
            "behavioral_sequence": "BEHAVIORAL SEQUENCE DOCUMENTATION",
            "environmental_context": "ENVIRONMENTAL CONTEXT",
            "suspicious_indicators": "SUSPICIOUS BEHAVIOR INDICATORS",
            "normal_indicators": "NORMAL SHOPPING INDICATORS"
        }

        for key, section_title in section_mapping.items():
            if key in cv_structured_obs and cv_structured_obs[key] != "Not found in observations":
                formatted.append(f"**{section_title}:**")

                # Handle array fields (suspicious_indicators, normal_indicators) properly
                if key in ["suspicious_indicators", "normal_indicators"]:
                    value = cv_structured_obs[key]
                    if isinstance(value, list):
                        if value:  # Non-empty list
                            formatted.append("\n".join(f"- {item}" for item in value))
                        else:  # Empty list
                            formatted.append("None observed")
                    else:  # Fallback for string representation
                        formatted.append(str(value))
                else:
                    # Handle string fields normally
                    formatted.append(str(cv_structured_obs[key]))

                formatted.append("")

        return "\n".join(formatted)

    def _extract_enhanced_response(self, model_response: GenerationResponse) -> Tuple[bool, float, Dict]:
        """
        Extract enhanced response with detailed analysis from model response.
        
        Args:
            model_response (GenerationResponse): Model response
            
        Returns:
            Tuple[bool, float, Dict]: (detected, confidence, detailed_analysis)
        """
        try:
            response_json = json.loads(model_response.text)

            detected = response_json["Shoplifting Detected"]
            confidence = response_json["Confidence Level"]

            detailed_analysis = {
                "evidence_tier": response_json.get("Evidence Tier", "UNKNOWN"),
                "key_behaviors": response_json.get("Key Behaviors Observed", []),
                "concealment_actions": response_json.get("Concealment Actions", []),
                "risk_assessment": response_json.get("Risk Assessment", ""),
                "decision_reasoning": response_json.get("Decision Reasoning", "")
            }

            return detected, confidence, detailed_analysis

        except (json.JSONDecodeError, KeyError) as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Failed to parse enhanced response: {e}")

            # Return conservative defaults
            return False, 0.1, {
                "evidence_tier": "ERROR",
                "key_behaviors": [],
                "concealment_actions": [],
                "risk_assessment": "Analysis failed",
                "decision_reasoning": f"Response parsing error: {e}"
            }

    def get_final_analysis_based_on_iterations_results(self,
                                                       confidences: List[float],
                                                       detections: List[bool],
                                                       shoplifting_detection_threshold: float,
                                                       detailed_analyses: List[Dict] = None) -> Tuple[float, bool, str]:
        """
        Enhanced decision-making logic with protection for strong theft evidence.

        Args:
            confidences (List[float]): List of confidence scores from iterations
            detections (List[bool]): List of detection results from iterations
            shoplifting_detection_threshold (float): Threshold for shoplifting detection strictness. affects both the wanted confidence and detection rate.
            detailed_analyses (List[Dict], optional): Detailed analysis results

        Returns:
            Tuple[float, bool, str]: (final_confidence, final_detection, reasoning)
        """
        if not confidences:
            return 0.1, False, "No analysis results available"

        avg_confidence = sum(confidences) / len(confidences)
        detection_rate = sum(detections) / len(detections)

        # Check for strong theft evidence that should be protected from override
        strong_theft_evidence = self._is_there_strong_theft_evidence(detailed_analyses)
        reasoning_of_iteration_with_confidence_closest_to_the_average_confidence = self._find_reasoning_near_avg_confidence(
            confidences, detailed_analyses)

        # Determine the final decision based on detection rate, confidence, and evidence strength.
        final_confidence, final_detection, reasoning_summary = self._get_detection_confidence_summary(
            detection_rate, avg_confidence, strong_theft_evidence, shoplifting_detection_threshold
        )

        final_reasoning = reasoning_of_iteration_with_confidence_closest_to_the_average_confidence + "\nFinal Decision Reasoning Summary: " + reasoning_summary
        return final_confidence, final_detection, final_reasoning

    def _is_there_strong_theft_evidence(self, detailed_analyses: List[Dict] = None) -> bool:
        """
        Check if there is strong theft evidence in the detailed analyses.

        Args:
            detailed_analyses (List[Dict], optional): Detailed analysis results.
        Returns:
            bool: True if strong theft evidence is found, False otherwise
        """
        if not detailed_analyses:
            return False

        for analysis in detailed_analyses:
            concealment_actions = analysis.get("concealment_actions", [])
            evidence_tier = analysis.get("evidence_tier", "")
            # Strong evidence indicators
            if concealment_actions or evidence_tier in ["TIER_1_HIGH", "TIER_2_MODERATE"]:
                return True
        else:
            return False

    def _find_reasoning_near_avg_confidence(self,
                                            confidences: List[float],
                                            detailed_analyses: List[Dict] = None) -> str:
        """
        Helper function to find the iteration with confidence closest to the average confidence
        and return its decision reasoning.

        Args:
            confidences (List[float]): List of confidence scores from iterations
            detailed_analyses (List[Dict], optional): Detailed analysis results

        Returns:
            str: Decision reasoning from the closest iteration, or empty string if not found
        """
        if not confidences or not detailed_analyses:
            return ""

            # Use only indices present in both lists
        n = min(len(confidences), len(detailed_analyses))
        if n == 0:
            return ""

        avg = sum(confidences) / len(confidences)

        closest_idx = min(range(n), key=lambda i: abs(confidences[i] - avg))
        reasoning = detailed_analyses[closest_idx].get("decision_reasoning", "")

        if reasoning:
            return reasoning

        # Fallback: first non-empty reasoning anywhere
        return next(
            (a.get("decision_reasoning") for a in detailed_analyses if a.get("decision_reasoning")),
            ""
        )

    def _get_detection_confidence_summary(self,
                                          detection_rate: float,
                                          avg_confidence: float,
                                          strong_theft_evidence: bool,
                                          shoplifting_detection_threshold: float) -> Tuple[float, bool, str]:
        """
        Determine the final decision based on detection rate, confidence, and evidence strength.

        Args:
            detection_rate (float): Ratio of detections to total iterations
            avg_confidence (float): Average confidence across all iterations
            strong_theft_evidence (bool): Whether strong theft evidence was detected
            shoplifting_detection_threshold (float): Threshold for shoplifting detection

        Returns:
            Tuple[float, bool, str]: (final_confidence, final_detection, reasoning_summary)
        """
        high_detection_likelihood_threshold = shoplifting_detection_threshold
        moderate_detection_likelihood_threshold = 0.8 * shoplifting_detection_threshold
        low_detection_likelihood_threshold = 0.5 * shoplifting_detection_threshold
        high_confidence_threshold = shoplifting_detection_threshold
        moderate_confidence_threshold = 0.8 * shoplifting_detection_threshold

        # Enhanced decision logic addressing high confidence scenarios
        if detection_rate >= high_detection_likelihood_threshold and avg_confidence >= high_confidence_threshold:
            # High consistency and confidence - likely theft
            final_confidence = min(avg_confidence, 0.9)
            final_detection = True
            reasoning_summary = f"High detection consistency ({detection_rate:.1%}) with strong confidence ({avg_confidence:.3f})"

        elif detection_rate >= moderate_detection_likelihood_threshold and avg_confidence >= moderate_confidence_threshold:
            # Moderate consistency - likely theft but with some uncertainty
            final_confidence = avg_confidence * 0.9  # Slight reduction for uncertainty
            final_detection = True
            reasoning_summary = f"Moderate detection consistency ({detection_rate:.1%}) with adequate confidence ({avg_confidence:.3f})"

        elif strong_theft_evidence and avg_confidence >= moderate_confidence_threshold:
            # Strong theft evidence should not be overridden by low consistency
            final_confidence = avg_confidence
            final_detection = True
            reasoning_summary = f"Strong theft evidence detected, maintaining original assessment (confidence: {avg_confidence:.3f})"

        elif detection_rate <= low_detection_likelihood_threshold and avg_confidence >= high_confidence_threshold:
            # Low detection rate but high confidence - likely normal behavior with high certainty
            final_confidence = avg_confidence
            final_detection = False
            reasoning_summary = f"Low detection rate ({detection_rate:.1%}) but high confidence ({avg_confidence:.3f}) - normal behavior with high certainty"

        elif detection_rate <= low_detection_likelihood_threshold and avg_confidence >= moderate_confidence_threshold:
            # Low detection rate with moderate confidence - likely normal behavior
            final_confidence = avg_confidence
            final_detection = False
            reasoning_summary = f"Low detection rate ({detection_rate:.1%}) with moderate confidence ({avg_confidence:.3f}) - normal behavior"

        elif detection_rate <= low_detection_likelihood_threshold and avg_confidence < moderate_confidence_threshold:
            # Low detection rate and low confidence - normal behavior but uncertain
            final_confidence = min(avg_confidence, 0.3)
            final_detection = False
            reasoning_summary = f"Low detection rate ({detection_rate:.1%}) and low confidence ({avg_confidence:.3f}) - normal behavior but uncertain"

        elif detection_rate >= moderate_detection_likelihood_threshold and avg_confidence < moderate_confidence_threshold:
            # Moderate detection rate but low confidence - mixed signals with theft suspicion
            final_confidence = avg_confidence * 0.8
            final_detection = False
            reasoning_summary = f"Moderate detection rate ({detection_rate:.1%}) but low confidence ({avg_confidence:.3f}) - mixed signals with theft suspicion"

        elif moderate_detection_likelihood_threshold > detection_rate > low_detection_likelihood_threshold and avg_confidence >= moderate_confidence_threshold:
            # Medium detection rate with moderate confidence - unclear but leaning toward theft
            final_confidence = avg_confidence * 0.85
            final_detection = avg_confidence >= shoplifting_detection_threshold
            reasoning_summary = f"Medium detection rate ({detection_rate:.1%}) with moderate confidence ({avg_confidence:.3f}) - unclear but leaning toward theft"

        else:
            # Mixed signals - use average confidence with conservative approach
            final_confidence = avg_confidence * 0.8  # Conservative adjustment
            final_detection = False
            reasoning_summary = f"Mixed signals - detection rate: {detection_rate:.1%}, confidence: {avg_confidence:.3f}, adjusted to {final_confidence:.3f}"

        return final_confidence, final_detection, reasoning_summary
