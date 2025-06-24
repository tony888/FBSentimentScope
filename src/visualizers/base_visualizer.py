"""Base visualizer interface for analysis results."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import logging

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    VISUALIZATION_IMPORT_ERROR = str(e)

from ..core.models import AnalysisResult
from ..core.exceptions import VisualizationError

logger = logging.getLogger(__name__)


class BaseVisualizer(ABC):
    """Abstract base class for data visualizers."""
    
    def __init__(self, output_dir: str = "visualizations", style: str = "seaborn-v0_8"):
        """Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization files
            style: Matplotlib style to use
            
        Raises:
            VisualizationError: If required visualization libraries are not available
        """
        if not VISUALIZATION_AVAILABLE:
            raise VisualizationError(f"Visualization requires matplotlib, seaborn, and pandas: {VISUALIZATION_IMPORT_ERROR}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up matplotlib style
        try:
            plt.style.use(style)
        except OSError:
            # Fallback to default style if specified style is not available
            logger.warning(f"Style '{style}' not available, using default")
            plt.style.use('default')
        
        # Set up seaborn theme
        sns.set_theme()
        
        # Configure matplotlib for better output
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    @abstractmethod
    def create_visualization(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Create a visualization from analysis results.
        
        Args:
            results: List of analysis results to visualize
            filename: Name of the output file (without extension)
            **kwargs: Additional visualization options
            
        Returns:
            Path to the created visualization file
            
        Raises:
            VisualizationError: If visualization creation fails
        """
        pass
    
    def _prepare_sentiment_data(self, results: List[AnalysisResult]) -> pd.DataFrame:
        """Prepare sentiment data for visualization.
        
        Args:
            results: List of analysis results
            
        Returns:
            DataFrame with sentiment data ready for visualization
        """
        data = []
        
        for result in results:
            # Add post sentiment data
            if result.post_sentiment:
                data.append({
                    'type': 'post',
                    'id': result.post.id,
                    'content_preview': result.post.content[:50] + '...' if len(result.post.content) > 50 else result.post.content,
                    'author': result.post.author,
                    'compound': result.post_sentiment.compound,
                    'positive': result.post_sentiment.positive,
                    'negative': result.post_sentiment.negative,
                    'neutral': result.post_sentiment.neutral,
                    'language': result.post_sentiment.language,
                    'analyzer': result.post_sentiment.analyzer_used,
                    'likes_count': result.post.likes_count,
                })
            
            # Add comment sentiment data
            for comment, sentiment in zip(result.post.comments, result.comment_sentiments):
                if sentiment:
                    data.append({
                        'type': 'comment',
                        'id': comment.id,
                        'post_id': result.post.id,
                        'content_preview': comment.content[:50] + '...' if len(comment.content) > 50 else comment.content,
                        'author': comment.author,
                        'compound': sentiment.compound,
                        'positive': sentiment.positive,
                        'negative': sentiment.negative,
                        'neutral': sentiment.neutral,
                        'language': sentiment.language,
                        'analyzer': sentiment.analyzer_used,
                        'likes_count': comment.likes_count,
                    })
        
        return pd.DataFrame(data)
    
    def _get_sentiment_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for sentiment data.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}
        
        return {
            'total_items': len(df),
            'avg_compound': df['compound'].mean(),
            'avg_positive': df['positive'].mean(),
            'avg_negative': df['negative'].mean(),
            'avg_neutral': df['neutral'].mean(),
            'posts_count': len(df[df['type'] == 'post']),
            'comments_count': len(df[df['type'] == 'comment']),
            'languages': df['language'].value_counts().to_dict(),
            'analyzers': df['analyzer'].value_counts().to_dict(),
        }
    
    def _save_figure(self, fig, filename: str, dpi: int = 300, bbox_inches: str = 'tight') -> str:
        """Save a matplotlib figure to file.
        
        Args:
            fig: Matplotlib figure object
            filename: Name of the output file (without extension)
            dpi: Resolution for the saved image
            bbox_inches: Bounding box in inches
            
        Returns:
            Path to the saved file
        """
        output_file = self.output_dir / f"{filename}.png"
        
        try:
            fig.savefig(output_file, dpi=dpi, bbox_inches=bbox_inches, 
                       facecolor='white', edgecolor='none')
            logger.info(f"Visualization saved to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to save visualization: {e}")
            raise VisualizationError(f"Failed to save visualization: {e}")
    
    def _create_color_palette(self, n_colors: int) -> List[str]:
        """Create a color palette for visualizations.
        
        Args:
            n_colors: Number of colors needed
            
        Returns:
            List of color codes
        """
        return sns.color_palette("husl", n_colors).as_hex()
