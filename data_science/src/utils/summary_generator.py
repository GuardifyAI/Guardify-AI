"""
Summary generation utilities for event descriptions.

This module contains functions for generating ultra-short summaries from 
video analysis results, using behavioral indicators and analysis data.
"""
from typing import List, Dict
from data_science.src.model.pipeline.shoplifting_analyzer import ShopliftingAnalyzer
from utils.logger_utils import create_logger
import nltk

# Create logger for summary generation
logger = create_logger("SummaryGenerator", "summary_generator.log")


def generate_event_description_summary(iteration_results: List[dict], decision_reasoning: str) -> str:
    """
    Generate a summary description for Event from iteration results.
    
    Args:
        iteration_results (List[Dict]): List of iteration analysis results
        decision_reasoning (str): Final decision reasoning
        
    Returns:
        str: Summarized description of the analysis for Event description
    """
    try:
        # Ensure required NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            logger.info("Downloading required NLTK data for summarization...")
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('stopwords', quiet=True)
            logger.info("NLTK data download completed.")
        
        try:
            # Collect all text content from iterations
            text_content = [f"Final Decision: {decision_reasoning}"]
            
            # Extract detailed analysis from each iteration
            for i, iteration in enumerate(iteration_results, 1):
                iteration_text = f"Iteration {i} Analysis: "
                
                # Add computer vision observations
                if 'cv_observations' in iteration:
                    iteration_text += f"Observations: {iteration['cv_observations']}. "
                
                # Add analysis response
                if 'analysis_response' in iteration:
                    iteration_text += f"Analysis: {iteration['analysis_response']}. "
                
                # Add detailed analysis reasoning if available
                if 'detailed_analysis' in iteration and isinstance(iteration['detailed_analysis'], dict):
                    detailed = iteration['detailed_analysis']
                    if 'decision_reasoning' in detailed:
                        iteration_text += f"Reasoning: {detailed['decision_reasoning']}. "
                    if 'key_behaviors' in detailed and detailed['key_behaviors']:
                        behaviors = ', '.join(detailed['key_behaviors']) if isinstance(detailed['key_behaviors'], list) else str(detailed['key_behaviors'])
                        iteration_text += f"Key Behaviors: {behaviors}. "
                    if 'evidence_tier' in detailed:
                        iteration_text += f"Evidence Level: {detailed['evidence_tier']}. "
                
                text_content.append(iteration_text)
            
            # Combine all text
            full_text = ' '.join(text_content)
            
            # Basic validation
            if not full_text or len(full_text.strip()) < 20:
                return decision_reasoning or "Analysis completed."
            
            # Generate ultra-short 6-word summary
            return create_short_summary(full_text, decision_reasoning, iteration_results)
            
        except Exception as summary_error:
            logger.warning(f"Summary generation failed: {summary_error}")
            # Fallback to simple short description
            return create_fallback_short_summary(decision_reasoning, iteration_results)
        
    except Exception as e:
        logger.warning(f"Failed to generate event description summary, using fallback: {e}")
        # Fallback: return decision reasoning + basic info
        fallback = f"Analysis Result: {decision_reasoning}"
        if iteration_results:
            fallback += f" Based on {len(iteration_results)} iteration(s) of detailed analysis."
        return fallback


def create_short_summary(full_text: str, decision_reasoning: str, iteration_results: List[dict]) -> str:
    """
    Create a 6-word summary from analysis results.
    
    Args:
        full_text (str): Combined text from all iterations
        decision_reasoning (str): Final decision reasoning
        iteration_results (List[dict]): Raw iteration data
        
    Returns:
        str: Ultra-short 6-word summary
    """
    # Extract key information
    detected = any('detected' in str(decision_reasoning).lower() for _ in [1])
    confidence_level = extract_confidence_level(decision_reasoning, iteration_results)
    behavior_type = extract_key_behavior(full_text, iteration_results)
    
    # Generate 6-word summary patterns
    if detected:
        if confidence_level == 'high':
            return f"Shoplifting detected: {behavior_type} behavior confirmed"
        elif confidence_level == 'medium':
            return f"Suspicious {behavior_type}: potential shoplifting detected"
        else:
            return f"Possible shoplifting: {behavior_type} observed"
    else:
        return f"Normal behavior: no theft detected"


def extract_confidence_level(decision_reasoning: str, iteration_results: List[dict]) -> str:
    """
    Extract confidence level from analysis.
    
    Returns:
        str: 'high', 'medium', or 'low'
    """
    text = (decision_reasoning or '').lower()
    
    # Check for high confidence indicators
    high_indicators = ['high confidence', 'strong evidence', 'clear indication', 'definitive']
    if any(indicator in text for indicator in high_indicators):
        return 'high'
    
    # Check evidence tier from iterations
    for iteration in iteration_results:
        if 'detailed_analysis' in iteration:
            evidence_tier = iteration['detailed_analysis'].get('evidence_tier', '').lower()
            if evidence_tier == 'high':
                return 'high'
            elif evidence_tier == 'medium':
                return 'medium'
    
    # Check for medium confidence indicators
    medium_indicators = ['likely', 'probable', 'suggests', 'indicates']
    if any(indicator in text for indicator in medium_indicators):
        return 'medium'
    
    return 'low'


def extract_key_behavior(full_text: str, iteration_results: List[dict]) -> str:
    """
    Extract the most relevant behavior type for the summary using ShopliftingAnalyzer indicators.
    
    Returns:
        str: Single word describing the key behavior
    """
    text = full_text.lower()
    
    # Check iteration results for key behaviors first (most specific)
    for iteration in iteration_results:
        if 'detailed_analysis' in iteration:
            key_behaviors = iteration['detailed_analysis'].get('key_behaviors', [])
            if key_behaviors:
                if isinstance(key_behaviors, list) and key_behaviors:
                    first_behavior = str(key_behaviors[0]).lower()
                    if 'conceal' in first_behavior or 'hide' in first_behavior:
                        return 'concealment'
                    elif 'nervous' in first_behavior or 'anxious' in first_behavior:
                        return 'nervous'
    
    # Use ShopliftingAnalyzer theft indicators for analysis
    theft_indicators = ShopliftingAnalyzer.THEFT_INDICATORS
    normal_indicators = ShopliftingAnalyzer.NORMAL_INDICATORS
    
    # Count matches for theft vs normal indicators
    theft_matches = sum(1 for indicator in theft_indicators if indicator.lower() in text)
    normal_matches = sum(1 for indicator in normal_indicators if indicator.lower() in text)
    
    # Determine behavior type based on strongest matches
    if theft_matches > normal_matches:
        # Find the most specific theft behavior
        for indicator in theft_indicators:
            if indicator.lower() in text:
                if indicator.lower() in ['concealed', 'hidden', 'tucked', 'conceal', 'pocket']:
                    return 'concealment'
                elif indicator.lower() in ['nervous', 'furtive', 'suspicious']:
                    return 'nervous'
                elif indicator.lower() in ['quick', 'hand movement']:
                    return 'movement'
        return 'suspicious'
    else:
        return 'activity'


def create_fallback_short_summary(decision_reasoning: str, iteration_results: List[dict]) -> str:
    """
    Create a simple fallback summary when main generation fails.
    
    Returns:
        str: Simple 4-6 word fallback summary
    """
    text = (decision_reasoning or '').lower()
    
    if 'detected' in text or 'theft' in text:
        return "Shoplifting activity detected"
    elif 'suspicious' in text:
        return "Suspicious behavior observed"
    elif 'normal' in text or 'no' in text:
        return "Normal customer behavior"
    else:
        return "Analysis completed successfully"