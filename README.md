# 🔍 SentimentScope - Facebook Comment Sentiment Analyzer

<div align="center">

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey.svg)

*A comprehensive, multi-language sentiment analysis tool for Facebook posts and comments*

</div>

---

## 🌟 **Overview**

SentimentScope is a production-ready sentiment analysis tool that transforms Facebook comments and posts into actionable insights. Built with clean architecture principles, it supports multiple languages, provides professional visualizations, and offers a comprehensive CLI interface for social media managers, data analysts, and researchers.

### ✨ **Why SentimentScope?**

- **🌐 Multi-Language Support**: Native English and Thai sentiment analysis with extensible architecture
- **🏗️ Clean Architecture**: Modular, maintainable, and testable codebase following SOLID principles
- **📊 Professional Reporting**: Export to CSV, JSON, Excel with rich visualizations and dashboards
- **🔧 Production Ready**: Comprehensive error handling, logging, and configuration management
- **🎯 User Friendly**: Interactive CLI with progress bars, setup wizards, and helpful error messages

---

## 🚀 **Features**

### **Core Functionality**
- ✅ **Facebook Graph API Integration** - Secure, rate-limited API communication
- ✅ **Multi-Language Sentiment Analysis** - English (VADER) + Thai (Custom Lexicon)
- ✅ **Automatic Language Detection** - Smart Unicode-based language identification
- ✅ **Bulk Comment Processing** - Handle thousands of comments with pagination support
- ✅ **Real-Time Progress Tracking** - Visual feedback during long-running operations

### **Data Analysis & Insights**
- 📊 **Comprehensive Sentiment Scoring** - Positive, negative, neutral with confidence scores
- 📈 **Engagement Correlation Analysis** - Sentiment vs. likes, replies, and shares
- 🕒 **Temporal Analysis** - Sentiment trends over time
- 🌍 **Language Demographics** - Audience language distribution analysis
- 🎯 **Key Insights Extraction** - Most positive/negative comments identification

### **Export & Visualization**
- 📄 **Multiple Export Formats** - CSV, JSON, Excel with rich metadata
- 📊 **Interactive Dashboards** - Professional charts and visualizations
- 📈 **Statistical Reports** - Comprehensive analysis summaries
- 🎨 **Customizable Visualizations** - Pie charts, histograms, timelines, heatmaps

### **User Experience**
- 🖥️ **Professional CLI Interface** - Built with Click framework
- ⚙️ **Interactive Setup Wizard** - Guided Facebook API configuration
- 🔧 **Configuration Management** - Environment variables, YAML, and CLI options
- 📝 **Comprehensive Help System** - Built-in documentation and examples
- 🚨 **Rich Error Reporting** - Clear, actionable error messages

---

## 🚀 **Quick Start**

### **1. Clone & Install**
```bash
git clone https://github.com/yourusername/SentimentScope.git
cd SentimentScope
pip install -r requirements.txt
```

### **2. Configure Facebook API**
```bash
# Interactive setup wizard
python main.py setup
```

### **3. Analyze Your First Post**
```bash
# Analyze a Facebook post with visualization
python main.py analyze-post \
  --post-id "YOUR_POST_ID" \
  --create-viz \
  --export-format json
```

### **4. View Results**
```bash
# Results will be saved as:
# - Analysis data: post_YOUR_POST_ID_analysis_TIMESTAMP.json
# - Dashboard: post_YOUR_POST_ID_dashboard_TIMESTAMP.png
# - Sentiment chart: post_YOUR_POST_ID_sentiment_TIMESTAMP.png
```

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.9 or higher
- Facebook Developer Account (for API access)
- Git (for cloning the repository)

