"""
Command Line Interface for Facebook Comment Analyzer.

This module provides a comprehensive CLI for the Facebook Comment Analyzer
with commands for analyzing posts, pages, and configuration management.
"""

import click
import sys
import os
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    ConfigManager, 
    FacebookAnalyzerError, 
    ConfigurationError,
    Language,
    SentimentLabel
)


@click.group()
@click.version_option(version='2.0.0')
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Facebook Comment Sentiment Analyzer CLI"""
    ctx.ensure_object(dict)
    
    try:
        ctx.obj['config_manager'] = ConfigManager(config)
        ctx.obj['config_file'] = config
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--post-id', required=True, help='Facebook Post ID to analyze')
@click.option('--limit', default=100, help='Maximum number of comments to fetch')
@click.option('--export-format', default='csv', type=click.Choice(['csv', 'json', 'excel']), 
              help='Export format')
@click.option('--output-dir', default='.', help='Output directory for results')
@click.option('--create-viz', is_flag=True, help='Create visualization dashboard')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def analyze_post(ctx, post_id: str, limit: int, export_format: str, output_dir: str, 
                create_viz: bool, verbose: bool):
    """Analyze comments from a specific Facebook post"""
    
    click.echo("🔍 Facebook Comment Sentiment Analyzer v2.0")
    click.echo("=" * 50)
    
    try:
        config_manager = ctx.obj['config_manager']
        
        # Validate configuration
        try:
            config_manager.validate_config()
        except ConfigurationError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            click.echo("💡 Run 'python main.py setup' to configure the analyzer")
            sys.exit(1)
        
        click.echo(f"📊 Analyzing post: {post_id}")
        click.echo(f"📈 Fetching up to {limit} comments...")
        click.echo(f"💾 Export format: {export_format}")
        click.echo(f"📁 Output directory: {output_dir}")
        
        # Import and initialize services here to avoid circular imports
        from services.facebook_api_service import FacebookAPIService
        from services.sentiment_analysis_service import SentimentAnalysisService
        from exporters.csv_exporter import CSVExporter
        from visualizers.sentiment_dashboard import SentimentDashboard
        
        # Initialize services
        fb_config = config_manager.get_facebook_config()
        api_service = FacebookAPIService(fb_config)
        sentiment_service = SentimentAnalysisService()
        
        # Create progress bar
        with click.progressbar(length=100, label='Processing') as bar:
            # Step 1: Fetch comments (30%)
            click.echo("\n🔄 Fetching comments from Facebook...")
            comments = api_service.fetch_comments_from_post(post_id, limit)
            bar.update(30)
            
            if not comments:
                click.echo("❌ No comments found for this post")
                return
            
            click.echo(f"✅ Fetched {len(comments)} comments")
            
            # Step 2: Analyze sentiment (40%)
            click.echo("🧠 Analyzing sentiment...")
            analyzed_comments = sentiment_service.analyze_comments(comments)
            bar.update(40)
            
            # Step 3: Export results (20%)
            click.echo(f"💾 Exporting results as {export_format}...")
            if export_format == 'csv':
                exporter = CSVExporter()
                export_file = exporter.export(analyzed_comments, 
                    os.path.join(output_dir, f"post_{post_id}_analysis.csv"))
            # Add other export formats here...
            
            click.echo(f"✅ Results exported to: {export_file}")
            bar.update(20)
            
            # Step 4: Create visualization (10%)
            if create_viz:
                click.echo("📈 Creating visualization dashboard...")
                dashboard = SentimentDashboard()
                viz_file = dashboard.create_dashboard(analyzed_comments,
                    os.path.join(output_dir, f"post_{post_id}_dashboard.png"))
                click.echo(f"✅ Dashboard saved to: {viz_file}")
            bar.update(10)
        
        # Display summary
        _display_analysis_summary(analyzed_comments)
        
        click.echo("\n🎉 Analysis completed successfully!")
        
    except FacebookAnalyzerError as e:
        click.echo(f"❌ Analyzer error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--page-id', required=True, help='Facebook Page ID to analyze')
@click.option('--post-limit', default=10, help='Maximum number of posts to fetch')
@click.option('--comment-limit', default=50, help='Maximum comments per post')
@click.option('--export-format', default='csv', type=click.Choice(['csv', 'json', 'excel']))
@click.option('--output-dir', default='.')
@click.option('--create-viz', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def analyze_page(ctx, page_id: str, post_limit: int, comment_limit: int, 
                export_format: str, output_dir: str, create_viz: bool, verbose: bool):
    """Analyze comments from multiple posts on a Facebook page"""
    
    click.echo("🔍 Facebook Page Comment Analysis")
    click.echo("=" * 50)
    
    try:
        config_manager = ctx.obj['config_manager']
        
        # Validate configuration
        config_manager.validate_config()
        
        click.echo(f"📊 Analyzing page: {page_id}")
        click.echo(f"📈 Fetching up to {post_limit} posts with {comment_limit} comments each")
        
        # TODO: Implement page analysis
        click.echo("🚧 Page analysis feature coming soon!")
        
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def setup():
    """Interactive setup wizard for Facebook API credentials"""
    
    click.echo("🚀 Facebook Comment Analyzer Setup")
    click.echo("=" * 50)
    
    click.echo("Please provide your Facebook API credentials:")
    click.echo("(You can get these from https://developers.facebook.com/)")
    click.echo()
    
    app_id = click.prompt("📱 Facebook App ID", type=str)
    app_secret = click.prompt("🔐 Facebook App Secret", type=str, hide_input=True)
    access_token = click.prompt("🎫 Access Token", type=str, hide_input=True)
    
    # Optional settings
    click.echo("\n⚙️  Optional Settings (press Enter for defaults):")
    api_version = click.prompt("📡 API Version", default="v18.0")
    positive_threshold = click.prompt("➕ Positive Sentiment Threshold", default=0.05, type=float)
    negative_threshold = click.prompt("➖ Negative Sentiment Threshold", default=-0.05, type=float)
    
    # Create .env file
    env_content = f"""# Facebook API Configuration
