import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import warnings

# Sentiment Analysis Libraries
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Visualization
import matplotlib
# Use 'TkAgg' for interactive plots or 'Agg' for file-only (no GUI warnings)
matplotlib.use('Agg')  # Change to 'TkAgg' if you want interactive plots
import matplotlib.pyplot as plt

# Configure matplotlib to avoid GUI warnings
plt.ioff()  # Turn off interactive mode

# Import Thai-specific libraries if available
# Note: pythainlp.sentiment is not available in current version, will be imported as needed

# Suppress matplotlib warnings for headless environments
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

load_dotenv(override=True)  # Force reload to get latest values

@dataclass
class Comment:
    id: str
    text: str
    author: str
    created_time: str
    likes_count: int
    replies_count: int
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None

@dataclass
class Post:
    id: str
    message: str
    created_time: str
    likes_count: int
    comments_count: int
    shares_count: int

class FacebookCommentAnalyzer:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
    def test_token_validity(self) -> bool:
        """Test if the access token is valid"""
        if not self.access_token:
            print("No access token found in environment variables")
            return False
            
        url = "https://graph.facebook.com/v18.0/me"
        params = {'access_token': self.access_token}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"Token valid for user/app: {data.get('name', data.get('id', 'Unknown'))}")
                return True
            else:
                print(f"Token validation failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"Error validating token: {e}")
            return False
    
    def get_page_access_token(self, page_id: str) -> Optional[str]:
        """Get page access token using app credentials"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()['access_token']
        except Exception as e:
            print(f"Error getting access token: {e}")
        return None
    
    def fetch_posts_from_page(self, page_id: str, limit: int = 10) -> List[Post]:
        """Fetch posts from a Facebook page using Graph API"""
        posts = []
        # Use the user access token directly instead of generating app token
        access_token = self.access_token
        
        if not access_token:
            print("No access token found in environment variables")
            return posts
        
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for post_data in data.get('data', []):
                    try:
                        post = Post(
                            id=post_data['id'],
                            message=post_data.get('message', ''),
                            created_time=post_data.get('created_time', ''),
                            likes_count=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                            comments_count=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                            shares_count=post_data.get('shares', {}).get('count', 0)
                        )
                        posts.append(post)
                    except Exception as e:
                        print(f"Error parsing post {post_data.get('id', 'unknown')}: {e}")
                        continue
            else:
                print(f"Error fetching posts: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error fetching posts: {e}")
        
        return posts
    
    def fetch_comments_from_post(self, post_id: str, limit: int = 100) -> List[Comment]:
        """Fetch comments from a specific post using Graph API"""
        comments = []
        # Use the user access token directly
        access_token = self.access_token
        
        if not access_token:
            print("No access token found in environment variables")
            return comments
        
        url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        params = {
            'access_token': access_token,
            'fields': 'id,message,from,created_time,like_count,comment_count',
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for comment_data in data.get('data', []):
                    comment = Comment(
                        id=comment_data['id'],
                        text=comment_data.get('message', ''),
                        author=comment_data.get('from', {}).get('name', 'Unknown'),
                        created_time=comment_data['created_time'],
                        likes_count=comment_data.get('like_count', 0),
                        replies_count=comment_data.get('comment_count', 0)
                    )
                    comments.append(comment)
                    
                # Handle pagination
                while 'paging' in data and 'next' in data['paging']:
                    next_url = data['paging']['next']
                    response = requests.get(next_url)
                    if response.status_code == 200:
                        data = response.json()
                        for comment_data in data.get('data', []):
                            comment = Comment(
                                id=comment_data['id'],
                                text=comment_data.get('message', ''),
                                author=comment_data.get('from', {}).get('name', 'Unknown'),
                                created_time=comment_data['created_time'],
                                likes_count=comment_data.get('like_count', 0),
                                replies_count=comment_data.get('comment_count', 0)
                            )
                            comments.append(comment)
                    else:
                        break
                        
            else:
                print(f"Error fetching comments: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error fetching comments: {e}")
        
        return comments
    
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
            
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'label': label
        }
    
    def analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
            
        return {
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': label
        }
    
    def analyze_sentiment_thai(self, text: str) -> Dict[str, float]:
        """Analyze sentiment for Thai text using lexicon-based approach"""
        try:
            # Try to use PyThaiNLP if available
            try:
                import pythainlp
                # Since pythainlp.sentiment is not available in current version,
                # we'll use our custom lexicon-based approach
                return self._analyze_thai_lexicon(text)
            except ImportError:
                # Fallback to lexicon-based approach for Thai
                return self._analyze_thai_lexicon(text)
            
        except Exception as e:
            print(f"Error in Thai sentiment analysis: {e}")
            # Fallback to lexicon-based approach
            return self._analyze_thai_lexicon(text)
    
    def _analyze_thai_lexicon(self, text: str) -> Dict[str, float]:
        """Simple lexicon-based Thai sentiment analysis"""
        # Basic Thai positive/negative words
        thai_positive_words = [
            'ดี', 'สวย', 'สุด', 'เจ้า', 'รัก', 'ชอบ', 'ยอดเยี่ยม', 'เลิศ', 'ดีเยี่ยม',
            'น่ารัก', 'เก่ง', 'มาก', 'สนุก', 'ใส', 'เด็ด', 'เจ๋ง', 'เยี่ยม', 'วิเศษ',
            'สุดยอด', 'เฮง', 'โชค', 'ซื้อ', 'แชร์', 'ดีใจ', 'สำเร็จ', 'ปัง', 'เก๋',
            '👍', '❤️', '😍', '🥰', '😊', '👏', '🎉', '✨', '💕', '🔥'
        ]
        
        thai_negative_words = [
            'แย่', 'เสีย', 'ไม่', 'ผิด', 'เกลียด', 'หยุด', 'ป่วย', 'เจ็บ', 'ตาย',
            'เศร้า', 'โกรธ', 'งั่ง', 'ห่วย', 'แพง', 'เบื่อ', 'น่าเบื่อ', 'ขยะ',
            'ปลิ้น', 'บ้า', 'โง่', 'งี่เง่า', 'แปลก', 'ผิดหวัง', 'เฮี้ยน', 'ปวด',
            '👎', '😠', '😡', '😢', '😭', '💔', '😰', '🤮', '👹', '😵'
        ]
        
        # Count positive and negative words
        positive_count = sum(1 for word in thai_positive_words if word in text)
        negative_count = sum(1 for word in thai_negative_words if word in text)
        
        # Calculate compound score
        total_words = len(text.split())
        if total_words == 0:
            compound = 0.0
        else:
            compound = (positive_count - negative_count) / max(total_words, 1)
            compound = max(-1.0, min(1.0, compound))  # Normalize to [-1, 1]
        
        # Determine label
        if compound >= 0.1:
            label = 'positive'
        elif compound <= -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'label': label,
            'method': 'thai_lexicon'
        }
    
    def detect_language(self, text: str) -> str:
        """Detect if text is primarily Thai or English"""
        thai_chars = sum(1 for char in text if '\u0e00' <= char <= '\u0e7f')
        english_chars = sum(1 for char in text if char.isalpha() and char.isascii())
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return 'unknown'
        
        thai_ratio = thai_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if thai_ratio > 0.3:  # If more than 30% Thai characters
            return 'thai'
        elif english_ratio > 0.5:  # If more than 50% English characters
            return 'english'
        else:
            return 'mixed'

    def analyze_comments_sentiment(self, comments: List[Comment]) -> List[Comment]:
        """Analyze sentiment for all comments"""
        analyzed_comments = []
        
        for comment in comments:
            if comment.text:
                # Detect language and choose analysis method
                lang = self.detect_language(comment.text)
                
                if lang == 'thai':
                    # Use specialized Thai sentiment analysis
                    thai_result = self.analyze_sentiment_thai(comment.text)
                    comment.sentiment_score = thai_result['compound']
                    comment.sentiment_label = thai_result['label']
                else:
                    # Use VADER for social media text (better for informal text)
                    vader_result = self.analyze_sentiment_vader(comment.text)
                    comment.sentiment_score = vader_result['compound']
                    comment.sentiment_label = vader_result['label']
            else:
                comment.sentiment_score = 0
                comment.sentiment_label = 'neutral'
            
            analyzed_comments.append(comment)
        
        return analyzed_comments
    
    def generate_sentiment_report(self, comments: List[Comment], post: Post = None) -> Dict:
        """Generate comprehensive sentiment analysis report"""
        if not comments:
            return {}
        
        # Calculate sentiment distribution
        sentiments = [c.sentiment_label for c in comments if c.sentiment_label]
        sentiment_counts = pd.Series(sentiments).value_counts()
        
        # Calculate average sentiment score
        sentiment_scores = [c.sentiment_score for c in comments if c.sentiment_score is not None]
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        
        # Find most positive and negative comments
        positive_comments = [c for c in comments if c.sentiment_label == 'positive']
        negative_comments = [c for c in comments if c.sentiment_label == 'negative']
        
        most_positive = max(positive_comments, key=lambda x: x.sentiment_score) if positive_comments else None
        most_negative = min(negative_comments, key=lambda x: x.sentiment_score) if negative_comments else None
        
        # Engagement analysis
        total_likes = sum(c.likes_count for c in comments)
        avg_likes_per_comment = total_likes / len(comments) if comments else 0
        
        # Language analysis
        languages = {}
        for comment in comments:
            if comment.text:
                lang = self.detect_language(comment.text)
                languages[lang] = languages.get(lang, 0) + 1
        
        report = {
            'total_comments': len(comments),
            'language_distribution': languages,
            'sentiment_distribution': sentiment_counts.to_dict(),
            'sentiment_percentages': (sentiment_counts / len(comments) * 100).to_dict(),
            'average_sentiment_score': avg_sentiment,
            'total_comment_likes': total_likes,
            'average_likes_per_comment': avg_likes_per_comment,
            'most_positive_comment': {
                'text': most_positive.text[:100] + '...' if most_positive and len(most_positive.text) > 100 else most_positive.text if most_positive else None,
                'score': most_positive.sentiment_score if most_positive else None,
                'likes': most_positive.likes_count if most_positive else None
            } if most_positive else None,
            'most_negative_comment': {
                'text': most_negative.text[:100] + '...' if most_negative and len(most_negative.text) > 100 else most_negative.text if most_negative else None,
                'score': most_negative.sentiment_score if most_negative else None,
                'likes': most_negative.likes_count if most_negative else None
            } if most_negative else None
        }
        
        if post:
            report['post_info'] = {
                'post_id': post.id,
                'post_likes': post.likes_count,
                'post_shares': post.shares_count,
                'engagement_ratio': (total_likes / post.likes_count * 100) if post.likes_count > 0 else 0
            }
        
        return report
    
    def visualize_sentiment_analysis(self, comments: List[Comment], save_path: str = None):
        """Create visualization of sentiment analysis results"""
        if not comments:
            print("No comments to visualize")
            return
        
        # Prepare data
        sentiments = [c.sentiment_label for c in comments if c.sentiment_label]
        sentiment_scores = [c.sentiment_score for c in comments if c.sentiment_score is not None]
        likes = [c.likes_count for c in comments]
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Facebook Comments Sentiment Analysis', fontsize=16)
        
        # 1. Sentiment Distribution (Pie Chart)
        sentiment_counts = pd.Series(sentiments).value_counts()
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', colors=colors[:len(sentiment_counts)])
        axes[0, 0].set_title('Sentiment Distribution')
        
        # 2. Sentiment Score Distribution (Histogram)
        axes[0, 1].hist(sentiment_scores, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Sentiment Score Distribution')
        axes[0, 1].set_xlabel('Sentiment Score (-1 to 1)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
        
        # 3. Sentiment vs Likes
        sentiment_numeric = {'negative': -1, 'neutral': 0, 'positive': 1}
        sentiment_values = [sentiment_numeric[s] for s in sentiments]
        axes[1, 0].scatter(sentiment_values, likes[:len(sentiment_values)], alpha=0.6)
        axes[1, 0].set_title('Sentiment vs Likes')
        axes[1, 0].set_xlabel('Sentiment (-1: Negative, 0: Neutral, 1: Positive)')
        axes[1, 0].set_ylabel('Number of Likes')
        
        # 4. Timeline of Sentiment (if timestamps available)
        if hasattr(comments[0], 'created_time') and comments[0].created_time:
            try:
                timestamps = [datetime.fromisoformat(c.created_time.replace('Z', '+00:00')) for c in comments if c.created_time and c.sentiment_score is not None]
                sentiment_timeline = [c.sentiment_score for c in comments if c.created_time and c.sentiment_score is not None]
                
                if timestamps and sentiment_timeline:
                    axes[1, 1].plot(timestamps, sentiment_timeline, marker='o', alpha=0.7)
                    axes[1, 1].set_title('Sentiment Over Time')
                    axes[1, 1].set_xlabel('Time')
                    axes[1, 1].set_ylabel('Sentiment Score')
                    axes[1, 1].tick_params(axis='x', rotation=45)
                else:
                    axes[1, 1].text(0.5, 0.5, 'No timestamp data available', ha='center', va='center', transform=axes[1, 1].transAxes)
            except Exception as e:
                axes[1, 1].text(0.5, 0.5, f'Error plotting timeline: {str(e)}', ha='center', va='center', transform=axes[1, 1].transAxes)
        else:
            axes[1, 1].text(0.5, 0.5, 'No timestamp data available', ha='center', va='center', transform=axes[1, 1].transAxes)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        else:
            # Save with default filename if no path specified
            default_path = f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {default_path}")
        
        # Close the figure to free memory and avoid warnings
        plt.close()
        
        # Note: plt.show() removed to avoid warning with Agg backend
    
    def export_results_to_csv(self, comments: List[Comment], filename: str = None):
        """Export analysis results to CSV"""
        if not filename:
            filename = f"facebook_comments_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        data = []
        for comment in comments:
            data.append({
                'comment_id': comment.id,
                'text': comment.text,
                'author': comment.author,
                'created_time': comment.created_time,
                'likes_count': comment.likes_count,
                'replies_count': comment.replies_count,
                'sentiment_score': comment.sentiment_score,
                'sentiment_label': comment.sentiment_label
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")
        return filename

    def test_facebook_api_connection(self, page_id: str) -> bool:
        """Test Facebook API connection with the exact same parameters as the working curl command"""
        if not self.access_token:
            print("No access token found")
            return False
        
        # Exact same URL and parameters as your working curl command
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        params = {
            'field': 'id,comments',  # Using 'field' (singular) like in your curl
            'access_token': self.access_token
        }
        
        print(f"Testing API connection to: {url}")
        print(f"With parameters: {params}")
        
        try:
            response = requests.get(url, params=params)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {len(data.get('data', []))} posts")
                if data.get('data'):
                    first_post = data['data'][0]
                    print(f"First post ID: {first_post.get('id')}")
                    print(f"First post has comments: {'comments' in first_post}")
                return True
            else:
                print(f"Error response: {response.text}")
                return False
        except Exception as e:
            print(f"Exception occurred: {e}")
            return False
    
    def get_post_info(self, post_id: str) -> Optional[Post]:
        """Get basic information about a specific post"""
        if not self.access_token:
            print("No access token found")
            return None
        
        url = f"https://graph.facebook.com/v18.0/{post_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                post_data = response.json()
                return Post(
                    id=post_data['id'],
                    message=post_data.get('message', ''),
                    created_time=post_data.get('created_time', ''),
                    likes_count=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                    comments_count=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                    shares_count=post_data.get('shares', {}).get('count', 0)
                )
            else:
                print(f"Error fetching post info: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Error fetching post info: {e}")
            return None

# Alternative Selenium-based scraper (Use with caution - may violate ToS)
class FacebookScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Uncomment the next line to run in headless mode
            # chrome_options.add_argument("--headless")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except ImportError:
            print("Selenium not installed. Web scraping functionality not available.")
            self.driver = None
    
    def scrape_post_comments(self, post_url: str, max_comments: int = 50) -> List[str]:
        """
        Scrape comments from a Facebook post URL
        WARNING: This method may violate Facebook's Terms of Service
        """
        if not self.driver:
            print("Chrome driver not available")
            return []
            
        comments = []
        
        try:
            self.driver.get(post_url)
            time.sleep(3)
            
            # Wait for page to load
            time.sleep(5)
            
            # Try to find and click "View more comments" buttons
            for _ in range(max_comments // 10):
                try:
                    from selenium.webdriver.common.by import By
                    view_more_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'View more comments')]")
                    view_more_button.click()
                    time.sleep(2)
                except Exception:
                    break
            
            # Extract comment text
            try:
                from selenium.webdriver.common.by import By
                comment_elements = self.driver.find_elements(By.XPATH, "//div[@data-testid='comment']//span[contains(@class, '')]")
                
                for element in comment_elements[:max_comments]:
                    try:
                        comment_text = element.text.strip()
                        if comment_text and len(comment_text) > 10:  # Filter out very short text
                            comments.append(comment_text)
                    except Exception:
                        continue
            except ImportError:
                print("Selenium By module not available")
                    
        except Exception as e:
            print(f"Error scraping comments: {e}")
        
        return comments
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Example usage of the Facebook Comment Analyzer"""
    analyzer = FacebookCommentAnalyzer()
    
    # Test token validity first
    print("=== Facebook Comment Analysis Tool ===\n")
    print("Testing access token...")
    if not analyzer.test_token_validity():
        print("Please check your access token in the .env file")
        print("Continuing with sample data only...\n")
    else:
        print("Access token is valid!\n")
    
    # Give user options for analysis
    print("Choose analysis mode:")
    print("1. Analyze comments from a specific post ID")
    print("2. Analyze posts from a Facebook page")
    print("3. Skip to sample data demo")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        # Option 1: Direct post ID analysis
        post_id = input("Enter Facebook Post ID: ").strip()
        if post_id:
            print(f"\n=== Analyzing Post: {post_id} ===")
            
            # Get post information first
            post_info = analyzer.get_post_info(post_id)
            if post_info:
                print(f"Post Message: {post_info.message[:100]}..." if len(post_info.message) > 100 else f"Post Message: {post_info.message}")
                print(f"Post Likes: {post_info.likes_count}")
                print(f"Post Comments: {post_info.comments_count}")
                print(f"Post Shares: {post_info.shares_count}")
                print(f"Created: {post_info.created_time}")
            
            comments = analyzer.fetch_comments_from_post(post_id)
            
            if comments:
                print(f"\nFound {len(comments)} comments")
                
                # Analyze sentiment
                analyzed_comments = analyzer.analyze_comments_sentiment(comments)
                
                # Generate report with post info
                report = analyzer.generate_sentiment_report(analyzed_comments, post_info)
                
                print("\n=== SENTIMENT ANALYSIS REPORT ===")
                print(f"Total Comments: {report['total_comments']}")
                print(f"Average Sentiment Score: {report['average_sentiment_score']:.3f}")
                print(f"Total Comment Likes: {report['total_comment_likes']}")
                print(f"Average Likes per Comment: {report['average_likes_per_comment']:.1f}")
                
                # Show language distribution
                if report.get('language_distribution'):
                    print("\nLanguage Distribution:")
                    for lang, count in report['language_distribution'].items():
                        percentage = (count / report['total_comments']) * 100
                        print(f"  {lang.capitalize()}: {count} comments ({percentage:.1f}%)")
                
                print("\nSentiment Distribution:")
                for sentiment, percentage in report['sentiment_percentages'].items():
                    print(f"  {sentiment.capitalize()}: {percentage:.1f}%")
                
                if report.get('most_positive_comment'):
                    print("\nMost Positive Comment:")
                    print(f"  Text: {report['most_positive_comment']['text']}")
                    print(f"  Score: {report['most_positive_comment']['score']:.3f}")
                    print(f"  Likes: {report['most_positive_comment']['likes']}")
                
                if report.get('most_negative_comment'):
                    print("\nMost Negative Comment:")
                    print(f"  Text: {report['most_negative_comment']['text']}")
                    print(f"  Score: {report['most_negative_comment']['score']:.3f}")
                    print(f"  Likes: {report['most_negative_comment']['likes']}")
                
                if report.get('post_info'):
                    print("\nPost Engagement Analysis:")
                    print(f"  Comment-to-Post Engagement Ratio: {report['post_info']['engagement_ratio']:.1f}%")
                
                # Export results
                filename = f"post_{post_id.replace('_', '-')}_analysis.csv"
                analyzer.export_results_to_csv(analyzed_comments, filename)
                
                # Create visualization
                try:
                    viz_filename = f"post_{post_id.replace('_', '-')}_sentiment.png"
                    analyzer.visualize_sentiment_analysis(analyzed_comments, viz_filename)
                    print(f"Visualization saved to: {viz_filename}")
                except Exception as e:
                    print(f"Could not create visualization: {e}")
            else:
                print("No comments found or unable to access comments from this post")
                print("This could be due to:")
                print("- Invalid post ID")
                print("- Post has no comments")
                print("- Insufficient permissions")
                print("- Post is private or deleted")
    
    elif choice == "2":
        # Option 2: Page analysis (original functionality)
        page_id = input("Enter Facebook Page ID: ").strip()
        
        if page_id:
            print("\n=== Testing API Connection ===")
            if analyzer.test_facebook_api_connection(page_id):
                print("✅ API connection successful!")
                print(f"\nFetching posts from page: {page_id}")
                posts = analyzer.fetch_posts_from_page(page_id, limit=5)
                
                if posts:
                    print(f"Found {len(posts)} posts")
                    
                    # Show available posts
                    print("\nAvailable posts:")
                    for i, post in enumerate(posts[:5], 1):
                        preview = post.message[:50] + "..." if len(post.message) > 50 else post.message
                        print(f"  {i}. {post.id} - {preview}")
                        print(f"     Comments: {post.comments_count}, Likes: {post.likes_count}")
                    
                    # Let user choose which post to analyze
                    post_choice = input(f"\nChoose post to analyze (1-{len(posts)}) or Enter for first post: ").strip()
                    
                    try:
                        post_index = int(post_choice) - 1 if post_choice else 0
                        if 0 <= post_index < len(posts):
                            selected_post = posts[post_index]
                        else:
                            selected_post = posts[0]
                    except ValueError:
                        selected_post = posts[0]
                    
                    print(f"\nAnalyzing comments from post: {selected_post.id}")
                    comments = analyzer.fetch_comments_from_post(selected_post.id)
                    
                    if comments:
                        print(f"Found {len(comments)} comments")
                        
                        # Analyze sentiment
                        analyzed_comments = analyzer.analyze_comments_sentiment(comments)
                        
                        # Generate report
                        report = analyzer.generate_sentiment_report(analyzed_comments, selected_post)
                        
                        print("\n=== SENTIMENT ANALYSIS REPORT ===")
                        print(f"Total Comments: {report['total_comments']}")
                        print(f"Average Sentiment Score: {report['average_sentiment_score']:.3f}")
                        print(f"Total Comment Likes: {report['total_comment_likes']}")
                        print(f"Average Likes per Comment: {report['average_likes_per_comment']:.1f}")
                        
                        # Show language distribution
                        if report.get('language_distribution'):
                            print("\nLanguage Distribution:")
                            for lang, count in report['language_distribution'].items():
                                percentage = (count / report['total_comments']) * 100
                                print(f"  {lang.capitalize()}: {count} comments ({percentage:.1f}%)")
                        
                        print("\nSentiment Distribution:")
                        for sentiment, percentage in report['sentiment_percentages'].items():
                            print(f"  {sentiment.capitalize()}: {percentage:.1f}%")
                        
                        if report.get('post_info'):
                            print("\nPost Engagement:")
                            print(f"  Post Likes: {report['post_info']['post_likes']}")
                            print(f"  Post Shares: {report['post_info']['post_shares']}")
                            print(f"  Comment-to-Post Engagement Ratio: {report['post_info']['engagement_ratio']:.1f}%")
                        
                        # Export results
                        filename = f"page_{page_id}_post_analysis.csv"
                        analyzer.export_results_to_csv(analyzed_comments, filename)
                        
                        # Create visualization
                        try:
                            viz_filename = f"page_{page_id}_sentiment.png"
                            analyzer.visualize_sentiment_analysis(analyzed_comments, viz_filename)
                            print(f"Visualization saved to: {viz_filename}")
                        except Exception as e:
                            print(f"Could not create visualization: {e}")
                    else:
                        print("No comments found or unable to access comments")
                else:
                    print("No posts found or unable to access posts")
            else:
                print("❌ API connection failed. Check your permissions and page ID.")
    
    # Example 3: Analyze sample comments with Thai support (for testing)
    print("\n=== Testing with Mixed Language Sample Comments ===")
    sample_comments = [
        Comment("1", "This is amazing! I love it! 😍", "User1", "2024-01-01", 5, 0),
        Comment("2", "สวยมากเลย ชอบมาก ❤️", "User2", "2024-01-01", 8, 0),
        Comment("3", "Not impressed at all. Very disappointing. 👎", "User3", "2024-01-01", 1, 0),
        Comment("4", "แย่มาก เกลียดเลย ไม่ชอบ", "User4", "2024-01-01", 0, 0),
        Comment("5", "It's okay, nothing special.", "User5", "2024-01-01", 2, 0),
        Comment("6", "ปังมาก เจ๋งสุด 🔥 ดีเยี่ยม", "User6", "2024-01-01", 12, 0),
        Comment("7", "Absolutely fantastic! Best thing ever! 🎉", "User7", "2024-01-01", 10, 0),
        Comment("8", "เบื่อ น่าเบื่อ ห่วยแตก 😰", "User8", "2024-01-01", 0, 0),
        Comment("9", "Pretty good mix สวย nice เด็ด!", "User9", "2024-01-01", 6, 0),
        Comment("10", "Terrible experience. Would not recommend.", "User10", "2024-01-01", 0, 0),
    ]
    
    analyzed_sample = analyzer.analyze_comments_sentiment(sample_comments)
    sample_report = analyzer.generate_sentiment_report(analyzed_sample)
    
    print(f"Mixed Language Analysis - Total Comments: {sample_report['total_comments']}")
    print(f"Average Sentiment Score: {sample_report['average_sentiment_score']:.3f}")
    
    # Show language distribution
    if sample_report.get('language_distribution'):
        print("\nLanguage Distribution:")
        for lang, count in sample_report['language_distribution'].items():
            percentage = (count / sample_report['total_comments']) * 100
            print(f"  {lang.capitalize()}: {count} comments ({percentage:.1f}%)")
    
    print("\nSentiment Distribution:")
    for sentiment, percentage in sample_report['sentiment_percentages'].items():
        print(f"  {sentiment.capitalize()}: {percentage:.1f}%")
    
    # Export sample results
    sample_csv = analyzer.export_results_to_csv(analyzed_sample, "sample_analysis.csv")
    print(f"Sample results saved to: {sample_csv}")
    
    # Create sample visualization
    try:
        analyzer.visualize_sentiment_analysis(analyzed_sample, 'sample_sentiment_analysis.png')
        print("Sample visualization saved to: sample_sentiment_analysis.png")
    except Exception as e:
        print(f"Could not create sample visualization: {e}")

if __name__ == "__main__":
    main()
