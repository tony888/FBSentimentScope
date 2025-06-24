"""Text processing utility functions for Facebook Comment Analyzer."""

import re
import html
import unicodedata
from typing import List, Set, Optional, Union
import logging

logger = logging.getLogger(__name__)


class TextUtils:
    """Utility class for text processing and manipulation."""
    
    # Common social media text patterns
    URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    MENTION_PATTERN = re.compile(r'@[\w\._-]+')
    HASHTAG_PATTERN = re.compile(r'#[\w\._-]+')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'[\+]?[1-9]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}')
    
    # Common stopwords (basic set)
    ENGLISH_STOPWORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
        'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with'
    }
    
    @staticmethod
    def clean_text(text: str, remove_urls: bool = True, remove_mentions: bool = False,
                   remove_hashtags: bool = False, remove_extra_whitespace: bool = True) -> str:
        """Clean and normalize text for analysis.
        
        Args:
            text: Text to clean
            remove_urls: Whether to remove URLs
            remove_mentions: Whether to remove @mentions
            remove_hashtags: Whether to remove #hashtags
            remove_extra_whitespace: Whether to normalize whitespace
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove URLs
        if remove_urls:
            text = TextUtils.URL_PATTERN.sub('', text)
        
        # Remove mentions
        if remove_mentions:
            text = TextUtils.MENTION_PATTERN.sub('', text)
        
        # Remove hashtags
        if remove_hashtags:
            text = TextUtils.HASHTAG_PATTERN.sub('', text)
        
        # Normalize whitespace
        if remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize Unicode characters in text.
        
        Args:
            text: Text to normalize
            
        Returns:
            Unicode-normalized text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Normalize Unicode to NFD (canonical decomposition)
        text = unicodedata.normalize('NFD', text)
        
        # Remove combining characters (accents, etc.) if needed
        # text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        return text
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text.
        
        Args:
            text: Text to extract URLs from
            
        Returns:
            List of URLs found in text
        """
        if not isinstance(text, str):
            return []
        
        return TextUtils.URL_PATTERN.findall(text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract @mentions from text.
        
        Args:
            text: Text to extract mentions from
            
        Returns:
            List of mentions found in text (without @)
        """
        if not isinstance(text, str):
            return []
        
        mentions = TextUtils.MENTION_PATTERN.findall(text)
        return [mention[1:] for mention in mentions]  # Remove @ prefix
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract #hashtags from text.
        
        Args:
            text: Text to extract hashtags from
            
        Returns:
            List of hashtags found in text (without #)
        """
        if not isinstance(text, str):
            return []
        
        hashtags = TextUtils.HASHTAG_PATTERN.findall(text)
        return [hashtag[1:] for hashtag in hashtags]  # Remove # prefix
    
    @staticmethod
    def remove_stopwords(text: str, stopwords: Optional[Set[str]] = None, 
                        language: str = 'english') -> str:
        """Remove stopwords from text.
        
        Args:
            text: Text to process
            stopwords: Custom set of stopwords (optional)
            language: Language for default stopwords
            
        Returns:
            Text with stopwords removed
        """
        if not isinstance(text, str):
            text = str(text)
        
        if stopwords is None:
            if language.lower() == 'english':
                stopwords = TextUtils.ENGLISH_STOPWORDS
            else:
                logger.warning(f"No default stopwords for language: {language}")
                stopwords = set()
        
        words = text.lower().split()
        filtered_words = [word for word in words if word not in stopwords]
        
        return ' '.join(filtered_words)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """Truncate text to a maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length of text
            suffix: Suffix to add if text is truncated
            
        Returns:
            Truncated text
        """
        if not isinstance(text, str):
            text = str(text)
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        if not isinstance(text, str):
            text = str(text)
        
        return len(text.split())
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """Count characters in text.
        
        Args:
            text: Text to count characters in
            include_spaces: Whether to include spaces in count
            
        Returns:
            Number of characters
        """
        if not isinstance(text, str):
            text = str(text)
        
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(' ', ''))
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text.
        
        Args:
            text: Text to extract emails from
            
        Returns:
            List of email addresses found
        """
        if not isinstance(text, str):
            return []
        
        return TextUtils.EMAIL_PATTERN.findall(text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers from text.
        
        Args:
            text: Text to extract phone numbers from
            
        Returns:
            List of phone numbers found
        """
        if not isinstance(text, str):
            return []
        
        return TextUtils.PHONE_PATTERN.findall(text)
    
    @staticmethod
    def is_emoji(character: str) -> bool:
        """Check if a character is an emoji.
        
        Args:
            character: Character to check
            
        Returns:
            True if character is an emoji
        """
        return character in (
            '\U0001F600-\U0001F64F'  # emoticons
            '\U0001F300-\U0001F5FF'  # symbols & pictographs
            '\U0001F680-\U0001F6FF'  # transport & map symbols
            '\U0001F1E0-\U0001F1FF'  # flags (iOS)
            '\U00002700-\U000027BF'  # dingbats
        )
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        """Remove emojis from text.
        
        Args:
            text: Text to remove emojis from
            
        Returns:
            Text without emojis
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove emojis using regex
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002700-\U000027BF"  # dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.sub('', text)
    
    @staticmethod
    def detect_language_simple(text: str) -> str:
        """Simple language detection based on character patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code ('en', 'th', 'unknown')
        """
        if not isinstance(text, str) or not text.strip():
            return 'unknown'
        
        text = text.strip()
        
        # Check for Thai characters
        thai_chars = sum(1 for char in text if '\u0e00' <= char <= '\u0e7f')
        thai_ratio = thai_chars / len(text)
        
        if thai_ratio > 0.1:  # More than 10% Thai characters
            return 'th'
        
        # Default to English for Latin characters
        latin_chars = sum(1 for char in text if char.isascii())
        latin_ratio = latin_chars / len(text)
        
        if latin_ratio > 0.7:  # More than 70% ASCII characters
            return 'en'
        
        return 'unknown'
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize a filename by removing invalid characters.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = 'unnamed'
        
        return filename