FACEBOOK_APP_ID={app_id}
FACEBOOK_APP_SECRET={app_secret}
FACEBOOK_ACCESS_TOKEN={access_token}
FACEBOOK_API_VERSION={api_version}

# Analysis Configuration  
POSITIVE_THRESHOLD={positive_threshold}
NEGATIVE_THRESHOLD={negative_threshold}
MAX_COMMENTS_PER_REQUEST=100
RATE_LIMIT_DELAY=1.0

# Export Configuration
EXPORT_FORMAT=csv
OUTPUT_DIRECTORY=.
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        click.echo("\n✅ Configuration saved to .env file")
        
        # Test configuration
        click.echo("🧪 Testing configuration...")
        
        try:
            config_manager = ConfigManager()
            config_manager.validate_config()
            click.echo("✅ Configuration is valid!")
            
            # Test API connection
            click.echo("🔗 Testing Facebook API connection...")
            from services.facebook_api_service import FacebookAPIService
            
            fb_config = config_manager.get_facebook_config()
            api_service = FacebookAPIService(fb_config)
            
            # Simple API test
            if api_service.test_connection():
                click.echo("✅ Facebook API connection successful!")
            else:
                click.echo("⚠️  Facebook API connection test failed - please verify your credentials")
            
        except Exception as e:
            click.echo(f"⚠️  Configuration test failed: {e}")
            click.echo("You may need to verify your Facebook API credentials")
        
        click.echo("\n🎉 Setup completed! You can now run analysis commands.")
        click.echo("💡 Try: python main.py analyze-post --post-id YOUR_POST_ID")
        
    except Exception as e:
        click.echo(f"❌ Setup failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def validate_config(ctx):
    """Validate current configuration"""
    
    click.echo("🔍 Validating Configuration")
    click.echo("=" * 30)
    
    try:
        config_manager = ctx.obj['config_manager']
        
        # Test Facebook config
        click.echo("📱 Facebook API Configuration:")
        fb_config = config_manager.get_facebook_config()
        click.echo(f"  App ID: {fb_config.app_id[:8]}..." if fb_config.app_id else "  App ID: ❌ Missing")
        click.echo(f"  Access Token: {'✅ Present' if fb_config.access_token else '❌ Missing'}")
        click.echo(f"  API Version: {fb_config.api_version}")
        
        # Test Analysis config
        click.echo("\n🧠 Analysis Configuration:")
        analysis_config = config_manager.get_analysis_config()
        click.echo(f"  Positive Threshold: {analysis_config.positive_threshold}")
        click.echo(f"  Negative Threshold: {analysis_config.negative_threshold}")
        click.echo(f"  Max Comments: {analysis_config.max_comments_per_request}")
        
        # Validate all
        config_manager.validate_config()
        click.echo("\n✅ Configuration is valid!")
        
    except ConfigurationError as e:
        click.echo(f"\n❌ Configuration error: {e}")
        click.echo("💡 Run 'python main.py setup' to fix configuration")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Validation failed: {e}")
        sys.exit(1)


def _display_analysis_summary(comments):
    """Display analysis summary"""
    if not comments:
        return
    
    # Calculate statistics
    total_comments = len(comments)
    sentiment_counts = {}
    language_counts = {}
    
    for comment in comments:
        # Count sentiments
        if comment.sentiment_label:
            sentiment_counts[comment.sentiment_label] = sentiment_counts.get(comment.sentiment_label, 0) + 1
        
        # Count languages
        if comment.language:
            language_counts[comment.language] = language_counts.get(comment.language, 0) + 1
    
    # Display summary
    click.echo("\n" + "="*50)
    click.echo("📊 ANALYSIS SUMMARY")
    click.echo("="*50)
    click.echo(f"Total Comments: {total_comments}")
    
    if sentiment_counts:
        click.echo("\nSentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total_comments) * 100
            emoji = "😊" if sentiment == SentimentLabel.POSITIVE else "😢" if sentiment == SentimentLabel.NEGATIVE else "😐"
            click.echo(f"  {emoji} {sentiment.value.capitalize()}: {count} ({percentage:.1f}%)")
    
    if language_counts:
        click.echo("\nLanguage Distribution:")
        for language, count in language_counts.items():
            percentage = (count / total_comments) * 100
            flag = "🇹🇭" if language == Language.THAI else "🇺🇸" if language == Language.ENGLISH else "🌐"
            click.echo(f"  {flag} {language.value.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Calculate average sentiment
    sentiment_scores = [c.sentiment_score for c in comments if c.sentiment_score is not None]
    if sentiment_scores:
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        click.echo(f"\nAverage Sentiment: {avg_sentiment:.3f}")


def main():
    """Main CLI entry point"""
    cli()


if __name__ == '__main__':
    main()
