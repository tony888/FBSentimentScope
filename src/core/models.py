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
    Represents a Facebook comment.
    
    Attributes:
        id: Unique identifier for the comment
        content: The comment text content
        author: Name of the comment author
        created_time: When the comment was created
        likes_count: Number of likes on the comment
        replies_count: Number of replies to the comment
    """
    id: str
    content: str
    author: str
    created_time: Optional[datetime] = None
    likes_count: int = 0
    replies_count: int = 0


@dataclass
class Post:
    """
    Represents a Facebook post with its comments.
    
    Attributes:
        id: Unique identifier for the post
        content: The post content/message
        author: Name of the post author
        created_time: When the post was created
        likes_count: Number of likes on the post
        comments: List of comments on the post
        shares_count: Number of times the post was shared
        url: URL to the post (if available)
    """
    id: str
    content: str
    author: str
    created_time: Optional[datetime] = None
    likes_count: int = 0
    comments: List[Comment] = field(default_factory=list)
    shares_count: int = 0
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
        language: Language of the analyzed text
        analyzer_used: Name of the analyzer used
        confidence: Confidence in the analysis (0 to 1)
    """
    compound: float
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0
    language: Optional[str] = None
    analyzer_used: str = "unknown"
    confidence: float = 0.0
    
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
    Comprehensive analysis results for a post and its comments.
    
    Attributes:
        post: The analyzed post
        post_sentiment: Sentiment analysis of the post
        comment_sentiments: List of sentiment analysis for each comment
        analysis_timestamp: When the analysis was performed
        metadata: Additional metadata about the analysis
    """
    post: Post
    post_sentiment: Optional[SentimentScore] = None
    comment_sentiments: List[Optional[SentimentScore]] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_items(self) -> int:
        """Total number of items (post + comments) analyzed."""
        return 1 + len(self.post.comments)
    
    @property
    def sentiment_distribution(self) -> Dict[str, int]:
        """Distribution of sentiment labels."""
        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Count post sentiment
        if self.post_sentiment:
            label = self.post_sentiment.label.value
            distribution[label] += 1
        
        # Count comment sentiments
        for sentiment in self.comment_sentiments:
            if sentiment:
                label = sentiment.label.value
                distribution[label] += 1
        
        return distribution
    
    @property
    def average_sentiment(self) -> float:
        """Average sentiment score across all items."""
        scores = []
        
        if self.post_sentiment:
            scores.append(self.post_sentiment.compound)
        
        for sentiment in self.comment_sentiments:
            if sentiment:
                scores.append(sentiment.compound)
        
        return sum(scores) / len(scores) if scores else 0.0


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
