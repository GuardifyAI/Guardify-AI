"""
Shared behavioral indicators for shoplifting detection analysis.

This module provides centralized behavioral indicators that are used across
the AI analysis pipeline and summary generation systems.
"""

# Theft-related behavioral indicators
THEFT_INDICATORS = [
    'pocket', 'bag', 'waist', 'concealed', 'hidden', 'tucked',
    'clothing adjustment', 'hand movement', 'body area', 'conceal',
    'nervous', 'furtive', 'quick', 'suspicious', 'concealment'
]

# Normal shopping behavioral indicators
NORMAL_INDICATORS = [
    'browsing', 'examining', 'looking', 'normal', 'casual',
    'no clear', 'no visible', 'ambiguous', 'consistent with normal',
    'returned', 'shelf', 'checkout', 'natural', 'regular'
]