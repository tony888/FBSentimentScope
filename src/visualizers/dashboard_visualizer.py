"""Dashboard visualizer for comprehensive Facebook Comment Analysis reporting."""

from typing import List, Dict, Any
import logging

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from matplotlib.gridspec import GridSpec
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

from .base_visualizer import BaseVisualizer
from ..core.models import AnalysisResult
from ..core.exceptions import VisualizationError

logger = logging.getLogger(__name__)


class DashboardVisualizer(BaseVisualizer):
    """Create comprehensive dashboard visualizations."""
    
    def create_visualization(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Create a comprehensive dashboard visualization.
        
        Args:
            results: List of analysis results to visualize
            filename: Name of the output file (without extension)
            **kwargs: Additional visualization options
                include_summary: Whether to include summary statistics (default: True)
                
        Returns:
            Path to the created dashboard visualization file
            
        Raises:
            VisualizationError: If visualization creation fails
        """
        include_summary = kwargs.get('include_summary', True)
        
        if not VISUALIZATION_AVAILABLE:
            raise VisualizationError("Visualization libraries not available")
        
        try:
            df = self._prepare_sentiment_data(results)
            
            if df.empty:
                raise VisualizationError("No sentiment data available for dashboard")
            
            return self._create_comprehensive_dashboard(df, filename, include_summary)
                
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise VisualizationError(f"Failed to create dashboard: {e}")
    
    def _create_comprehensive_dashboard(self, df: pd.DataFrame, filename: str, include_summary: bool) -> str:
        """Create a comprehensive dashboard with multiple visualization components.
        
        Args:
            df: DataFrame with sentiment data
            filename: Name of the output file
            include_summary: Whether to include summary statistics
            
        Returns:
            Path to the saved dashboard
        """
        # Create figure with custom grid layout
        fig = plt.figure(figsize=(20, 16))
        gs = GridSpec(4, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Facebook Comment Analysis Dashboard', fontsize=20, fontweight='bold', y=0.95)
        
        # 1. Key Metrics Summary (Top row, full width)
        if include_summary:
            ax_summary = fig.add_subplot(gs[0, :])
            self._add_summary_metrics(ax_summary, df)
        
        # 2. Sentiment Distribution Pie Chart
        ax_pie = fig.add_subplot(gs[1, 0])
        self._add_sentiment_pie_chart(ax_pie, df)
        
        # 3. Sentiment Score Distribution
        ax_hist = fig.add_subplot(gs[1, 1])
        self._add_sentiment_histogram(ax_hist, df)
        
        # 4. Posts vs Comments Comparison
        ax_comparison = fig.add_subplot(gs[1, 2])
        self._add_type_comparison(ax_comparison, df)
        
        # 5. Language Distribution
        ax_language = fig.add_subplot(gs[1, 3])
        self._add_language_distribution(ax_language, df)
        
        # 6. Sentiment Timeline (if timestamps available)
        ax_timeline = fig.add_subplot(gs[2, :2])
        self._add_sentiment_timeline(ax_timeline, df)
        
        # 7. Sentiment vs Engagement
        ax_engagement = fig.add_subplot(gs[2, 2:])
        self._add_engagement_analysis(ax_engagement, df)
        
        # 8. Top Insights
        ax_insights = fig.add_subplot(gs[3, :])
        self._add_key_insights(ax_insights, df)
        
        return self._save_figure(fig, f"{filename}_dashboard", dpi=150)
    
    def _add_summary_metrics(self, ax, df: pd.DataFrame) -> None:
        """Add summary metrics to the dashboard.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        ax.axis('off')
        
        # Calculate key metrics
        total_items = len(df)
        avg_sentiment = df['compound'].mean()
        posts_count = len(df[df['type'] == 'post'])
        comments_count = len(df[df['type'] == 'comment'])
        
        # Categorize overall sentiment
        if avg_sentiment >= 0.05:
            sentiment_label = "Positive"
            sentiment_color = "green"
        elif avg_sentiment <= -0.05:
            sentiment_label = "Negative"
            sentiment_color = "red"
        else:
            sentiment_label = "Neutral"
            sentiment_color = "gray"
        
        # Create summary boxes
        metrics = [
            ("Total Items", str(total_items), "blue"),
            ("Posts", str(posts_count), "purple"),
            ("Comments", str(comments_count), "orange"),
            ("Avg Sentiment", f"{avg_sentiment:.3f}", sentiment_color),
            ("Overall Mood", sentiment_label, sentiment_color)
        ]
        
        box_width = 0.18
        for i, (label, value, color) in enumerate(metrics):
            x_pos = i * 0.2 + 0.1
            
            # Draw box
            box = plt.Rectangle((x_pos, 0.3), box_width, 0.4, 
                              facecolor=color, alpha=0.2, edgecolor=color)
            ax.add_patch(box)
            
            # Add text
            ax.text(x_pos + box_width/2, 0.6, value, 
                   ha='center', va='center', fontsize=14, fontweight='bold', color=color)
            ax.text(x_pos + box_width/2, 0.4, label, 
                   ha='center', va='center', fontsize=10)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('Key Metrics', fontsize=14, fontweight='bold', pad=20)
    
    def _add_sentiment_pie_chart(self, ax, df: pd.DataFrame) -> None:
        """Add sentiment distribution pie chart.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        sentiment_counts = self._categorize_sentiment(df)
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
        
        wedges, texts, autotexts = ax.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        
        # Beautify the pie chart
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Sentiment Distribution', fontsize=12, fontweight='bold')
    
    def _add_sentiment_histogram(self, ax, df: pd.DataFrame) -> None:
        """Add sentiment score histogram.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        ax.hist(df['compound'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax.axvline(df['compound'].mean(), color='red', linestyle='--', 
                  label=f'Mean: {df["compound"].mean():.3f}')
        ax.set_xlabel('Compound Score')
        ax.set_ylabel('Frequency')
        ax.set_title('Sentiment Score Distribution', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _add_type_comparison(self, ax, df: pd.DataFrame) -> None:
        """Add posts vs comments comparison.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        type_sentiment = df.groupby('type')['compound'].mean()
        colors = ['#ff9999', '#66b3ff']
        bars = ax.bar(type_sentiment.index, type_sentiment.values, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Average Sentiment')
        ax.set_title('Posts vs Comments\nSentiment', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _add_language_distribution(self, ax, df: pd.DataFrame) -> None:
        """Add language distribution chart.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        if 'language' in df.columns and df['language'].notna().any():
            language_counts = df['language'].value_counts().head(5)  # Top 5 languages
            colors = self._create_color_palette(len(language_counts))
            bars = ax.bar(language_counts.index, language_counts.values, color=colors, alpha=0.7)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel('Count')
            ax.set_title('Language Distribution', fontsize=12, fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'No language\ndata available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Language Distribution', fontsize=12, fontweight='bold')
    
    def _add_sentiment_timeline(self, ax, df: pd.DataFrame) -> None:
        """Add sentiment timeline if timestamp data is available.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        ax.text(0.5, 0.5, 'Timeline visualization\nwould require timestamp data\nfrom Facebook API', 
               ha='center', va='center', transform=ax.transAxes, fontsize=10)
        ax.set_title('Sentiment Timeline', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Sentiment Score')
    
    def _add_engagement_analysis(self, ax, df: pd.DataFrame) -> None:
        """Add engagement vs sentiment analysis.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        if 'likes_count' in df.columns and df['likes_count'].notna().any():
            scatter = ax.scatter(df['likes_count'], df['compound'], 
                               c=df['compound'], cmap='RdYlGn', alpha=0.6, s=50)
            
            # Add colorbar
            plt.colorbar(scatter, ax=ax, label='Sentiment Score')
            
            # Calculate and display correlation
            correlation = df['likes_count'].corr(df['compound'])
            ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                   transform=ax.transAxes, fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_xlabel('Likes Count')
            ax.set_ylabel('Sentiment Score')
            ax.set_title('Engagement vs Sentiment', fontsize=12, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Engagement data\nnot available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Engagement vs Sentiment', fontsize=12, fontweight='bold')
    
    def _add_key_insights(self, ax, df: pd.DataFrame) -> None:
        """Add key insights section.
        
        Args:
            ax: Matplotlib axis object
            df: DataFrame with sentiment data
        """
        ax.axis('off')
        
        # Generate insights
        insights = self._generate_insights(df)
        
        # Display insights
        ax.text(0.5, 0.9, 'Key Insights', ha='center', va='top', 
               fontsize=14, fontweight='bold', transform=ax.transAxes)
        
        y_pos = 0.7
        for i, insight in enumerate(insights[:4]):  # Show top 4 insights
            ax.text(0.05, y_pos - i*0.15, f"• {insight}", ha='left', va='top', 
                   fontsize=11, transform=ax.transAxes, wrap=True)
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate key insights from the sentiment data.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Overall sentiment insight
        avg_sentiment = df['compound'].mean()
        if avg_sentiment > 0.1:
            insights.append(f"Overall sentiment is positive (avg: {avg_sentiment:.3f})")
        elif avg_sentiment < -0.1:
            insights.append(f"Overall sentiment is negative (avg: {avg_sentiment:.3f})")
        else:
            insights.append(f"Overall sentiment is neutral (avg: {avg_sentiment:.3f})")
        
        # Posts vs comments insight
        if 'type' in df.columns:
            post_sentiment = df[df['type'] == 'post']['compound'].mean()
            comment_sentiment = df[df['type'] == 'comment']['compound'].mean()
            if abs(post_sentiment - comment_sentiment) > 0.1:
                if post_sentiment > comment_sentiment:
                    insights.append("Posts are more positive than comments")
                else:
                    insights.append("Comments are more positive than posts")
        
        # Language insight
        if 'language' in df.columns and df['language'].notna().any():
            dominant_language = df['language'].mode().iloc[0]
            lang_percentage = (df['language'] == dominant_language).mean() * 100
            insights.append(f"{dominant_language.capitalize()} is the dominant language ({lang_percentage:.1f}%)")
        
        # Engagement insight
        if 'likes_count' in df.columns and df['likes_count'].notna().any():
            correlation = df['likes_count'].corr(df['compound'])
            if abs(correlation) > 0.3:
                if correlation > 0:
                    insights.append("Positive content tends to get more likes")
                else:
                    insights.append("Negative content tends to get more engagement")
        
        return insights
    
    def _categorize_sentiment(self, df: pd.DataFrame) -> Dict[str, int]:
        """Categorize sentiment scores.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary with sentiment categories and counts
        """
        def categorize(score):
            if score >= 0.05:
                return 'Positive'
            elif score <= -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        
        df_copy = df.copy()
        df_copy['sentiment_category'] = df_copy['compound'].apply(categorize)
        return df_copy['sentiment_category'].value_counts().to_dict()