### **Option 1: Standard Installation**
```bash
# Clone the repository
git clone https://github.com/yourusername/SentimentScope.git
cd SentimentScope

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Option 2: Using UV (Faster)**
```bash
# If you have uv installed
git clone https://github.com/yourusername/SentimentScope.git
cd SentimentScope
uv sync
```

### **Option 3: Development Installation**
```bash
# For contributors and developers
git clone https://github.com/yourusername/SentimentScope.git
cd SentimentScope
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Additional dev dependencies
```

---

## 🔧 **Configuration**

### **Facebook API Setup**

1. **Create Facebook App**
   - Go to [Facebook for Developers](https://developers.facebook.com/)
   - Create a new app → Business type
   - Note your App ID and App Secret

2. **Generate Access Token**
   - Use [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your app and generate a User Access Token
   - Required permissions: `pages_read_engagement`, `pages_show_list`

3. **Configure SentimentScope**
   ```bash
   # Interactive setup (recommended)
   python main.py setup
   
   # Or manually create .env file
   cp .env.example .env
   # Edit .env with your credentials
   ```

### **Environment Variables**
```bash
# Facebook API Configuration
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_API_VERSION=v18.0

# Analysis Configuration
POSITIVE_THRESHOLD=0.05
NEGATIVE_THRESHOLD=-0.05
MAX_COMMENTS_PER_REQUEST=100
RATE_LIMIT_DELAY=1.0

# Export Configuration
EXPORT_FORMAT=csv
OUTPUT_DIRECTORY=.
```

---

## 💻 **Usage**

### **Command Line Interface**

#### **Basic Analysis**
```bash
# Analyze a single post
python main.py analyze-post --post-id "123456789_987654321"

# With specific options
python main.py analyze-post \
  --post-id "123456789_987654321" \
  --limit 200 \
  --export-format excel \
  --output-dir ./results \
  --create-viz \
  --verbose
```

#### **Available Commands**
```bash
# Setup and configuration
python main.py setup                    # Interactive setup wizard
python main.py validate-config          # Validate current configuration

# Analysis commands
python main.py analyze-post             # Analyze specific post
python main.py analyze-page             # Analyze page posts (coming soon)

# Help and information
python main.py --help                   # Show all commands
python main.py analyze-post --help      # Command-specific help
```

#### **Command Options**
```bash
# analyze-post options
--post-id TEXT          Facebook Post ID (required)
--limit INTEGER         Max comments to fetch (default: 100)
--export-format CHOICE  Export format: csv|json|excel (default: csv)
--output-dir PATH       Output directory (default: current)
--create-viz            Create visualization dashboard
--verbose, -v           Verbose output with detailed logging
--config, -c PATH       Custom configuration file path
```

### **Programmatic Usage**

```python
from src.analyzers.base_analyzer import MultiLanguageAnalyzer
from src.analyzers.language_detector import LanguageDetector
from src.analyzers.vader_analyzer import VaderSentimentAnalyzer
from src.analyzers.thai_analyzer import ThaiSentimentAnalyzer
from src.services.facebook_api_service import FacebookAPIService
from src.core.models import Language
from src.core.config import ConfigManager

# Initialize configuration
config_manager = ConfigManager()
fb_config = config_manager.get_facebook_config()

# Setup analyzer
language_detector = LanguageDetector()
analyzer = MultiLanguageAnalyzer(language_detector)
analyzer.register_analyzer(Language.ENGLISH, VaderSentimentAnalyzer())
analyzer.register_analyzer(Language.THAI, ThaiSentimentAnalyzer())

# Setup API service
api_service = FacebookAPIService(fb_config)

# Analyze a post
post = api_service.fetch_post("YOUR_POST_ID")
comments = api_service.fetch_comments("YOUR_POST_ID", limit=100)
post.comments = comments

# Get analysis results
results = analyzer.analyze_post(post)
print(f"Overall sentiment: {results.post_sentiment.label}")
```

---

## 📊 **Output Examples**

### **Console Output**
```
🔍 Facebook Comment Sentiment Analyzer v2.0
==================================================
📊 Analyzing post: 170584316340695_1129247439237919
📈 Fetching up to 100 comments...
💾 Export format: csv
📁 Output directory: .

