from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, List, Optional, Union
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType, \
    GenerationResponse
from typing import Tuple
import os
import json
from data_science.src.utils import load_env_variables

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

    default_system_instruction = [
        "You are an elite retail security analyst with 15+ years of specialized experience in shoplifting detection.",
        "Your expertise lies in analyzing detailed surveillance observations to make accurate theft determinations.",
        "You excel at distinguishing between normal shopping behaviors and genuine theft patterns.",
        "You understand that surveillance videos capture partial sequences and you can assess risk from behavioral evidence.",
        "Your decisions are based on proven behavioral indicators and you balance security needs with customer experience.",
        "You provide confidence-based assessments that help security teams make informed intervention decisions.",
        "Your goal is accurate threat assessment that minimizes both false positives and false negatives.",
        "You understand the difference between brief normal interactions and deliberate concealment behaviors."
    ]

    enhanced_analysis_prompt = """
    You are an expert retail security analyst making theft detection decisions based on detailed surveillance observations.

    🎯 PRIMARY OBJECTIVES:
    1. ACCURATELY DETECT genuine shoplifting behavior
    2. PROTECT normal shopping customers from false accusations
    3. PROVIDE reliable confidence assessments for security teams

    🛍️ FUNDAMENTAL UNDERSTANDING: 
    • 95% of customer interactions are NORMAL SHOPPING behaviors
    • Theft requires deliberate concealment intent, not just brief interactions
    • Surveillance cameras can detect behavioral patterns even with limited item visibility

    📋 ENHANCED DECISION FRAMEWORK:

    **🚨 TIER 1 - HIGH CONFIDENCE THEFT (0.75-0.95):**
    Detailed observations show:
    • Clear item pickup → concealment motion → departure sequence
    • Multiple items systematically moved to concealment areas  
    • "Grab and stuff" patterns with clear concealment intent
    • Items visibly placed in pockets, bags, waistband, or clothing
    • Body positioning deliberately blocking camera view during concealment
    • Removal of items from packaging with contents concealed

    **🔍 TIER 2 - MODERATE CONFIDENCE THEFT (0.55-0.75):**
    Observations indicate:
    • Item interaction followed by hand movements to typical concealment zones
    • Suspicious behavioral sequence suggesting concealment
    • Multiple quick movements toward body/clothing areas after handling items
    • Nervous behavior combined with concealment-type movements
    • Pattern of examining some items normally, concealing others

    **⚠️ TIER 3 - LOW CONFIDENCE SUSPICION (0.35-0.55):**
    Limited evidence suggests:
    • Unusual product handling that could facilitate concealment
    • Quick movements that might involve concealment (but unclear)
    • Some irregular behaviors but not definitively theft-related
    • Partially obscured actions that could be concealment

    **✅ NORMAL SHOPPING BEHAVIOR (0.05-0.35):**
    Observations clearly show:
    • Items examined and returned to proper shelf locations
    • Natural browsing, comparison shopping, or product examination
    • Hand movements for comfort, phone, or adjustment WITHOUT item interaction
    • Items moved toward checkout areas, shopping carts, or baskets
    • Regular shopping pace and natural body language
    • Brief item interactions consistent with normal browsing

    🔍 CRITICAL DECISION FACTORS:

    **Behavioral Sequence Analysis:**
    • THEFT PATTERN: Item pickup → concealment motion → departure
    • NORMAL PATTERN: Item pickup → examination → return to shelf OR carry to checkout
    • TIMING MATTERS: Hand-to-body movements AFTER handling merchandise are significant

    **Evidence Quality Assessment:**
    • High-quality evidence: Clear visual confirmation of concealment actions
    • Medium-quality evidence: Strong behavioral patterns suggesting concealment
    • Low-quality evidence: Unclear or ambiguous movements
    • Poor camera visibility should REDUCE confidence, not increase it

    **Context Evaluation:**
    • Duration and nature of item interactions
    • Overall behavioral patterns and body language
    • Environmental factors affecting observation quality
    • Consistency of behaviors throughout the sequence

    🎯 ENHANCED CONFIDENCE CALIBRATION:

    **High Confidence (0.70+)**: Multiple strong indicators present
    • Can you identify clear concealment actions from the observations?
    • Are there multiple supporting behavioral indicators?
    • Would this evidence warrant immediate security intervention?
    • Is the behavioral sequence clearly distinct from normal shopping?

    **Moderate Confidence (0.40-0.70)**: Some concerning evidence
    • Behavioral patterns suggest possible theft but aren't definitive
    • Some theft indicators present but missing clear visual confirmation
    • Evidence warrants closer monitoring or investigation

    **Low Confidence (0.05-0.40)**: Minimal or normal behavior
    • Behavior consistent with legitimate shopping
    • Brief interactions without clear concealment intent
    • Minor irregularities within normal shopping range

    🚨 SURVEILLANCE-REALISTIC DETECTION PRINCIPLES:

    **Trust Behavioral Evidence:**
    • Behavioral patterns are valid evidence even without perfect item visibility
    • Focus on the sequence: merchandise interaction → concealment motion → continuation
    • Hand movements to concealment areas after handling items are significant indicators

    **Distinguish Intent:**
    • NORMAL: Hand-to-body movements for comfort/convenience during general browsing
    • SUSPICIOUS: Hand-to-concealment areas specifically after merchandise interaction
    • NORMAL: Casual body touching during shopping
    • SUSPICIOUS: Deliberate concealment motions following item handling

    **Evidence Integration:**
    • Multiple weak indicators can combine to moderate confidence
    • Single strong indicator (clear concealment) can justify high confidence
    • Contradictory evidence should reduce overall confidence

    ⚖️ BALANCED ASSESSMENT STANDARDS:

    **Protection Against False Positives:**
    • Brief interactions are usually normal browsing, not theft
    • Hand movements for comfort/phone/adjustment are normal
    • Require evidence of concealment INTENT, not just movement

    **Protection Against False Negatives:**
    • Trust clear behavioral patterns indicating concealment
    • Don't dismiss theft evidence due to camera limitations
    • Recognize that shoplifting involves deliberate concealment behaviors

    🎯 DECISION THRESHOLD: Set "Shoplifting Detected" to TRUE if confidence ≥ 0.50

    📊 REQUIRED ANALYSIS OUTPUT:
    • Clear detection decision (true/false)
    • Calibrated confidence level (0.0-1.0)
    • Evidence tier classification
    • Key behavioral indicators observed
    • Specific concealment actions (if any)
    • Risk assessment summary

    Remember: Your analysis affects real people. False positives harm innocent customers; false negatives allow theft to continue. Focus on clear evidence and proven behavioral patterns for accurate assessment.
    """

    enhanced_response_schema = {
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
        temperature=0.05,  # Very low for consistent, analytical decisions
        top_p=0.8,  # Focused responses for decision-making
        top_k=20,  # Conservative vocabulary for analytical precision
        candidate_count=1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=enhanced_response_schema
    )

    # Set safety settings.
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

        super().__init__(model_name=model_name
                         , generation_config=generation_config
                         , safety_settings=safety_settings
                         , system_instruction=system_instruction
                         , labels=labels)

    def analyze_video_observations(self, video_file: Part, video_observations: str, prompt: str = None) -> Tuple[str, bool, float]:
        """
        Enhanced analysis method that processes detailed CV observations.
        
        Args:
            video_file (Part): Video file part object
            video_observations (str): Detailed observations from CV model
            prompt (str, optional): Custom analysis prompt
            
        Returns:
            Tuple[str, bool, float]: (full_response, shoplifting_detected, confidence_level)
        """
        if prompt is None:
            prompt = self.enhanced_analysis_prompt

        # Enhanced prompt with structured observations
        enhanced_prompt = prompt + "\n\nDETAILED SURVEILLANCE OBSERVATIONS TO ANALYZE:\n" + video_observations

        contents = [video_file, enhanced_prompt]

        # Generate analysis decision
        analysis_response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        shoplifting_detected, confidence_level = self._extract_values_from_response(analysis_response)
        return analysis_response.text, shoplifting_detected, confidence_level

    def analyze_structured_observations(self, video_file: Part, structured_observations: Dict[str, str]) -> Tuple[
        str, bool, float, Dict]:
        """
        Analyze structured observations from enhanced CV model.
        
        Args:
            video_file (Part): Video file part object
            structured_observations (Dict): Structured observations from CV model
            
        Returns:
            Tuple[str, bool, float, Dict]: (response_text, detected, confidence, detailed_analysis)
        """
        # Format structured observations for analysis
        formatted_observations = self._format_structured_observations(structured_observations)

        # Use enhanced analysis prompt with formatted observations
        enhanced_prompt = self.enhanced_analysis_prompt + "\n\nSTRUCTURED SURVEILLANCE OBSERVATIONS:\n" + formatted_observations

        contents = [video_file, enhanced_prompt]

        # Generate analysis
        response = self.generate_content(
            contents,
            generation_config=self._generation_config,
            safety_settings=self._safety_settings,
        )

        # Extract detailed results
        detected, confidence, detailed_analysis = self._extract_enhanced_response(response)

        return response.text, detected, confidence, detailed_analysis

    def _format_structured_observations(self, structured_obs: Dict[str, str]) -> str:
        """
        Format structured observations for analysis prompt.
        
        Args:
            structured_obs (Dict): Structured observations from CV model
            
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
            if key in structured_obs and structured_obs[key] != "Not found in observations":
                formatted.append(f"**{section_title}:**")
                formatted.append(structured_obs[key])
                formatted.append("")

        return "\n".join(formatted)

    def _extract_values_from_response(self, response: GenerationResponse) -> Tuple[bool, float]:
        """
        Extract basic values from analysis response.
        
        Args:
            response (GenerationResponse): Model response
            
        Returns:
            Tuple[bool, float]: (shoplifting_detected, confidence_level)
        """
        try:
            response_json = json.loads(response.text)
            shoplifting_detected = response_json["Shoplifting Detected"]
            confidence_level = response_json["Confidence Level"]

            # Enhanced logging if logger is available
            if hasattr(self, 'logger') and self.logger:
                evidence_tier = response_json.get("Evidence Tier", "UNKNOWN")
                key_behaviors = response_json.get("Key Behaviors Observed", [])
                concealment_actions = response_json.get("Concealment Actions", [])

                self.logger.debug(
                    f"Analysis Result: detected={shoplifting_detected}, confidence={confidence_level:.3f}")
                self.logger.debug(f"Evidence Tier: {evidence_tier}")
                self.logger.debug(f"Key Behaviors: {key_behaviors}")
                self.logger.debug(f"Concealment Actions: {concealment_actions}")

            return shoplifting_detected, confidence_level

        except (json.JSONDecodeError, KeyError) as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Failed to parse analysis response: {e}")
            # Return conservative defaults on parsing failure
            return False, 0.1

    def _extract_enhanced_response(self, response: GenerationResponse) -> Tuple[bool, float, Dict]:
        """
        Extract enhanced response with detailed analysis.
        
        Args:
            response (GenerationResponse): Model response
            
        Returns:
            Tuple[bool, float, Dict]: (detected, confidence, detailed_analysis)
        """
        try:
            response_json = json.loads(response.text)

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

    def make_surveillance_realistic_decision(self, confidences: List[float], detections: List[bool],
                                             detailed_analyses: List[Dict] = None) -> Tuple[float, bool, str]:
        """
        Enhanced decision-making logic with protection for strong theft evidence.
        
        Args:
            confidences (List[float]): List of confidence scores from iterations
            detections (List[bool]): List of detection results from iterations  
            detailed_analyses (List[Dict], optional): Detailed analysis results
            
        Returns:
            Tuple[float, bool, str]: (final_confidence, final_detection, reasoning)
        """
        if not confidences:
            return 0.1, False, "No analysis results available"

        avg_confidence = sum(confidences) / len(confidences)
        detection_count = sum(detections)
        detection_rate = detection_count / len(detections)

        # Check for strong theft evidence that should be protected from override
        strong_theft_evidence = False
        if detailed_analyses:
            # Look for clear theft patterns in reasoning
            theft_patterns = [
                "classic", "grab and stuff", "concealment", "theft pattern",
                "clear concealment", "definitive", "obvious", "pocket", "bag", "hidden"
            ]

            for analysis in detailed_analyses:
                reasoning = analysis.get("decision_reasoning", "").lower()
                concealment_actions = analysis.get("concealment_actions", [])
                evidence_tier = analysis.get("evidence_tier", "")

                # Strong evidence indicators
                if (any(pattern in reasoning for pattern in theft_patterns) or
                        concealment_actions or
                        evidence_tier in ["TIER_1_HIGH", "TIER_2_MODERATE"]):
                    strong_theft_evidence = True
                    break

        # Enhanced decision logic
        if detection_rate >= 0.8 and avg_confidence >= 0.6:
            # High consistency and confidence - likely theft
            final_confidence = min(avg_confidence, 0.9)
            final_detection = True
            reasoning = f"High detection consistency ({detection_rate:.1%}) with strong confidence ({avg_confidence:.3f})"

        elif detection_rate >= 0.6 and avg_confidence >= 0.5:
            # Moderate consistency - likely theft but with some uncertainty
            final_confidence = avg_confidence * 0.9  # Slight reduction for uncertainty
            final_detection = True
            reasoning = f"Moderate detection consistency ({detection_rate:.1%}) with adequate confidence ({avg_confidence:.3f})"

        elif strong_theft_evidence and avg_confidence >= 0.4:
            # Strong theft evidence should not be overridden by low consistency
            final_confidence = avg_confidence
            final_detection = avg_confidence >= 0.5
            reasoning = f"Strong theft evidence detected, maintaining original assessment (confidence: {avg_confidence:.3f})"

        elif detection_rate <= 0.3 and avg_confidence <= 0.4:
            # Low detection rate and confidence - likely normal behavior
            final_confidence = min(avg_confidence, 0.3)
            final_detection = False
            reasoning = f"Low detection rate ({detection_rate:.1%}) and confidence ({avg_confidence:.3f}) - normal behavior"

        else:
            # Mixed signals - use average confidence with conservative approach
            final_confidence = avg_confidence * 0.8  # Conservative adjustment
            final_detection = final_confidence >= 0.5
            reasoning = f"Mixed signals - detection rate: {detection_rate:.1%}, confidence: {avg_confidence:.3f}, adjusted to {final_confidence:.3f}"

        return final_confidence, final_detection, reasoning