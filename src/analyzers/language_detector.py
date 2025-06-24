"""
Language detection utilities.

This module provides language detection capabilities for determining
whether text is in English, Thai, or a mix of languages.
"""

import re
from typing import Dict, Tuple
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.base_analyzer import LanguageAnalyzer
from core.models import Language
from core.exceptions import LanguageDetectionError


class TextLanguageDetector(LanguageAnalyzer):
    """
    Rule-based language detector for Thai and English text.
    
    Uses character set analysis and pattern matching to determine
    the primary language of input text.
    """
    
    def __init__(self):
        """Initialize language detector."""
        # Thai Unicode range: U+0E00–U+0E7F
        self.thai_pattern = re.compile(r'[\u0e00-\u0e7f]')
        
        # English pattern (basic ASCII letters)
        self.english_pattern = re.compile(r'[a-zA-Z]')
        
        # Common English words for additional validation
        self.common_english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'can', 'may', 'might', 'this', 'that', 'these', 'those',
            'a', 'an', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
            'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its',
            'our', 'their', 'good', 'bad', 'great', 'nice', 'love', 'like',
            'hate', 'happy', 'sad', 'beautiful', 'ugly', 'big', 'small'
        }
        
        # Common Thai words for additional validation
        self.common_thai_words = {
            'และ', 'หรือ', 'แต่', 'ใน', 'บน', 'ที่', 'เพื่อ', 'ของ', 'กับ',
            'โดย', 'เป็น', 'คือ', 'มี', 'ได้', 'ทำ', 'จะ', 'ไป', 'มา', 'นี้',
            'นั้น', 'เหล่านี้', 'เหล่านั้น', 'ฉัน', 'คุณ', 'เขา', 'เธอ', 'มัน',
            'เรา', 'พวกเขา', 'ผม', 'ดิฉัน', 'ของ', 'ดี', 'เลว', 'ยอดเยี่ยม',
            'สวย', 'รัก', 'ชอบ', 'เกลียด', 'มีความสุข', 'เศร้า', 'ใหญ่', 'เล็ก'
        }
    
    def detect_language(self, text: str) -> Language:
        """
        Detect the primary language of the text.
        
        Args:
            text: Text to analyze for language
            
        Returns:
            Language: Detected language
        """
        if not text or not text.strip():
            return Language.UNKNOWN
        
        try:
            # Calculate character ratios
            thai_ratio, english_ratio, other_ratio = self._calculate_character_ratios(text)
            
            # Calculate word-based confidence
            thai_word_confidence = self._calculate_thai_word_confidence(text)
            english_word_confidence = self._calculate_english_word_confidence(text)
            
            # Combine character and word analysis
            thai_score = thai_ratio * 0.7 + thai_word_confidence * 0.3
            english_score = english_ratio * 0.7 + english_word_confidence * 0.3
            
            # Decision logic
            if thai_score >= 0.3 and english_score >= 0.3:
                return Language.MIXED
            elif thai_score > english_score and thai_score >= 0.2:
                return Language.THAI
            elif english_score > thai_score and english_score >= 0.3:
                return Language.ENGLISH
            elif thai_score > 0.1 or english_score > 0.1:
                # If there's some language content but not enough, return mixed
                return Language.MIXED
            else:
                return Language.UNKNOWN
        
        except Exception as e:
            raise LanguageDetectionError(f"Language detection failed: {e}")
    
    def get_confidence(self, text: str) -> float:
        """
        Get confidence score for language detection.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        if not text or not text.strip():
            return 1.0  # High confidence for empty text being unknown
        
        try:
            # Calculate character ratios
            thai_ratio, english_ratio, other_ratio = self._calculate_character_ratios(text)
            
            # Calculate word-based confidence
            thai_word_confidence = self._calculate_thai_word_confidence(text)
            english_word_confidence = self._calculate_english_word_confidence(text)
            
            # Combine scores
            thai_score = thai_ratio * 0.7 + thai_word_confidence * 0.3
            english_score = english_ratio * 0.7 + english_word_confidence * 0.3
            
            # Confidence is based on how clearly one language dominates
            max_score = max(thai_score, english_score)
            min_score = min(thai_score, english_score)
            
            # If scores are very close, confidence is low (mixed language)
            if max_score - min_score < 0.2:
                return 0.6  # Moderate confidence for mixed content
            
            # High confidence if one language clearly dominates
            return min(1.0, max_score * 1.2)
        
        except Exception:
            return 0.0
    
    def _calculate_character_ratios(self, text: str) -> Tuple[float, float, float]:
        """
        Calculate ratios of Thai, English, and other characters.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple[float, float, float]: Thai ratio, English ratio, Other ratio
        """
        if not text:
            return 0.0, 0.0, 0.0
        
        # Count characters
        thai_chars = len(self.thai_pattern.findall(text))
        english_chars = len(self.english_pattern.findall(text))
        
        # Count only printable characters (exclude whitespace and punctuation)
        printable_chars = sum(1 for char in text if char.isprintable() and not char.isspace())
        
        if printable_chars == 0:
            return 0.0, 0.0, 0.0
        
        thai_ratio = thai_chars / printable_chars
        english_ratio = english_chars / printable_chars
        other_ratio = max(0.0, 1.0 - thai_ratio - english_ratio)
        
        return thai_ratio, english_ratio, other_ratio
    
    def _calculate_thai_word_confidence(self, text: str) -> float:
        """
        Calculate confidence based on Thai word presence.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: Thai word confidence (0.0 to 1.0)
        """
        words = text.lower().split()
        if not words:
            return 0.0
        
        thai_word_count = sum(1 for word in words if word in self.common_thai_words)
        return min(1.0, thai_word_count / len(words) * 2)  # Boost the signal
    
    def _calculate_english_word_confidence(self, text: str) -> float:
        """
        Calculate confidence based on English word presence.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: English word confidence (0.0 to 1.0)
        """
        # Remove punctuation and convert to lowercase
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = cleaned_text.split()
        
        if not words:
            return 0.0
        
        english_word_count = sum(1 for word in words if word in self.common_english_words)
        return min(1.0, english_word_count / len(words) * 2)  # Boost the signal
    
    def get_language_breakdown(self, text: str) -> Dict[str, float]:
        """
        Get detailed breakdown of language composition.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict[str, float]: Language breakdown with percentages
        """
        if not text or not text.strip():
            return {'unknown': 100.0, 'thai': 0.0, 'english': 0.0, 'other': 0.0}
        
        try:
            thai_ratio, english_ratio, other_ratio = self._calculate_character_ratios(text)
            thai_word_conf = self._calculate_thai_word_confidence(text)
            english_word_conf = self._calculate_english_word_confidence(text)
            
            # Combine character and word analysis
            thai_score = (thai_ratio * 0.7 + thai_word_conf * 0.3) * 100
            english_score = (english_ratio * 0.7 + english_word_conf * 0.3) * 100
            other_score = other_ratio * 100
            
            # Normalize to ensure total is 100%
            total = thai_score + english_score + other_score
            if total > 0:
                thai_score = (thai_score / total) * 100
                english_score = (english_score / total) * 100
                other_score = (other_score / total) * 100
            
            return {
                'thai': round(thai_score, 2),
                'english': round(english_score, 2),
                'other': round(other_score, 2),
                'mixed': round(min(thai_score, english_score) * 2, 2) if thai_score > 20 and english_score > 20 else 0.0
            }
        
        except Exception:
            return {'unknown': 100.0, 'thai': 0.0, 'english': 0.0, 'other': 0.0}
    
    def is_thai_dominant(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is Thai-dominant.
        
        Args:
            text: Text to check
            threshold: Minimum ratio for Thai dominance
            
        Returns:
            bool: True if Thai is dominant language
        """
        detected = self.detect_language(text)
        return detected == Language.THAI
    
    def is_english_dominant(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is English-dominant.
        
        Args:
            text: Text to check
            threshold: Minimum ratio for English dominance
            
        Returns:
            bool: True if English is dominant language
        """
        detected = self.detect_language(text)
        return detected == Language.ENGLISH
    
    def is_mixed_language(self, text: str) -> bool:
        """
        Check if text contains mixed languages.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text contains mixed languages
        """
        detected = self.detect_language(text)
        return detected == Language.MIXED


# Convenience function for quick language detection
def detect_text_language(text: str) -> Language:
    """
    Quick language detection function.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language: Detected language
    """
    detector = TextLanguageDetector()
    return detector.detect_language(text)
