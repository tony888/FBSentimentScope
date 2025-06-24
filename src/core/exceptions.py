"""
Custom exceptions for the Facebook Comment Analyzer.

This module defines application-specific exceptions to provide
better error handling and debugging information.
"""


class FacebookAnalyzerError(Exception):
    """Base exception for Facebook Comment Analyzer."""
    pass


class FacebookAPIError(FacebookAnalyzerError):
    """Raised when Facebook API requests fail."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(FacebookAPIError):
    """Raised when Facebook API authentication fails."""
    pass


class RateLimitError(FacebookAPIError):
    """Raised when Facebook API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class SentimentAnalysisError(FacebookAnalyzerError):
    """Raised when sentiment analysis fails."""
    pass


class ConfigurationError(FacebookAnalyzerError):
    """Raised when configuration is invalid or missing."""
    pass


class DataValidationError(FacebookAnalyzerError):
    """Raised when data validation fails."""
    pass


class ExportError(FacebookAnalyzerError):
    """Raised when data export fails."""
    pass


class VisualizationError(FacebookAnalyzerError):
    """Raised when visualization creation fails."""
    pass


class LanguageDetectionError(FacebookAnalyzerError):
    """Raised when language detection fails."""
    pass
