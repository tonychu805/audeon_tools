# Master Article Processor Technical Specification

**Version**: 1.0  
**Date**: August 22, 2025  
**Tool**: `Tools/master_article_processor.py`

## 📋 **Overview**

The Master Article Processor is the primary content processing tool that consolidates all article scraping, content enhancement, and metadata generation functionality. It serves as the foundation of the Audeon Tools pipeline, transforming curated markdown lists into rich, TTS-ready JSON data.

### **Purpose**
- **Replaces**: All legacy scrapers and content processors
- **Input**: Curated markdown article lists 
- **Output**: Enhanced JSON with scraped content, LLM summaries, and metadata
- **Integration**: First step in the complete audio generation pipeline

### **Core Functionality**
1. **Markdown Parsing** - Extracts article metadata from curated lists
2. **Content Scraping** - Multi-method content extraction from URLs
3. **LLM Enhancement** - Generates rich summaries using local AI models
4. **Content Processing** - Audio-optimized text cleaning and formatting
5. **Metadata Generation** - Image extraction, read time calculation, categorization

---

## 🏗️ **Architecture**

### **Processing Pipeline**
```
Curated Markdown
       ↓
   Parse Articles (regex extraction)
       ↓
   Scrape Content (hybrid: Firecrawl → Requests → Selenium)
       ↓
   Generate LLM Summaries (Ollama integration)
       ↓
   Extract Images & Metadata
       ↓
   Clean & Process Content (audio optimization)
       ↓
   Enhanced JSON Output
```

### **Class Structure**
```python
class MasterArticleProcessor:
    - markdown parsing methods
    - multi-method content scraping
    - LLM integration (Ollama)
    - content cleaning pipeline
    - metadata extraction
    - progress tracking & resumption
```

---

## ⚙️ **Configuration & Setup**

### **Requirements**
```bash
# Python Dependencies
pip install requests beautifulsoup4 selenium

# System Dependencies  
brew install ollama ffmpeg

# Optional: Chrome/Chromium for Selenium fallback
```

### **Environment Variables**
Create `Tools/.env`:
```bash
# Optional: For Firecrawl integration
FIRECRAWL_API_KEY=your_firecrawl_key
```

### **LLM Setup (Ollama)**
```bash
# Install and start Ollama
brew install ollama
ollama serve

# Pull recommended model
ollama pull llama3.2

# Alternative models
ollama pull llama3.1
ollama pull mistral
```

---

## 🚀 **Usage**

### **Command Line Interface**
```bash
cd Tools

# Basic usage (default paths)
python master_article_processor.py

# Custom input/output
python master_article_processor.py --input my-articles.md --output enhanced.json

# Processing options
python master_article_processor.py --limit 10 --start-from 5 --no-llm

# LLM configuration
python master_article_processor.py --model llama3.1 --ollama-url http://localhost:11434
```

### **Parameters Reference**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input, -i` | string | `../Content/articles/raw/Curated Content List for Audiobook App.markdown` | Input markdown file path |
| `--output, -o` | string | `../Content/articles/raw_metadata/articles_with_summaries.json` | Output JSON file path |
| `--model, -m` | string | `llama3.2` | Ollama model name for summaries |
| `--ollama-url` | string | `http://localhost:11434` | Ollama server URL |
| `--limit` | integer | None | Limit number of articles (testing) |
| `--start-from` | integer | 1 | Start processing from article N (resumption) |
| `--no-llm` | flag | False | Disable LLM summary generation |
| `--no-selenium` | flag | False | Disable Selenium fallback scraping |

---

## 📝 **Input Format Specification**

### **Markdown Structure**
```markdown
# Title

## **CATEGORY: NAME**

1. **Article Title** - Author Name  
   https://full-url-to-article
   *Brief description (gets replaced by LLM)*

2. **Another Article** - Author Name
   https://another-url
   *Another description*
```

### **Parsing Rules**
- **Regex Pattern**: `(\d+)\.\s+\*\*(.*?)\*\*\s*-\s*(.*?)\s*\n\s*https://([^\s]+)\s*\n\s*\*(.*?)\*`
- **Required Elements**: Number, title (bold), author, URL, description (italic)
- **URL Normalization**: Automatically adds `https://` prefix
- **Description Handling**: Basic descriptions are replaced with LLM summaries

---

## 🔍 **Content Scraping Engine**

### **Multi-Method Approach**
1. **Firecrawl MCP** (Priority 1) - Enterprise scraping with JavaScript rendering
2. **Requests + BeautifulSoup** (Priority 2) - Fast, lightweight scraping
3. **Selenium WebDriver** (Priority 3) - Fallback for complex sites