🔄 Fetching post and comments from Facebook...
✅ Fetched post with 25 comments

🧠 Analyzing sentiment...
💾 Exporting results as csv...
✅ Results exported to: post_170584316340695_1129247439237919_analysis_20250624_174251.csv

📊 ANALYSIS SUMMARY
==================================================
Post ID: 170584316340695_1129247439237919
Total Items: 26 (1 post + 25 comments)

Sentiment Distribution:
  😊 Positive: 12 (46.2%)
  😐 Neutral: 8 (30.8%)
  😢 Negative: 6 (23.1%)

Language Distribution:
  🇺🇸 EN: 18 (69.2%)
  🇹🇭 TH: 8 (30.8%)

Average Sentiment: 0.245
Overall Mood: 😊 Positive

🎉 Analysis completed successfully!
```

### **CSV Export Sample**
```csv
id,content,author,created_time,likes_count,replies_count,sentiment_compound,sentiment_label,language,analyzer_used
123_456,This is amazing! Love it! 😍,John Doe,2024-01-15 10:30:00,12,3,0.861,POSITIVE,en,vader
789_012,สวยมากเลย ชอบมาก ❤️,Jane Smith,2024-01-15 11:15:00,8,1,0.667,POSITIVE,th,thai_lexicon
```

### **Visualization Dashboard**
The tool generates professional visualizations including:
- 📊 Sentiment distribution pie chart
- 📈 Sentiment score histogram
- 🔗 Sentiment vs. engagement scatter plot
- 🕒 Sentiment timeline analysis
- 🌍 Language distribution breakdown

---

## 🏗️ **Architecture**

### **Project Structure**
```
SentimentScope/
├── 📁 src/
│   ├── 📁 core/                 # Core models, config, exceptions
│   │   ├── __init__.py
│   │   ├── models.py            # Data models (Post, Comment, SentimentScore)
│   │   ├── config.py            # Configuration management
│   │   └── exceptions.py        # Custom exception hierarchy
│   │
│   ├── 📁 services/             # External service integrations
│   │   ├── __init__.py
│   │   └── facebook_api_service.py  # Facebook Graph API client
│   │
│   ├── 📁 analyzers/            # Sentiment analysis engines
│   │   ├── __init__.py
│   │   ├── base_analyzer.py     # Abstract analyzer interfaces
│   │   ├── vader_analyzer.py    # English sentiment analysis
│   │   ├── thai_analyzer.py     # Thai sentiment analysis
│   │   └── language_detector.py # Language detection utility
│   │
│   ├── 📁 exporters/            # Data export functionality
│   │   ├── __init__.py
│   │   ├── base_exporter.py     # Export interface
│   │   ├── csv_exporter.py      # CSV export
│   │   ├── json_exporter.py     # JSON export
│   │   └── excel_exporter.py    # Excel export
│   │
│   ├── 📁 visualizers/          # Data visualization
│   │   ├── __init__.py
│   │   ├── base_visualizer.py   # Visualization interface
│   │   ├── sentiment_visualizer.py  # Sentiment charts
│   │   └── dashboard_visualizer.py  # Comprehensive dashboards
│   │
│   ├── 📁 utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── text_utils.py        # Text processing utilities
│   │   └── data_utils.py        # Data manipulation helpers
│   │
│   └── 📁 interfaces/           # User interfaces
│       ├── __init__.py
│       └── cli.py               # Command-line interface
│
├── 📁 tests/                    # Test suite
├── 📁 docs/                     # Documentation
├── 📁 examples/                 # Usage examples
├── 📄 main.py                   # Application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example             # Environment template
└── 📄 README.md                # This file
```

### **Design Patterns Used**
- **Strategy Pattern**: Multiple sentiment analyzers
- **Factory Pattern**: Exporter and visualizer creation
- **Dependency Injection**: Service configuration
- **Template Method**: Base analyzer workflow
- **Observer Pattern**: Progress reporting

### **Key Design Principles**
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **Clean Architecture**: Separation of concerns, dependency rule
- **Type Safety**: Comprehensive type hints throughout
- **Error Handling**: Graceful degradation and user-friendly messages
- **Testing**: Comprehensive test coverage for reliability

---

## 🧪 **Testing**

### **Run Tests**
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/unit/           # Unit tests
python -m pytest tests/integration/    # Integration tests
```

