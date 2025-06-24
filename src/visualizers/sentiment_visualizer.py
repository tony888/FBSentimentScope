"""Sentiment analysis visualizer for Facebook Comment Analyzer."""

from typing import List
import logging

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

from .base_visualizer import BaseVisualizer
from ..core.models import AnalysisResult
from ..core.exceptions import VisualizationError

logger = logging.getLogger(__name__)


class SentimentVisualizer(BaseVisualizer):
    """Create various sentiment analysis visualizations."""
    
    def create_visualization(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Create a comprehensive sentiment visualization.
        
        Args:
            results: List of analysis results to visualize
            filename: Name of the output file (without extension)
            **kwargs: Additional visualization options
                chart_type: Type of chart ('overview', 'distribution', 'timeline', 'comparison')
                
        Returns:
            Path to the created visualization file
            
        Raises:
            VisualizationError: If visualization creation fails
        """
        chart_type = kwargs.get('chart_type', 'overview')
        
        if not VISUALIZATION_AVAILABLE:
            raise VisualizationError("Visualization libraries not available")
        
        try:
            df = self._prepare_sentiment_data(results)
            
            if df.empty:
                raise VisualizationError("No sentiment data available for visualization")
            
            if chart_type == 'overview':
                return self._create_overview_chart(df, filename)
            elif chart_type == 'distribution':
                return self._create_distribution_chart(df, filename)
            elif chart_type == 'comparison':
                return self._create_comparison_chart(df, filename)
            else:
                return self._create_overview_chart(df, filename)
                
        except Exception as e:
            logger.error(f"Failed to create sentiment visualization: {e}")
            raise VisualizationError(f"Failed to create sentiment visualization: {e}")
    
    def _create_overview_chart(self, df: pd.DataFrame, filename: str) -> str:
        """Create an overview chart with multiple sentiment metrics.
        
        Args:
            df: DataFrame with sentiment data
            filename: Name of the output file
            
        Returns:
            Path to the saved visualization
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Sentiment Analysis Overview', fontsize=16, fontweight='bold')
        
        # 1. Sentiment Distribution (Pie Chart)
        sentiment_counts = self._categorize_sentiment(df)
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        ax1.pie(list(sentiment_counts.values()), labels=list(sentiment_counts.keys()), autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax1.set_title('Overall Sentiment Distribution')
        
        # 2. Compound Score Distribution (Histogram)
        ax2.hist(df['compound'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(df['compound'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["compound"].mean():.3f}')
        ax2.set_xlabel('Compound Sentiment Score')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Compound Sentiment Score Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Posts vs Comments Sentiment (Box Plot)
        sns.boxplot(data=df, x='type', y='compound', ax=ax3)
        ax3.set_title('Sentiment by Content Type')
        ax3.set_ylabel('Compound Sentiment Score')
        ax3.set_xlabel('Content Type')
        
        # 4. Language Distribution (Bar Chart)
        if 'language' in df.columns and df['language'].notna().any():
            language_counts = df['language'].value_counts()
            ax4.bar(language_counts.index, language_counts.values, color='lightcoral')
            ax4.set_title('Content Language Distribution')
            ax4.set_xlabel('Language')
            ax4.set_ylabel('Count')
            ax4.tick_params(axis='x', rotation=45)
        else:
            ax4.text(0.5, 0.5, 'No language data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Language Distribution')
        
        plt.tight_layout()
        return self._save_figure(fig, filename)
    
    def _create_distribution_chart(self, df: pd.DataFrame, filename: str) -> str:
        """Create detailed sentiment distribution charts.
        
        Args:
            df: DataFrame with sentiment data
            filename: Name of the output file
            
        Returns:
            Path to the saved visualization
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Sentiment Score Distributions', fontsize=16, fontweight='bold')
        
        # Individual sentiment component distributions
        sentiment_components = ['positive', 'negative', 'neutral', 'compound']
        axes = [ax1, ax2, ax3, ax4]
        colors = ['green', 'red', 'gray', 'blue']
        
        for i, (component, ax, color) in enumerate(zip(sentiment_components, axes, colors)):
            ax.hist(df[component], bins=25, alpha=0.7, color=color, edgecolor='black')
            ax.set_title(f'{component.capitalize()} Sentiment Distribution')
            ax.set_xlabel(f'{component.capitalize()} Score')
            ax.set_ylabel('Frequency')
            ax.axvline(df[component].mean(), color='black', linestyle='--', 
                      label=f'Mean: {df[component].mean():.3f}')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_figure(fig, filename)
    
    def _create_comparison_chart(self, df: pd.DataFrame, filename: str) -> str:
        """Create comparison charts between different segments.
        
        Args:
            df: DataFrame with sentiment data
            filename: Name of the output file
            
        Returns:
            Path to the saved visualization
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Sentiment Analysis Comparisons', fontsize=16, fontweight='bold')
        
        # 1. Posts vs Comments Average Sentiment
        type_sentiment = df.groupby('type')[['positive', 'negative', 'neutral']].mean()
        type_sentiment.plot(kind='bar', ax=ax1, color=['green', 'red', 'gray'])
        ax1.set_title('Average Sentiment by Content Type')
        ax1.set_ylabel('Average Score')
        ax1.set_xlabel('Content Type')
        ax1.legend(title='Sentiment')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Sentiment vs Likes Correlation
        if 'likes_count' in df.columns and df['likes_count'].notna().any():
            ax2.scatter(df['likes_count'], df['compound'], alpha=0.6, color='purple')
            ax2.set_xlabel('Likes Count')
            ax2.set_ylabel('Compound Sentiment Score')
            ax2.set_title('Sentiment vs Popularity')
            
            # Add correlation coefficient
            correlation = df['likes_count'].corr(df['compound'])
            ax2.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=ax2.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        else:
            ax2.text(0.5, 0.5, 'No likes data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Sentiment vs Popularity')
        
        # 3. Analyzer Comparison (if multiple analyzers used)
        if 'analyzer' in df.columns and df['analyzer'].nunique() > 1:
            sns.boxplot(data=df, x='analyzer', y='compound', ax=ax3)
            ax3.set_title('Sentiment by Analyzer')
            ax3.set_ylabel('Compound Sentiment Score')
            ax3.set_xlabel('Analyzer Used')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, 'Single analyzer used', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax3.transAxes, fontsize=12)
            ax3.set_title('Analyzer Comparison')
        
        # 4. Sentiment Intensity Distribution
        df['sentiment_intensity'] = df['compound'].abs()
        ax4.hist(df['sentiment_intensity'], bins=25, alpha=0.7, color='orange', edgecolor='black')
        ax4.set_title('Sentiment Intensity Distribution')
        ax4.set_xlabel('Absolute Compound Score')
        ax4.set_ylabel('Frequency')
        ax4.axvline(df['sentiment_intensity'].mean(), color='red', linestyle='--',
                   label=f'Mean: {df["sentiment_intensity"].mean():.3f}')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_figure(fig, filename)
    
    def _categorize_sentiment(self, df: pd.DataFrame) -> dict:
        """Categorize sentiment scores into positive, negative, and neutral.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary with sentiment category counts
        """
        def categorize(score):
            if score >= 0.05:
                return 'Positive'
            elif score <= -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        
        df['sentiment_category'] = df['compound'].apply(categorize)
        return df['sentiment_category'].value_counts().to_dict()
    
    def create_sentiment_heatmap(self, results: List[AnalysisResult], filename: str) -> str:
        """Create a heatmap showing sentiment patterns.
        
        Args:
            results: List of analysis results to visualize
            filename: Name of the output file
            
        Returns:
            Path to the saved visualization
        """
        try:
            df = self._prepare_sentiment_data(results)
            
            if df.empty:
                raise VisualizationError("No sentiment data available for heatmap")
            
            # Create correlation matrix
            sentiment_cols = ['positive', 'negative', 'neutral', 'compound']
            correlation_matrix = df[sentiment_cols].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='RdYlBu_r', 
                       center=0, ax=ax, square=True, linewidths=0.5)
            ax.set_title('Sentiment Components Correlation Heatmap', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            return self._save_figure(fig, f"{filename}_heatmap")
            
        except Exception as e:
            logger.error(f"Failed to create sentiment heatmap: {e}")
            raise VisualizationError(f"Failed to create sentiment heatmap: {e}")
