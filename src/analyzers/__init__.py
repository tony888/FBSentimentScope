"""Analyzers module for Facebook Comment Analyzer."""

from .base_analyzer import (
    SentimentAnalyzer,
    LanguageAnalyzer, 
    MultiLanguageAnalyzer
)

from .vader_analyzer import (
    VaderSentimentAnalyzer,
    EnhancedVaderAnalyzer
)

from .thai_analyzer import ThaiSentimentAnalyzer

from .language_detector import (
    TextLanguageDetector,
    detect_text_language
)

__all__ = [
    # Base classes
    'SentimentAnalyzer',
    'LanguageAnalyzer',
    'MultiLanguageAnalyzer',
    
    # Sentiment analyzers
    'VaderSentimentAnalyzer',
    'EnhancedVaderAnalyzer',
    'ThaiSentimentAnalyzer',
    
    # Language detection
    'TextLanguageDetector',
    'detect_text_language'
]