### **Scraping Configuration**
```python
# Request Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) 
                   AppleWebKit/537.36 (KHTML, like Gecko) 
                   Chrome/91.0.4472.124 Safari/537.36'
}

# Selenium Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
```

### **Content Validation**
- **Minimum Length**: 500 characters
- **Quality Checks**: Removes navigation, ads, social elements
- **Encoding**: UTF-8 with fallback handling

---

## 🧠 **LLM Integration**

### **Ollama Configuration**
- **Default Model**: `llama3.2`
- **Temperature**: 0.3 (consistent summaries)
- **Max Tokens**: 200 (summary length)
- **Timeout**: 180 seconds per request

### **Summary Generation Prompt**
```python
prompt = f"""You are creating a summary for a product management article in an audiobook app. 

Article Title: "{title}"

Write an engaging 2-3 sentence summary that:
1. Captures the main insights and key takeaways
2. Explains what listeners will learn
3. Uses conversational, audio-friendly language
4. Is descriptive and compelling for audio content

Article Content:
{content_to_summarize}

Summary:"""
```

### **Fallback Behavior**
- **LLM Unavailable**: Generates basic template summaries
- **Content Too Short**: Skips LLM processing
- **API Errors**: Logs warnings, continues processing

---

## 🧹 **Content Cleaning Pipeline**

### **Audio Optimization**
```python
# Symbol Replacements for TTS
replacements = {
    '&': ' and ', '@': ' at ', '#': ' number ', '%': ' percent ',
    '+': ' plus ', '=': ' equals ', '<': ' less than ', '>': ' greater than ',
    '|': ' or ', '\\': ' backslash ', '/': ' slash ', '^': ' caret ',
    '~': ' tilde ', '`': '', '$': ' dollars ', '€': ' euros ',
    '£': ' pounds ', '¥': ' yen ', '[': ' ', ']': ' ', '{': ' ', 
    '}': ' ', '(': ' ', ')': ' ', '_': ' ', '*': ' '
}
```

### **Content Filtering**
- **Navigation Removal**: Sign up, Follow, Subscribe buttons
- **URL Cleaning**: Replaces URLs with "web link"
- **Email Cleaning**: Replaces emails with "email address"
- **Code Block Handling**: Replaces code with "code block"
- **Whitespace Normalization**: Consistent spacing and line breaks

### **Special Handling**
- **Bullet Points**: Converted to natural language lists
- **Smart Quotes**: Normalized to standard ASCII
- **Unicode Cleanup**: Removes problematic characters
- **Line Break Management**: Preserves paragraph structure

---

## 🖼️ **Image Extraction**

### **Medium Image Processing**
```python
# Priority: Medium images with content detection
medium_pattern = r'https://miro\.medium\.com/[^)"\s\]]+'

# Skip profile images
skip_patterns = [
    'resize:fill:64:64', 'resize:fill:32:32', 'resize:fill:80:80'
]

# Extract dimensions from URL
width_match = re.search(r'resize:fit:(\d+)', img_url)
width = int(width_match.group(1)) if width_match else 608
height = int(width * 0.6)  # Approximate aspect ratio
```

### **Fallback Image Detection**
- **Generic Patterns**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
- **Default Dimensions**: 1200x630 for social media compatibility
- **Caption Handling**: Extracted from alt text when available

---

## 📊 **Metadata Generation**

### **Read Time Calculation**
```python
def calculate_read_time(content: str) -> str:
    words = len(content.split())
    minutes = max(1, round(words / 200))  # 200 WPM average
    return f"{minutes} min read"
```

### **Community Detection**
```python
community_mapping = {
    'blackboxofpm.com': 'Black Box of PM',
    'medium.com': 'Medium',
    'svpg.com': 'SVPG',
    'bringthedonuts.com': 'Bring the Donuts',
    'producttalk.org': 'Product Talk',
    'mindtheproduct.com': 'Mind The Product',
    'a16z.com': 'A16Z',
    # ... additional mappings
}
```

### **Gender Detection**
```python
male_names = {
    'brandon', 'ben', 'ken', 'marty', 'marc', 'ryan', 'roman', 
    'clay', 'daniel', 'tren', 'stewart', 'stuart', 'sachin'
}

