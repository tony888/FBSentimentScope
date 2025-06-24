"""JSON exporter for analysis results."""

import json
from typing import List
from pathlib import Path
import logging
from datetime import datetime

from .base_exporter import BaseExporter
from ..core.models import AnalysisResult
from ..core.exceptions import ExportError

logger = logging.getLogger(__name__)


class JSONExporter(BaseExporter):
    """Export analysis results to JSON format."""
    
    def export(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Export analysis results to JSON file.
        
        Args:
            results: List of analysis results to export
            filename: Name of the output file (without extension)
            **kwargs: Additional export options
                pretty: Whether to format JSON nicely (default: True)
                include_summary: Whether to include summary statistics (default: True)
                
        Returns:
            Path to the exported JSON file
            
        Raises:
            ExportError: If export fails
        """
        pretty = kwargs.get('pretty', True)
        include_summary = kwargs.get('include_summary', True)
        output_file = self.output_dir / f"{filename}.json"
        
        try:
            # Prepare export data structure
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_results': len(results),
                    'analyzer_version': '1.0.0',
                },
                'results': self._prepare_structured_data(results)
            }
            
            # Add summary if requested
            if include_summary:
                export_data['summary'] = self._get_summary_stats(results)
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                if pretty:
                    json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, jsonfile, ensure_ascii=False)
            
            logger.info(f"Successfully exported {len(results)} results to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            raise ExportError(f"Failed to export to JSON: {e}")
    
    def _prepare_structured_data(self, results: List[AnalysisResult]) -> List[dict]:
        """Prepare analysis results in a structured format for JSON export.
        
        Args:
            results: List of analysis results
            
        Returns:
            List of structured dictionaries
        """
        structured_data = []
        
        for result in results:
            # Structure each result as a complete unit
            result_data = {
                'post': {
                    'id': result.post.id,
                    'content': result.post.content,
                    'author': result.post.author,
                    'created_time': result.post.created_time.isoformat() if result.post.created_time else None,
                    'likes_count': result.post.likes_count,
                    'sentiment': {
                        'compound': result.post_sentiment.compound if result.post_sentiment else None,
                        'positive': result.post_sentiment.positive if result.post_sentiment else None,
                        'negative': result.post_sentiment.negative if result.post_sentiment else None,
                        'neutral': result.post_sentiment.neutral if result.post_sentiment else None,
                        'language': result.post_sentiment.language if result.post_sentiment else None,
                        'analyzer_used': result.post_sentiment.analyzer_used if result.post_sentiment else None,
                    } if result.post_sentiment else None
                },
                'comments': []
            }
            
            # Add comments with their sentiments
            for comment, sentiment in zip(result.post.comments, result.comment_sentiments):
                comment_data = {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author,
                    'created_time': comment.created_time.isoformat() if comment.created_time else None,
                    'likes_count': comment.likes_count,
                    'sentiment': {
                        'compound': sentiment.compound if sentiment else None,
                        'positive': sentiment.positive if sentiment else None,
                        'negative': sentiment.negative if sentiment else None,
                        'neutral': sentiment.neutral if sentiment else None,
                        'language': sentiment.language if sentiment else None,
                        'analyzer_used': sentiment.analyzer_used if sentiment else None,
                    } if sentiment else None
                }
                result_data['comments'].append(comment_data)
            
            structured_data.append(result_data)
        
        return structured_data
