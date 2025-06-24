"""
Base classes and interfaces for sentiment analyzers.

This module defines the abstract interfaces that all sentiment analyzers
must implement to ensure consistency across different analysis methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, TYPE_CHECKING
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    from core.models import AnalysisResult

from core.models import SentimentScore, Language


class SentimentAnalyzer(ABC):
    """
    Abstract base class for sentiment analyzers.
    
    All sentiment analyzers must implement this interface to ensure
    consistent behavior across different analysis methods.
    """
    
    @abstractmethod
    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment of the given text.
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            SentimentScore: Detailed sentiment analysis results
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[Language]:
        """
        Get list of languages supported by this analyzer.
        
        Returns:
            List[Language]: Supported languages
        """
        pass
    
    @abstractmethod
    def get_analyzer_name(self) -> str:
        """
        Get the name/identifier of this analyzer.
        
        Returns:
            str: Analyzer name
        """
        pass
    
    def can_analyze_language(self, language: Language) -> bool:
        """
        Check if this analyzer can analyze the given language.
        
        Args:
            language: Language to check
            
        Returns:
            bool: True if language is supported
        """
        return language in self.get_supported_languages()
    
    def batch_analyze(self, texts: List[str]) -> List[SentimentScore]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List[SentimentScore]: List of sentiment analysis results
        """
        return [self.analyze(text) for text in texts]


class LanguageAnalyzer(ABC):
    """
    Abstract base class for language detection analyzers.
    """
    
    @abstractmethod
    def detect_language(self, text: str) -> Language:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze for language
            
        Returns:
            Language: Detected language
        """
        pass
    
    @abstractmethod
    def get_confidence(self, text: str) -> float:
        """
        Get confidence score for language detection.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        pass
    
    def batch_detect(self, texts: List[str]) -> List[Language]:
        """
        Detect languages for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List[Language]: List of detected languages
        """
        return [self.detect_language(text) for text in texts]


class MultiLanguageAnalyzer:
    """
    Combines multiple sentiment analyzers to handle different languages.
    """
    
    def __init__(self, language_detector: LanguageAnalyzer):
        """
        Initialize multi-language analyzer.
        
        Args:
            language_detector: Language detection analyzer
        """
        self.language_detector = language_detector
        self.analyzers: Dict[Language, SentimentAnalyzer] = {}
    
    def register_analyzer(self, language: Language, analyzer: SentimentAnalyzer) -> None:
        """
        Register a sentiment analyzer for a specific language.
        
        Args:
            language: Language the analyzer supports
            analyzer: Sentiment analyzer instance
        """
        self.analyzers[language] = analyzer
    
    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment using the appropriate language-specific analyzer.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentScore: Sentiment analysis results
        """
        # Detect language
        detected_language = self.language_detector.detect_language(text)
        
        # Get appropriate analyzer
        analyzer = self.analyzers.get(detected_language)
        
        # Fallback to English analyzer if specific language not available
        if analyzer is None:
            analyzer = self.analyzers.get(Language.ENGLISH)
        
        # If still no analyzer, raise error
        if analyzer is None:
            raise ValueError(f"No analyzer available for language: {detected_language}")
        
        # Perform analysis
        result = analyzer.analyze(text)
        
        # Add detected language info
        result.analyzer_used = f"{analyzer.get_analyzer_name()}_{detected_language.value}"
        
        return result
    
    def get_available_languages(self) -> List[Language]:
        """
        Get list of languages supported by registered analyzers.
        
        Returns:
            List[Language]: Supported languages
        """
        return list(self.analyzers.keys())
    
    def batch_analyze(self, texts: List[str]) -> List[SentimentScore]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List[SentimentScore]: List of sentiment analysis results
        """
        return [self.analyze(text) for text in texts]
    
    def analyze_post(self, post) -> 'AnalysisResult':
        """
        Analyze a post and its comments for sentiment.
        
        Args:
            post: Post object containing content and comments
            
        Returns:
            AnalysisResult with sentiment analysis for post and comments
        """
        from core.models import AnalysisResult
        
        # Analyze post content
        post_sentiment = None
        if post.content:
            post_sentiment = self.analyze(post.content)
        
        # Analyze comments
        comment_sentiments = []
        for comment in post.comments:
            if comment.content:
                comment_sentiment = self.analyze(comment.content)
                comment_sentiments.append(comment_sentiment)
            else:
                comment_sentiments.append(None)
        
        return AnalysisResult(
            post=post,
            post_sentiment=post_sentiment,
            comment_sentiments=comment_sentiments
        )