female_names = {
    'teresa', 'melissa', 'julie', 'amy', 'hannah', 'shayna',
    'madison', 'eira', 'swetha', 'merci', 'ishita'
}
```

### **Category Assignment**
- **Leadership**: manager, hire, team keywords
- **Discovery**: research, customer, discovery keywords
- **Strategy**: strategy, framework, vision keywords
- **AI Products**: ai, intelligent, machine learning keywords
- **Analytics**: data, metrics, measurement keywords

---

## 📋 **Output Format Specification**

### **JSON Structure**
```json
{
  "track_id": 1,
  "title": "Article Title",
  "url": "https://full-article-url",
  "creator": "Author Name",
  "community": "Publication/Platform",
  "category": "Product Management",
  "sub_category": ["specific_category"],
  "summary": "Enhanced LLM-generated summary with insights and takeaways",
  "releaseDate": "2025-08-20",
  "full_content": "Complete scraped and cleaned article content",
  "read_time": "X min read",
  "main_image": {
    "url": "https://image-url",
    "caption": "Image description",
    "width": 608,
    "height": 401
  },
  "voices": [],
  "gender": "male|female|unknown"
}
```

### **Data Types & Validation**
- **track_id**: Sequential integer starting from 1
- **title**: String, trimmed and cleaned
- **url**: Validated URL with https:// prefix
- **creator**: String, author name from markdown
- **community**: String, detected from URL domain
- **category**: String, always "Product Management"
- **sub_category**: Array of strings, categorized keywords
- **summary**: String, LLM-generated or template fallback
- **releaseDate**: ISO date string (currently defaulted)
- **full_content**: String, cleaned and processed article text
- **read_time**: String, calculated from word count
- **main_image**: Object with url, caption, width, height
- **voices**: Array (reserved for future TTS configuration)
- **gender**: String enum: "male", "female", "unknown"

---

## 🔧 **Error Handling & Recovery**

### **Progress Tracking**
- **Auto-save**: Progress saved every 5 articles
- **Resumption**: `--start-from` parameter for interrupted processing
- **Status Logging**: Detailed console output with success/failure indicators

### **Error Categories**

#### **Scraping Errors**
```python
# URL Access Issues
- HTTP 404/403/500 errors
- SSL certificate problems
- Timeout errors
- Connection failures

# Content Quality Issues  
- Content too short (<500 chars)
- No meaningful text extracted
- Parsing failures
```

#### **LLM Errors**
```python
# Ollama Connection Issues
- Server not running
- Model not available
- API timeout
- Response parsing errors

# Content Processing Issues
- Content too large for model
- Invalid response format
- Empty summary generation
```

#### **File System Errors**
```python
# Input/Output Issues
- File not found
- Permission denied
- Disk space issues
- JSON serialization errors
```

### **Fallback Strategies**
1. **Scraping Failures**: Skip article, log error, continue processing
2. **LLM Failures**: Use template summaries, continue processing  
3. **Image Failures**: Use default image structure
4. **Progress Loss**: Resume from last saved checkpoint

---

## 🧪 **Testing & Validation**

### **Unit Testing**
```bash
# Test markdown parsing
python -c "from master_article_processor import MasterArticleProcessor; 
           processor = MasterArticleProcessor(); 
           articles = processor.parse_markdown_articles('test.md')"

# Test content scraping
python -c "from master_article_processor import MasterArticleProcessor;
           processor = MasterArticleProcessor();
           content = processor.scrape_article_content({'url': 'https://example.com'})"
```

### **Integration Testing**
```bash
# Test with limited articles
python master_article_processor.py --limit 3 --output test_output.json

# Test without LLM
python master_article_processor.py --limit 5 --no-llm --output test_no_llm.json

# Test custom input
python master_article_processor.py --input test_articles.md --output test_custom.json
```

### **Validation Checks**
- **JSON Structure**: Validate against expected schema
- **Content Quality**: Check minimum length and cleanup effectiveness
- **Summary Quality**: Verify LLM summaries are meaningful
- **Image URLs**: Validate extracted image URLs are accessible
- **Data Completeness**: Ensure all required fields are populated

---

## 🔄 **Pipeline Integration**

### **Step 1: Article Processing**
```bash
python master_article_processor.py
# Output: articles_with_summaries.json
```

### **Step 2: Content Extraction** 
```bash
python content_extractor.py articles_with_summaries.json -p google
# Input: JSON from Step 1
# Output: Provider-specific SSML files
```

### **Step 3: Audio Generation**
```bash
python batch_tts_processor.py input_dir output_dir --provider google
# Input: SSML files from Step 2  
# Output: Audio files
```

### **Data Flow Validation**
- **JSON Compatibility**: Output format matches content_extractor.py expectations
- **Field Mapping**: All required fields present for downstream processing
- **Content Quality**: Text quality suitable for TTS processing

---

## 📈 **Performance Optimization**

### **Processing Speed**
- **Parallel Requests**: Multiple concurrent scraping operations
- **Caching**: Avoid re-scraping successfully processed articles
- **Batch Processing**: Group similar operations for efficiency

### **Memory Management**
- **Content Limits**: Truncate extremely large articles
- **Cleanup**: Regular garbage collection for long processing runs
- **Streaming**: Process articles individually to avoid memory buildup

### **Rate Limiting**
- **API Respect**: 1-second delays between LLM requests
- **Scraping Ethics**: Respectful delays between website requests
- **Error Backoff**: Exponential backoff on repeated failures

---

## 🔒 **Security Considerations**

### **Input Validation**
- **URL Sanitization**: Validate and sanitize all input URLs
- **Path Traversal**: Prevent directory traversal in file paths
- **Content Filtering**: Remove potentially malicious content

### **API Security**
- **Environment Variables**: Secure API key storage
- **Request Signing**: Proper authentication for external APIs
- **Error Disclosure**: Avoid exposing sensitive information in error messages

### **Output Security**
- **Content Sanitization**: Clean output content for safe processing
- **File Permissions**: Appropriate permissions on generated files
- **JSON Safety**: Prevent JSON injection vulnerabilities

---

## 🐛 **Troubleshooting Guide**

### **Common Issues**

#### **"No articles parsed from markdown"**
```bash
# Check markdown format
head -20 input.md

