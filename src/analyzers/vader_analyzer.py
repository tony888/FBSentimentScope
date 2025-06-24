"""
VADER sentiment analyzer implementation.

This module provides English sentiment analysis using the VADER
(Valence Aware Dictionary and sEntiment Reasoner) algorithm.
"""

from typing import List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.base_analyzer import SentimentAnalyzer
from core.models import SentimentScore, Language
from core.exceptions import SentimentAnalysisError


class VaderSentimentAnalyzer(SentimentAnalyzer):
    """
    VADER-based sentiment analyzer for English text.
    
    VADER is specifically attuned to sentiments expressed in social media text
    and works well on social media text, news articles, movie reviews, 
    product reviews, etc.
    """
    
    def __init__(self):
        """Initialize VADER sentiment analyzer."""
        try:
            self.analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            raise SentimentAnalysisError(f"Failed to initialize VADER analyzer: {e}")
    
    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            SentimentScore: Detailed sentiment analysis results
        """
        if not text or not text.strip():
            return SentimentScore(
                compound=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                confidence=1.0,
                method=self.get_analyzer_name()
            )
        
        try:
            # Get VADER scores
            scores = self.analyzer.polarity_scores(text)
            
            # Calculate confidence based on the distance from neutral
            confidence = abs(scores['compound'])
            
            return SentimentScore(
                compound=scores['compound'],
                positive=scores['pos'],
                negative=scores['neg'],
                neutral=scores['neu'],
                confidence=confidence,
                analyzer_used=self.get_analyzer_name()
            )
            
        except Exception as e:
            raise SentimentAnalysisError(f"VADER analysis failed: {e}")
    
    def get_supported_languages(self) -> List[Language]:
        """
        Get languages supported by VADER analyzer.
        
        Returns:
            List[Language]: Supported languages (English only)
        """
        return [Language.ENGLISH]
    
    def get_analyzer_name(self) -> str:
        """
        Get analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "vader"
    
    def analyze_with_details(self, text: str) -> dict:
        """
        Get detailed VADER analysis including individual component scores.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Detailed analysis results
        """
        if not text or not text.strip():
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neg': 0.0,
                'neu': 1.0,
                'word_scores': []
            }
        
        try:
            scores = self.analyzer.polarity_scores(text)
            
            # Add word-level scores if available
            # Note: This is a simplified implementation
            # Full word-level analysis would require VADER internals
            word_scores = []
            words = text.split()
            for word in words:
                word_score = self.analyzer.polarity_scores(word)
                if abs(word_score['compound']) > 0.1:  # Only include significant words
                    word_scores.append({
                        'word': word,
                        'score': word_score['compound']
                    })
            
            return {
                'compound': scores['compound'],
                'pos': scores['pos'],
                'neg': scores['neg'],
                'neu': scores['neu'],
                'word_scores': word_scores
            }
            
        except Exception as e:
            raise SentimentAnalysisError(f"Detailed VADER analysis failed: {e}")


class EnhancedVaderAnalyzer(VaderSentimentAnalyzer):
    """
    Enhanced VADER analyzer with additional preprocessing and features.
    """
    
    def __init__(self, enable_emoji_boost: bool = True, enable_caps_boost: bool = True):
        """
        Initialize enhanced VADER analyzer.
        
        Args:
            enable_emoji_boost: Whether to boost sentiment for emojis
            enable_caps_boost: Whether to boost sentiment for capital letters
        """
        super().__init__()
        self.enable_emoji_boost = enable_emoji_boost
        self.enable_caps_boost = enable_caps_boost
        
        # Emoji sentiment mappings
        self.emoji_sentiment = {
            '😊': 0.5, '😃': 0.6, '😄': 0.7, '😁': 0.6, '😆': 0.5,
            '😍': 0.8, '🥰': 0.8, '😘': 0.7, '😗': 0.5, '😙': 0.5,
            '😚': 0.5, '🤗': 0.6, '🤩': 0.8, '😎': 0.6, '😋': 0.5,
            '😌': 0.3, '😉': 0.4, '🙂': 0.3, '👍': 0.5,
            '👏': 0.6, '🎉': 0.7, '✨': 0.5, '💕': 0.8, '❤️': 0.9,
            '💖': 0.8, '💝': 0.7, '🔥': 0.6, '⭐': 0.5, '🌟': 0.6,
            
            '😢': -0.6, '😭': -0.8, '😞': -0.5, '😔': -0.4, '😟': -0.4,
            '😕': -0.3, '🙁': -0.3, '😣': -0.5, '😖': -0.6, '😫': -0.7,
            '😩': -0.6, '😤': -0.5, '😠': -0.7, '😡': -0.8, '🤬': -0.9,
            '😱': -0.6, '😨': -0.5, '😰': -0.6, '😥': -0.4, '😪': -0.3,
            '🤮': -0.8, '🤢': -0.7, '😷': -0.3, '🤒': -0.4, '🤕': -0.5,
            '👎': -0.5, '💔': -0.8, '😵': -0.6, '👹': -0.7, '💀': -0.8
        }
    
    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment with enhancements.
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            SentimentScore: Enhanced sentiment analysis results
        """
        # Get base VADER analysis
        base_result = super().analyze(text)
        
        if not text or not text.strip():
            return base_result
        
        # Apply enhancements
        enhanced_compound = base_result.compound
        
        # Emoji boost
        if self.enable_emoji_boost:
            emoji_boost = self._calculate_emoji_sentiment(text)
            enhanced_compound += emoji_boost * 0.3  # 30% weight for emoji sentiment
        
        # Caps boost
        if self.enable_caps_boost:
            caps_boost = self._calculate_caps_boost(text)
            enhanced_compound *= (1 + caps_boost)
        
        # Ensure compound stays within bounds
        enhanced_compound = max(-1.0, min(1.0, enhanced_compound))
        
        # Update confidence based on enhancements
        confidence = min(1.0, base_result.confidence + abs(enhanced_compound - base_result.compound) * 0.5)
        
        return SentimentScore(
            compound=enhanced_compound,
            positive=base_result.positive,
            negative=base_result.negative,
            neutral=base_result.neutral,
            confidence=confidence,
            method=f"{self.get_analyzer_name()}_enhanced"
        )
    
    def _calculate_emoji_sentiment(self, text: str) -> float:
        """Calculate sentiment boost from emojis."""
        emoji_score = 0.0
        emoji_count = 0
        
        for char in text:
            if char in self.emoji_sentiment:
                emoji_score += self.emoji_sentiment[char]
                emoji_count += 1
        
        if emoji_count == 0:
            return 0.0
        
        return emoji_score / emoji_count
    
    def _calculate_caps_boost(self, text: str) -> float:
        """Calculate sentiment boost from capital letters."""
        if not text:
            return 0.0
        
        caps_count = sum(1 for c in text if c.isupper())
        total_letters = sum(1 for c in text if c.isalpha())
        
        if total_letters == 0:
            return 0.0
        
        caps_ratio = caps_count / total_letters
        
        # Moderate caps usage (20-60%) gives slight boost
        if 0.2 <= caps_ratio <= 0.6:
            return 0.1
        # High caps usage (>60%) gives stronger boost but not too much
        elif caps_ratio > 0.6:
            return 0.2
        
        return 0.0
    
    def get_analyzer_name(self) -> str:
        """
        Get analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "vader_enhanced"
