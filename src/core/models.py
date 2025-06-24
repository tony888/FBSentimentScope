"""
Core data models for the Facebook Comment Analyzer.

This module defines the primary data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SentimentLabel(Enum):
    """Enumeration for sentiment labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Language(Enum):
    """Enumeration for supported languages."""
    ENGLISH = "english"
    THAI = "thai"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class Comment:
    """
    Represents a Facebook comment with sentiment analysis results.
    
    Attributes:
        id: Unique identifier for the comment
        text: The comment text content
        author: Name of the comment author
        created_time: When the comment was created (ISO format)
        likes_count: Number of likes on the comment
        replies_count: Number of replies to the comment
        sentiment_score: Numerical sentiment score (-1 to 1)
        sentiment_label: Categorical sentiment label
        language: Detected language of the comment
        confidence: Confidence score for sentiment analysis
        analysis_method: Method used for sentiment analysis
    """
    id: str
    text: str
    author: str
    created_time: str
    likes_count: int = 0
    replies_count: int = 0
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[SentimentLabel] = None
    language: Optional[Language] = None
    confidence: Optional[float] = None
    analysis_method: Optional[str] = None
    
    def __post_init__(self):
        """Convert string enums to proper enum instances."""
        if isinstance(self.sentiment_label, str):
            self.sentiment_label = SentimentLabel(self.sentiment_label)
        if isinstance(self.language, str):
            self.language = Language(self.language)


@dataclass
class Post:
    """
    Represents a Facebook post.
    
    Attributes:
        id: Unique identifier for the post
        message: The post content/message
        created_time: When the post was created (ISO format)
        likes_count: Number of likes on the post
        comments_count: Total number of comments
        shares_count: Number of times the post was shared
        author: Name of the post author
        url: URL to the post (if available)
    """
    id: str
    message: str
    created_time: str
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    author: Optional[str] = None
    url: Optional[str] = None


@dataclass
class SentimentScore:
    """
    Detailed sentiment analysis results.
    
    Attributes:
        compound: Overall sentiment score (-1 to 1)
        positive: Positive sentiment component (0 to 1)
        negative: Negative sentiment component (0 to 1)
        neutral: Neutral sentiment component (0 to 1)
        confidence: Confidence in the analysis (0 to 1)
        method: Analysis method used
    """
    compound: float
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0
    confidence: float = 0.0
    method: str = "unknown"
    
    @property
    def label(self) -> SentimentLabel:
        """Get sentiment label based on compound score."""
        if self.compound >= 0.05:
            return SentimentLabel.POSITIVE
        elif self.compound <= -0.05:
            return SentimentLabel.NEGATIVE
        return SentimentLabel.NEUTRAL


@dataclass
class AnalysisResult:
    """
    Comprehensive analysis results for a set of comments.
    
    Attributes:
        total_comments: Total number of comments analyzed
        sentiment_distribution: Count of each sentiment category
        language_distribution: Count of each language detected
        average_sentiment: Average sentiment score
        most_positive_comment: Comment with highest positive sentiment
        most_negative_comment: Comment with lowest negative sentiment
        engagement_metrics: Various engagement statistics
        analysis_timestamp: When the analysis was performed
        post_id: ID of the analyzed post (if applicable)
    """
    total_comments: int
    sentiment_distribution: Dict[SentimentLabel, int] = field(default_factory=dict)
    language_distribution: Dict[Language, int] = field(default_factory=dict)
    average_sentiment: float = 0.0
    most_positive_comment: Optional[Comment] = None
    most_negative_comment: Optional[Comment] = None
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    post_id: Optional[str] = None
    
    @property
    def positive_percentage(self) -> float:
        """Calculate positive sentiment percentage."""
        if self.total_comments == 0:
            return 0.0
        positive_count = self.sentiment_distribution.get(SentimentLabel.POSITIVE, 0)
        return (positive_count / self.total_comments) * 100
    
    @property
    def negative_percentage(self) -> float:
        """Calculate negative sentiment percentage."""
        if self.total_comments == 0:
            return 0.0
        negative_count = self.sentiment_distribution.get(SentimentLabel.NEGATIVE, 0)
        return (negative_count / self.total_comments) * 100
    
    @property
    def neutral_percentage(self) -> float:
        """Calculate neutral sentiment percentage."""
        if self.total_comments == 0:
            return 0.0
        neutral_count = self.sentiment_distribution.get(SentimentLabel.NEUTRAL, 0)
        return (neutral_count / self.total_comments) * 100


@dataclass
class AnalysisConfig:
    """
    Configuration settings for sentiment analysis.
    
    Attributes:
        positive_threshold: Minimum score to be considered positive
        negative_threshold: Maximum score to be considered negative
        max_comments_per_request: Maximum comments to fetch per API call
        rate_limit_delay: Delay between API requests (seconds)
        include_replies: Whether to include comment replies
        min_comment_length: Minimum character length for analysis
        enable_emoji_analysis: Whether to analyze emojis for sentiment
    """
    positive_threshold: float = 0.05
    negative_threshold: float = -0.05
    max_comments_per_request: int = 100
    rate_limit_delay: float = 1.0
    include_replies: bool = False
    min_comment_length: int = 1
    enable_emoji_analysis: bool = True


@dataclass
class FacebookConfig:
    """
    Facebook API configuration.
    
    Attributes:
        app_id: Facebook App ID
        app_secret: Facebook App Secret
        access_token: Facebook Access Token
        api_version: Facebook Graph API version
        timeout: Request timeout in seconds
    """
    app_id: str
    app_secret: str
    access_token: str
    api_version: str = "v18.0"
    timeout: int = 30
    
    def __post_init__(self):
        """Validate required configuration."""
        if not self.access_token:
            raise ValueError("Facebook access token is required")
        if not self.app_id:
            raise ValueError("Facebook app ID is required")


@dataclass
class ExportConfig:
    """
    Configuration for data export.
    
    Attributes:
        format: Export format (csv, json, excel)
        include_raw_data: Whether to include raw comment data
        include_metadata: Whether to include analysis metadata
        output_directory: Directory for output files
        filename_prefix: Prefix for generated filenames
    """
    format: str = "csv"
    include_raw_data: bool = True
    include_metadata: bool = True
    output_directory: str = "."
    filename_prefix: str = "facebook_analysis"