# Verify regex pattern matches
python -c "import re; print(re.findall(r'(\d+)\.\s+\*\*(.*?)\*\*', open('input.md').read()))"
```

#### **"Ollama connection failed"**
```bash
# Check Ollama status
ollama list

# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/version
```

#### **"All scraping methods failed"**
```bash
# Test URL manually
curl -I "https://problem-url.com"

# Check user agent
curl -H "User-Agent: Mozilla/5.0..." "https://problem-url.com"

# Try with Selenium explicitly
python master_article_processor.py --no-selenium false
```

#### **"Content too short after cleaning"**
- **Cause**: Over-aggressive content filtering
- **Solution**: Review site-specific cleaning rules
- **Workaround**: Manual content addition or URL replacement

### **Debug Mode**
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Performance Issues**
```bash
# Monitor resource usage
htop

# Check disk space
df -h

# Monitor network
netstat -an | grep 11434
```

---

## 📚 **API Reference**

### **MasterArticleProcessor Class**

#### **Constructor**
```python
def __init__(self, ollama_url="http://localhost:11434", model_name="llama3.2", 
             use_llm=True, use_selenium=True):
```

#### **Key Methods**

##### **parse_markdown_articles(markdown_file: str) -> List[Dict]**
Parses curated markdown file and extracts article metadata.
- **Parameters**: Path to markdown file
- **Returns**: List of article dictionaries with basic metadata
- **Raises**: FileNotFoundError, regex parsing errors

##### **scrape_article_content(article: Dict) -> str**
Scrapes full content from article URL using hybrid approach.
- **Parameters**: Article dictionary with URL
- **Returns**: Cleaned article content string
- **Raises**: Network errors, parsing errors

##### **generate_llm_summary(title: str, full_content: str) -> str**
Generates enhanced summary using Ollama LLM.
- **Parameters**: Article title and full content
- **Returns**: Generated summary string
- **Raises**: Ollama connection errors, model errors

##### **process_articles(markdown_file: str, output_file: str, start_from: int = 1, limit: int = None) -> bool**
Complete processing pipeline from markdown to enhanced JSON.
- **Parameters**: Input/output paths and processing options
- **Returns**: Success/failure boolean
- **Raises**: File system errors, processing errors

---

## 🔄 **Version History**

### **Version 1.0** (August 22, 2025)
- **Initial Release**: Consolidation of all legacy scrapers
- **Core Features**: Markdown parsing, multi-method scraping, LLM integration
- **Supported Providers**: Firecrawl, Requests+BeautifulSoup, Selenium
- **LLM Integration**: Ollama with llama3.2 model
- **Content Processing**: Audio-optimized cleaning pipeline
- **Metadata Generation**: Images, read time, gender detection, categorization

### **Future Enhancements**
- **Multi-threading**: Parallel article processing
- **Advanced Caching**: Persistent content cache
- **Enhanced LLM**: Support for additional model providers
- **Content Validation**: Advanced quality scoring
- **Incremental Updates**: Smart re-processing of changed content

---

## 📞 **Support & Maintenance**

### **Logging**
- **Location**: Console output with timestamps
- **Levels**: INFO (progress), WARNING (recoverable errors), ERROR (failures)
- **Format**: `[timestamp] LEVEL: message`

### **Monitoring**
- **Progress Tracking**: Real-time article processing status
- **Success Metrics**: Articles processed vs. failed
- **Performance Metrics**: Processing time per article
- **Quality Metrics**: Average content length, summary quality

### **Maintenance Tasks**
- **Model Updates**: Regular Ollama model updates
- **Dependency Updates**: Python package maintenance
- **Content Review**: Periodic output quality assessment
- **Performance Tuning**: Optimization based on usage patterns

---

*This specification covers the complete technical implementation of the Master Article Processor. For usage examples and quick start guides, refer to the main project README and Tools documentation.*