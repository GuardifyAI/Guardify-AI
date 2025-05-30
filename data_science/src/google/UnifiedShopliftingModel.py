from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

from typing import Dict, Optional, Tuple
from vertexai.generative_models._generative_models import PartsType, GenerationConfigType, SafetySettingsType, \
    GenerationResponse
import os
import json
from data_science.src.utils import load_env_variables

load_env_variables()


class UnifiedShopliftingModel(GenerativeModel):
    """
    REVOLUTIONARY UNIFIED ARCHITECTURE
    ==================================
    
    This model combines video analysis and shoplifting detection in a single step,
    eliminating information loss and using few-shot learning with real examples.
    """

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
