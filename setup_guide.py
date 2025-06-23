"""
Facebook Comment Analyzer Setup Guide
This script provides instructions and helper functions for setting up the Facebook Comment Analyzer
"""

def print_setup_instructions():
    """Print detailed setup instructions"""
    instructions = """
    ===== FACEBOOK COMMENT ANALYZER SETUP GUIDE =====
    
    STEP 1: Install Dependencies
    Run: pip install -r requirements.txt
    
    STEP 2: Facebook App Setup (for API access)
    1. Go to https://developers.facebook.com/
    2. Create a developer account if you don't have one
    3. Click "Create App" and select "Business" type
    4. Fill in app details and create the app
    5. Go to App Settings > Basic and note your App ID and App Secret
    
    STEP 3: Get Access Token
    1. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/
    2. Select your app from the dropdown
    3. Click "Generate Access Token"
    4. Select permissions: pages_read_engagement, pages_show_list
    5. Copy the generated token
    
    STEP 4: Environment Setup
    1. Copy .env.example to .env
    2. Fill in your Facebook credentials in the .env file
    
    STEP 5: Page Access
    Note: Due to Facebook's privacy changes, you can only access:
    - Pages you own/manage
    - Public pages with limited data
    - Comments may require special permissions
    
    ALTERNATIVE: Web Scraping Approach
    - Use the FacebookScraper class for scraping (use with caution)
    - May violate Facebook's Terms of Service
    - Requires manual handling of login and anti-bot measures
    
    USAGE EXAMPLES:
    
    # Basic usage
    analyzer = FacebookCommentAnalyzer()
    posts = analyzer.fetch_posts_from_page("PAGE_ID")
    comments = analyzer.fetch_comments_from_post("POST_ID")
    analyzed = analyzer.analyze_comments_sentiment(comments)
    report = analyzer.generate_sentiment_report(analyzed)
    
    # Export and visualize
    analyzer.export_results_to_csv(analyzed)
    analyzer.visualize_sentiment_analysis(analyzed)
    
    ===== IMPORTANT NOTES =====
    
    1. LEGAL COMPLIANCE:
       - Always respect Facebook's Terms of Service
       - Don't scrape private content
       - Use official APIs when possible
       - Implement rate limiting
    
    2. DATA PRIVACY:
       - Don't store personal information
       - Anonymize user data when possible
       - Follow GDPR and other privacy regulations
    
    3. LIMITATIONS:
       - Facebook limits API access for comment data
       - Many pages/posts may not be accessible
       - Rate limits apply to API calls
       - Web scraping may be blocked
    
    4. ALTERNATIVES:
       - Twitter API (more accessible)
       - Reddit API (easier to use)
       - Public comment datasets
       - Synthetic data for testing
    """
    
    print(instructions)

def test_installation():
    """Test if all required packages are installed"""
    required_packages = [
        'requests', 'selenium', 'beautifulsoup4', 'pandas', 
        'numpy', 'nltk', 'textblob', 'vaderSentiment', 
        'matplotlib', 'seaborn', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
    else:
        print("\n✓ All packages installed successfully!")

def create_sample_analysis():
    """Create a sample analysis with dummy data"""
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    from facebook_comment_analyzer import FacebookCommentAnalyzer, Comment
    
    analyzer = FacebookCommentAnalyzer()
    
    # Sample comments for testing
    sample_comments = [
        Comment("1", "This is absolutely amazing! I love everything about this post! 😍", "Alice", "2024-01-01T10:00:00Z", 15, 2),
        Comment("2", "Not really impressed. Expected much better quality.", "Bob", "2024-01-01T10:05:00Z", 3, 0),
        Comment("3", "It's okay I guess. Nothing too special but not bad either.", "Charlie", "2024-01-01T10:10:00Z", 7, 1),
        Comment("4", "BEST. POST. EVER! This made my day! Thank you so much! 🎉", "Diana", "2024-01-01T10:15:00Z", 25, 3),
        Comment("5", "Waste of time. Very disappointing and misleading.", "Eve", "2024-01-01T10:20:00Z", 1, 0),
        Comment("6", "Pretty good! Would recommend to friends.", "Frank", "2024-01-01T10:25:00Z", 12, 1),
        Comment("7", "Meh. Seen better.", "Grace", "2024-01-01T10:30:00Z", 4, 0),
        Comment("8", "Outstanding work! Really impressed with the quality! 👏", "Henry", "2024-01-01T10:35:00Z", 18, 2),
        Comment("9", "Could be better. Has potential but needs improvement.", "Iris", "2024-01-01T10:40:00Z", 6, 1),
        Comment("10", "Perfect! Exactly what I was looking for!", "Jack", "2024-01-01T10:45:00Z", 20, 0),
    ]
    
    print("Analyzing sample comments...")
    analyzed_comments = analyzer.analyze_comments_sentiment(sample_comments)
    report = analyzer.generate_sentiment_report(analyzed_comments)
    
    print("\n===== SAMPLE ANALYSIS REPORT =====")
    print(f"Total Comments: {report['total_comments']}")
    print(f"Average Sentiment Score: {report['average_sentiment_score']:.3f}")
    print(f"Total Likes on Comments: {report['total_comment_likes']}")
    print(f"Average Likes per Comment: {report['average_likes_per_comment']:.1f}")
    
    print("\nSentiment Distribution:")
    for sentiment, count in report['sentiment_distribution'].items():
        percentage = report['sentiment_percentages'][sentiment]
        print(f"  {sentiment.capitalize()}: {count} comments ({percentage:.1f}%)")
    
    if report['most_positive_comment']:
        print(f"\nMost Positive Comment:")
        print(f"  Text: {report['most_positive_comment']['text']}")
        print(f"  Score: {report['most_positive_comment']['score']:.3f}")
        print(f"  Likes: {report['most_positive_comment']['likes']}")
    
    if report['most_negative_comment']:
        print(f"\nMost Negative Comment:")
        print(f"  Text: {report['most_negative_comment']['text']}")
        print(f"  Score: {report['most_negative_comment']['score']:.3f}")
        print(f"  Likes: {report['most_negative_comment']['likes']}")
    
    # Export sample results
    filename = analyzer.export_results_to_csv(analyzed_comments, "sample_analysis.csv")
    print(f"\nSample results exported to: {filename}")
    
    # Create visualization
    try:
        analyzer.visualize_sentiment_analysis(analyzed_comments, "sample_sentiment_analysis.png")
        print("Sample visualization created: sample_sentiment_analysis.png")
    except Exception as e:
        print(f"Could not create visualization: {e}")

if __name__ == "__main__":
    print("Facebook Comment Analyzer Setup")
    print("Choose an option:")
    print("1. Show setup instructions")
    print("2. Test installation")
    print("3. Run sample analysis")
    print("4. All of the above")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice in ['1', '4']:
        print_setup_instructions()
    
    if choice in ['2', '4']:
        print("\n" + "="*50)
        print("TESTING INSTALLATION")
        print("="*50)
        test_installation()
    
    if choice in ['3', '4']:
        print("\n" + "="*50)
        print("SAMPLE ANALYSIS")
        print("="*50)
        create_sample_analysis()