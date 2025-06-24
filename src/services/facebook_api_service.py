"""
Facebook API Service for fetching posts and comments.

This module provides a comprehensive interface to the Facebook Graph API
for retrieving posts, comments, and related data with proper error handling
and rate limiting.
"""

import requests
import time
import json
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime, timezone
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import Comment, Post, FacebookConfig
from core.exceptions import (
    FacebookAPIError, 
    AuthenticationError, 
    RateLimitError,
    DataValidationError
)


class FacebookAPIService:
    """
    Service for interacting with Facebook Graph API.
    
    Provides methods to fetch posts and comments with proper error handling,
    rate limiting, and data validation.
    """
    
    def __init__(self, config: FacebookConfig):
        """
        Initialize Facebook API service.
        
        Args:
            config: Facebook API configuration
        """
        self.config = config
        self.base_url = f"https://graph.facebook.com/{config.api_version}"
        self.session = requests.Session()
        self.session.timeout = config.timeout
        
        # Rate limiting
        self.last_request_time = 0.0
        self.min_request_interval = 0.5  # Minimum seconds between requests
        
        # Validate configuration on initialization
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate Facebook API configuration."""
        if not self.config.access_token:
            raise AuthenticationError("Facebook access token is required")
        
        if not self.config.app_id:
            raise AuthenticationError("Facebook app ID is required")
    
    def test_connection(self) -> bool:
        """
        Test Facebook API connection and token validity.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            AuthenticationError: If authentication fails
            FacebookAPIError: If API request fails
        """
        try:
            url = f"{self.base_url}/me"
            response = self._make_request(url, {"fields": "id,name"})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connected to Facebook API as: {data.get('name', 'Unknown')}")
                return True
            else:
                error_data = response.json() if response.content else {}
                raise AuthenticationError(f"Token validation failed: {error_data}")
                
        except requests.RequestException as e:
            raise FacebookAPIError(f"Connection test failed: {e}")
    
    def fetch_posts_from_page(self, page_id: str, limit: int = 10) -> List[Post]:
        """
        Fetch posts from a Facebook page.
        
        Args:
            page_id: Facebook page ID
            limit: Maximum number of posts to fetch
            
        Returns:
            List[Post]: List of posts
            
        Raises:
            FacebookAPIError: If API request fails
        """
        posts = []
        url = f"{self.base_url}/{page_id}/posts"
        
        params = {
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares,from',
            'limit': min(limit, 25)  # Facebook's max per request
        }
        
        try:
            while len(posts) < limit:
                response = self._make_request(url, params)
                
                if response.status_code != 200:
                    self._handle_api_error(response)
                
                data = response.json()
                
                # Process posts
                for post_data in data.get('data', []):
                    try:
                        post = self._parse_post_data(post_data)
                        posts.append(post)
                        
                        if len(posts) >= limit:
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to parse post {post_data.get('id')}: {e}")
                        continue
                
                # Handle pagination
                if 'paging' in data and 'next' in data['paging'] and len(posts) < limit:
                    url = data['paging']['next']
                    params = {}  # Next URL already contains parameters
                else:
                    break
            
            print(f"✅ Fetched {len(posts)} posts from page {page_id}")
            return posts[:limit]
            
        except Exception as e:
            if isinstance(e, (FacebookAPIError, AuthenticationError, RateLimitError)):
                raise
            raise FacebookAPIError(f"Failed to fetch posts from page {page_id}: {e}")
    
    def fetch_comments_from_post(self, post_id: str, limit: int = 100) -> List[Comment]:
        """
        Fetch comments from a Facebook post.
        
        Args:
            post_id: Facebook post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            List[Comment]: List of comments
            
        Raises:
            FacebookAPIError: If API request fails
        """
        comments = []
        url = f"{self.base_url}/{post_id}/comments"
        
        params = {
            'fields': 'id,message,created_time,like_count,comment_count,from,parent',
            'limit': min(limit, 100),  # Facebook's max per request
            'order': 'chronological'
        }
        
        try:
            while len(comments) < limit:
                response = self._make_request(url, params)
                
                if response.status_code != 200:
                    self._handle_api_error(response)
                
                data = response.json()
                
                # Process comments
                for comment_data in data.get('data', []):
                    try:
                        comment = self._parse_comment_data(comment_data)
                        comments.append(comment)
                        
                        if len(comments) >= limit:
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to parse comment {comment_data.get('id')}: {e}")
                        continue
                
                # Handle pagination
                if 'paging' in data and 'next' in data['paging'] and len(comments) < limit:
                    url = data['paging']['next']
                    params = {}  # Next URL already contains parameters
                else:
                    break
            
            print(f"✅ Fetched {len(comments)} comments from post {post_id}")
            return comments[:limit]
            
        except Exception as e:
            if isinstance(e, (FacebookAPIError, AuthenticationError, RateLimitError)):
                raise
            raise FacebookAPIError(f"Failed to fetch comments from post {post_id}: {e}")
    
    def fetch_post_info(self, post_id: str) -> Optional[Post]:
        """
        Fetch information about a specific post.
        
        Args:
            post_id: Facebook post ID
            
        Returns:
            Optional[Post]: Post information or None if not found
        """
        url = f"{self.base_url}/{post_id}"
        params = {
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares,from'
        }
        
        try:
            response = self._make_request(url, params)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_post_data(data)
            elif response.status_code == 404:
                return None
            else:
                self._handle_api_error(response)
                
        except Exception as e:
            if isinstance(e, (FacebookAPIError, AuthenticationError, RateLimitError)):
                raise
            raise FacebookAPIError(f"Failed to fetch post info for {post_id}: {e}")
    
    def fetch_comments_batch(self, post_ids: List[str], limit_per_post: int = 50) -> Dict[str, List[Comment]]:
        """
        Fetch comments from multiple posts efficiently.
        
        Args:
            post_ids: List of Facebook post IDs
            limit_per_post: Maximum comments per post
            
        Returns:
            Dict[str, List[Comment]]: Comments grouped by post ID
        """
        results = {}
        
        for post_id in post_ids:
            try:
                comments = self.fetch_comments_from_post(post_id, limit_per_post)
                results[post_id] = comments
            except Exception as e:
                print(f"⚠️  Warning: Failed to fetch comments for post {post_id}: {e}")
                results[post_id] = []
        
        return results
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make HTTP request with rate limiting and error handling.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            requests.Response: HTTP response
            
        Raises:
            RateLimitError: If rate limit is exceeded
            FacebookAPIError: If request fails
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        # Prepare parameters
        if params is None:
            params = {}
        
        params['access_token'] = self.config.access_token
        
        try:
            response = self.session.get(url, params=params)
            self.last_request_time = time.time()
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds", retry_after)
            
            return response
            
        except requests.RequestException as e:
            raise FacebookAPIError(f"HTTP request failed: {e}")
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """
        Handle Facebook API error responses.
        
        Args:
            response: HTTP response with error
            
        Raises:
            AuthenticationError: For authentication errors
            RateLimitError: For rate limit errors
            FacebookAPIError: For other API errors
        """
        try:
            error_data = response.json()
            error = error_data.get('error', {})
            
            error_code = error.get('code')
            error_type = error.get('type')
            error_message = error.get('message', 'Unknown error')
            
            # Handle specific error types
            if error_code in [190, 102, 10]:  # Invalid token, session expired, permission denied
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif error_code == 4:  # Rate limit
                raise RateLimitError(f"Rate limit exceeded: {error_message}")
            elif error_code == 100:  # Invalid parameter
                raise DataValidationError(f"Invalid parameter: {error_message}")
            else:
                raise FacebookAPIError(
                    f"API error (code {error_code}): {error_message}",
                    status_code=response.status_code,
                    response_data=error_data
                )
                
        except json.JSONDecodeError:
            raise FacebookAPIError(
                f"API request failed with status {response.status_code}: {response.text}",
                status_code=response.status_code
            )
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse Facebook datetime string into datetime object.
        
        Args:
            datetime_str: Facebook datetime string (ISO format)
            
        Returns:
            datetime: Parsed datetime object or None if parsing fails
        """
        if not datetime_str:
            return None
            
        try:
            # Facebook returns datetime in ISO format like "2024-01-01T10:00:00+0000"
            # Parse and convert to UTC
            if datetime_str.endswith('+0000'):
                datetime_str = datetime_str[:-5] + 'Z'
            
            # Parse ISO format
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Failed to parse datetime '{datetime_str}': {e}")
            return None
    
    def _parse_post_data(self, post_data: Dict[str, Any]) -> Post:
        """
        Parse raw Facebook post data into Post object.
        
        Args:
            post_data: Raw post data from Facebook API
            
        Returns:
            Post: Parsed post object
        """
        try:
            # Extract basic information
            post_id = post_data['id']
            message = post_data.get('message', '')
            created_time_str = post_data.get('created_time', '')
            
            # Parse datetime
            created_time = self._parse_datetime(created_time_str)
            
            # Extract engagement metrics
            likes_data = post_data.get('likes', {}).get('summary', {})
            likes_count = likes_data.get('total_count', 0)
            
            shares_data = post_data.get('shares', {})
            shares_count = shares_data.get('count', 0)
            
            # Extract author information
            from_data = post_data.get('from', {})
            author = from_data.get('name', 'Unknown')
            
            return Post(
                id=post_id,
                content=message,
                created_time=created_time,
                likes_count=likes_count,
                shares_count=shares_count,
                author=author,
                comments=[]  # Comments will be added separately
            )
            
        except KeyError as e:
            raise DataValidationError(f"Missing required field in post data: {e}")
        except Exception as e:
            raise DataValidationError(f"Failed to parse post data: {e}")
    
    def _parse_comment_data(self, comment_data: Dict[str, Any]) -> Comment:
        """
        Parse raw Facebook comment data into Comment object.
        
        Args:
            comment_data: Raw comment data from Facebook API
            
        Returns:
            Comment: Parsed comment object
        """
        try:
            # Extract basic information
            comment_id = comment_data['id']
            text = comment_data.get('message', '')
            created_time_str = comment_data.get('created_time', '')
            
            # Parse datetime
            created_time = self._parse_datetime(created_time_str)
            
            # Extract engagement metrics
            likes_count = comment_data.get('like_count', 0)
            replies_count = comment_data.get('comment_count', 0)
            
            # Extract author information
            from_data = comment_data.get('from', {})
            author = from_data.get('name', 'Unknown')
            
            return Comment(
                id=comment_id,
                content=text,
                author=author,
                created_time=created_time,
                likes_count=likes_count,
                replies_count=replies_count
            )
            
        except KeyError as e:
            raise DataValidationError(f"Missing required field in comment data: {e}")
        except Exception as e:
            raise DataValidationError(f"Failed to parse comment data: {e}")
    
    def _parse_facebook_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse Facebook datetime string to datetime object.
        
        Args:
            datetime_str: Facebook datetime string (ISO format)
            
        Returns:
            datetime object or None if parsing fails
        """
        if not datetime_str:
            return None
            
        try:
            # Facebook returns ISO format datetime strings
            # Example: "2024-01-15T10:30:00+0000"
            if '+' in datetime_str:
                # Remove timezone info and parse
                datetime_str = datetime_str.split('+')[0]
            elif 'T' in datetime_str and 'Z' in datetime_str:
                # Handle Z timezone format
                datetime_str = datetime_str.replace('Z', '')
            
            return datetime.fromisoformat(datetime_str)
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Failed to parse datetime '{datetime_str}': {e}")
            return None
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Returns:
            Dict[str, Any]: API usage statistics
        """
        return {
            'base_url': self.base_url,
            'api_version': self.config.api_version,
            'timeout': self.config.timeout,
            'min_request_interval': self.min_request_interval,
            'last_request_time': self.last_request_time
        }
