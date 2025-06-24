"""Base exporter interface for analysis results."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from ..core.models import AnalysisResult

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Abstract base class for data exporters."""
    
    def __init__(self, output_dir: str = "exports"):
        """Initialize the exporter.
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def export(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Export analysis results to a file.
        
        Args:
            results: List of analysis results to export
            filename: Name of the output file (without extension)
            **kwargs: Additional export options
            
        Returns:
            Path to the exported file
            
        Raises:
            ExportError: If export fails
        """
        pass
    
    def _prepare_data(self, results: List[AnalysisResult]) -> List[Dict[str, Any]]:
        """Prepare analysis results for export by flattening the data structure.
        
        Args:
            results: List of analysis results
            
        Returns:
            List of dictionaries ready for export
        """
        exported_data = []
        
        for result in results:
            # Export post-level data
            post_data = {
                'type': 'post',
                'post_id': result.post.id,
                'comment_id': None,  # Posts don't have comment IDs
                'content': result.post.content[:100] + '...' if len(result.post.content) > 100 else result.post.content,
                'author': result.post.author,
                'created_time': result.post.created_time.isoformat() if result.post.created_time else None,
                'likes_count': result.post.likes_count,
                'comments_count': len(result.post.comments),
                'sentiment_compound': result.post_sentiment.compound if result.post_sentiment else None,
                'sentiment_positive': result.post_sentiment.positive if result.post_sentiment else None,
                'sentiment_negative': result.post_sentiment.negative if result.post_sentiment else None,
                'sentiment_neutral': result.post_sentiment.neutral if result.post_sentiment else None,
                'language': result.post_sentiment.language if result.post_sentiment else None,
                'analyzer_used': result.post_sentiment.analyzer_used if result.post_sentiment else None,
            }
            exported_data.append(post_data)
            
            # Export comment-level data
            for comment, sentiment in zip(result.post.comments, result.comment_sentiments):
                comment_data = {
                    'type': 'comment',
                    'post_id': result.post.id,
                    'comment_id': comment.id,
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'author': comment.author,
                    'created_time': comment.created_time.isoformat() if comment.created_time else None,
                    'likes_count': comment.likes_count,
                    'comments_count': None,  # Comments don't have sub-comments in this model
                    'sentiment_compound': sentiment.compound if sentiment else None,
                    'sentiment_positive': sentiment.positive if sentiment else None,
                    'sentiment_negative': sentiment.negative if sentiment else None,
                    'sentiment_neutral': sentiment.neutral if sentiment else None,
                    'language': sentiment.language if sentiment else None,
                    'analyzer_used': sentiment.analyzer_used if sentiment else None,
                }
                exported_data.append(comment_data)
        
        return exported_data
    
    def _get_summary_stats(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate summary statistics for the analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Dictionary containing summary statistics
        """
        total_posts = len(results)
        total_comments = sum(len(result.post.comments) for result in results)
        
        # Aggregate sentiment scores
        all_sentiments = []
        for result in results:
            if result.post_sentiment:
                all_sentiments.append(result.post_sentiment)
            all_sentiments.extend([s for s in result.comment_sentiments if s])
        
        if not all_sentiments:
            return {
                'total_posts': total_posts,
                'total_comments': total_comments,
                'total_items': total_posts + total_comments,
                'avg_compound': 0,
                'avg_positive': 0,
                'avg_negative': 0,
                'avg_neutral': 0,
            }
        
        avg_compound = sum(s.compound for s in all_sentiments) / len(all_sentiments)
        avg_positive = sum(s.positive for s in all_sentiments) / len(all_sentiments)
        avg_negative = sum(s.negative for s in all_sentiments) / len(all_sentiments)
        avg_neutral = sum(s.neutral for s in all_sentiments) / len(all_sentiments)
        
        return {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_items': total_posts + total_comments,
            'avg_compound': round(avg_compound, 4),
            'avg_positive': round(avg_positive, 4),
            'avg_negative': round(avg_negative, 4),
            'avg_neutral': round(avg_neutral, 4),
        }
