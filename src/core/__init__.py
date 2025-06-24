"""Core module for Facebook Comment Analyzer."""

from .models import (
    Comment,
    Post,
    SentimentScore,
    AnalysisResult,
    AnalysisConfig,
    FacebookConfig,
    ExportConfig,
    SentimentLabel,
    Language
)

from .exceptions import (
    FacebookAnalyzerError,
    FacebookAPIError,
    AuthenticationError,
    RateLimitError,
    SentimentAnalysisError,
    ConfigurationError,
    DataValidationError,
    ExportError,
    VisualizationError,
    LanguageDetectionError
)

from .config import ConfigManager, load_config

__all__ = [
    # Models
    'Comment',
    'Post', 
    'SentimentScore',
    'AnalysisResult',
    'AnalysisConfig',
    'FacebookConfig',
    'ExportConfig',
    'SentimentLabel',
    'Language',
    
    # Exceptions
    'FacebookAnalyzerError',
    'FacebookAPIError',
    'AuthenticationError',
    'RateLimitError',
    'SentimentAnalysisError',
    'ConfigurationError',
    'DataValidationError',
    'ExportError',
    'VisualizationError',
    'LanguageDetectionError',
    
    # Configuration
    'ConfigManager',
    'load_config'
]