### **Test Structure**
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_models.py
│   ├── test_analyzers.py
│   ├── test_exporters.py
│   └── test_visualizers.py
├── integration/             # Integration tests for workflows
│   ├── test_api_integration.py
│   └── test_end_to_end.py
└── fixtures/                # Test data and mocks
    ├── sample_comments.json
    └── mock_responses.json
```

---

## 🔒 **Security & Privacy**

### **Data Handling**
- **No Persistent Storage**: Data is processed and exported, not stored permanently
- **API Token Security**: Tokens stored in environment variables, never logged
- **Rate Limiting**: Respects Facebook's API rate limits
- **Error Sanitization**: Sensitive information removed from error messages

### **Privacy Considerations**
- **Anonymization Options**: Can exclude author names from exports
- **GDPR Compliance**: Tools for data deletion and export
- **Minimal Data Collection**: Only collects necessary sentiment analysis data
- **Local Processing**: All analysis happens locally, no external data transmission

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/yourusername/SentimentScope.git
cd SentimentScope
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```



### **Language Support**
- ✅ **English**: VADER sentiment analysis (optimized for social media)
- ✅ **Thai**: Custom lexicon-based analysis with emoji support


---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Facebook API Errors**
```bash
# Test your API connection
python main.py validate-config

# Common solutions:
# 1. Check if your access token is valid
# 2. Verify app permissions (pages_read_engagement)
# 3. Ensure the post/page is publicly accessible
```

#### **Installation Issues**
```bash
# If you encounter package conflicts:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# For M1 Mac users:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### **Analysis Errors**
```bash
# Enable verbose logging for debugging
python main.py analyze-post --post-id YOUR_POST_ID --verbose

# Check logs in ./logs/ directory
tail -f logs/analyzer.log
```

### **Getting Help**
- 📝 [Open an Issue](https://github.com/yourusername/SentimentScope/issues)
- 💬 [Discussions](https://github.com/yourusername/SentimentScope/discussions)
- 📧 Email: [your-email@example.com](mailto:your-email@example.com)

---

## 📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

### **Technologies Used**
- **[Facebook Graph API](https://developers.facebook.com/docs/graph-api/)** - Social media data access
- **[VADER Sentiment](https://github.com/cjhutto/vaderSentiment)** - English sentiment analysis
- **[PyThaiNLP](https://github.com/PyThaiNLP/pythainlp)** - Thai language processing
- **[Click](https://click.palletsprojects.com/)** - Command-line interface framework
- **[Matplotlib](https://matplotlib.org/)** - Data visualization
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis

### **Inspiration**
- Social media analytics platforms
- Academic research in sentiment analysis
- Open-source NLP libraries and tools

---

## 🔮 **Roadmap**

### **Version 2.1 (Next Release)**
- 🌐 Web-based dashboard interface
- 📊 Real-time analysis streaming
- 🎯 Batch processing for multiple posts
- 🔄 API rate limiting optimization

### **Version 2.2 (Future)**
- 🤖 Machine learning model training
- 🌍 Additional language support
- 📱 Mobile-friendly reporting
- 🔌 Plugin system for custom analyzers

### **Version 3.0 (Long-term)**
- 🏢 Enterprise features
- 🔗 Integration with other social platforms
- 🧠 Advanced NLP features (entity extraction, topic modeling)
- ☁️ Cloud deployment options


