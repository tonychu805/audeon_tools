#!/usr/bin/env python3
"""
Master Article Content Processor
Consolidates all scraping functionality into one comprehensive tool.

Pipeline:
1. Parse curated markdown → Basic article structure  
2. Scrape content → Populate full_content using hybrid methods
3. Generate LLM summaries → Rich summaries from full_content
4. Extract images → Populate main_image with dimensions
5. Clean content → Audio-optimized text processing
6. Output JSON → Exact articles_with_summaries.json format

Combines best features from all existing scrapers:
- mindtheproduct_scraper.py: Advanced scraping + LLM
- comprehensive_scraper.py: Image extraction + audio cleaning
- fix_content_cleaning.py: TTS-optimized cleaning
- run_pipeline.py: Multi-provider architecture
"""

import json
import os
import re
import sys
import time
import requests
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# MCP Firecrawl import (if available)
try:
    from mcp import ClientSession
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False

class MasterArticleProcessor:
    def __init__(self, ollama_url="http://localhost:11434", model_name="llama3.2", 
                 use_llm=True, use_selenium=True):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.use_llm_summarization = use_llm
        self.use_selenium = use_selenium
        
        # Gender mapping for enhanced functionality
        self.male_names = {
            'brandon', 'ben', 'ken', 'marty', 'marc', 'ryan', 'roman', 'clay', 
            'daniel', 'tren', 'stewart', 'stuart', 'sachin', 'richard', 'rich',
            'andrew', 'joseph', 'mohit'
        }
        self.female_names = {
            'teresa', 'melissa', 'julie', 'amy', 'hannah', 'shayna', 'madison',
            'eira', 'swetha', 'merci', 'ishita', 'louron', 'iuliia', 'steffi',
            'alena'
        }
    
    def determine_gender(self, name: str) -> str:
        """Determine gender based on first name"""
        first_name = name.split()[0].lower()
        
        if first_name in self.male_names:
            return 'male'
        elif first_name in self.female_names:
            return 'female'
        else:
            return 'unknown'
    
    def parse_markdown_articles(self, markdown_file: str) -> List[Dict]:
        """
        Parse curated markdown file to extract article information
        Enhanced version of process_articles.py functionality
        """
        print(f"Parsing markdown file: {markdown_file}")
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match numbered articles with title, author, URL, and description
        pattern = r'(\d+)\.\s+\*\*(.*?)\*\*\s*-\s*(.*?)\s*\n\s*https://([^\s]+)\s*\n\s*\*(.*?)\*'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        articles = []
        
        for match in matches:
            article_num, title, author, url, basic_description = match
            
            # Clean up the data
            title = title.strip()
            author = author.strip()
            url = f"https://{url.strip()}"
            # Ignore basic description - we'll generate rich summaries later
            
            # Determine community/source from URL
            community = self.determine_community(url)
            
            # Determine category and subcategory
            category, sub_category = self.determine_category(title, basic_description)
            
            # Determine gender
            gender = self.determine_gender(author)
            
            article = {
                "track_id": len(articles) + 1,
                "title": title,
                "url": url,
                "creator": author,
                "community": community,
                "category": category,
                "sub_category": sub_category,
                "summary": "",  # Will be generated from full_content via LLM
                "releaseDate": "2025-08-20",  # Default date, could be enhanced
                "full_content": "",  # Will be populated by scraping
                "read_time": "5 min read",  # Will be calculated from content
                "main_image": {
                    "url": "",
                    "caption": "",
                    "width": 1200,
                    "height": 630
                },
                "voices": [],
                "gender": gender
            }
            
            articles.append(article)
        
        print(f"Parsed {len(articles)} articles from markdown")
        return articles
    
    def determine_community(self, url: str) -> str:
        """Determine community/source from URL"""
        url_lower = url.lower()
        
        if "blackboxofpm.com" in url_lower:
            return "Black Box of PM"
        elif "medium.com" in url_lower:
            return "Medium"
        elif "svpg.com" in url_lower:
            return "SVPG"
        elif "bringthedonuts.com" in url_lower:
            return "Bring the Donuts"
        elif "producttalk.org" in url_lower:
            return "Product Talk"
        elif "melissaperri.com" in url_lower:
            return "Melissa Perri"
        elif "mindtheproduct.com" in url_lower:
            return "Mind The Product"
        elif "a16z.com" in url_lower:
            return "A16Z"
        elif "paulgraham.com" in url_lower:
            return "Paul Graham"
        elif "amplitude.com" in url_lower:
            return "Amplitude"
        elif "intercom.com" in url_lower:
            return "Intercom"
        elif "romanpichler.com" in url_lower:
            return "Roman Pichler"
        elif "sachinrekhi.com" in url_lower:
            return "Sachin Rekhi"
        elif "hbr.org" in url_lower:
            return "Harvard Business Review"
        else:
            return "Unknown"
    
    def determine_category(self, title: str, description: str) -> Tuple[str, List[str]]:
        """Determine category and subcategory from title and description"""
        title_lower = title.lower()
        desc_lower = description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        if any(word in combined for word in ["leadership", "manager", "hire", "team"]):
            return "Product Management", ["leadership"]
        elif any(word in combined for word in ["discovery", "research", "customer"]):
            return "Product Management", ["product_discovery"]
        elif any(word in combined for word in ["strategy", "framework", "vision"]):
            return "Product Management", ["product_strategy"]
        elif any(word in combined for word in ["ai", "intelligent", "machine learning"]):
            return "Product Management", ["ai_products"]
        elif any(word in combined for word in ["okr", "goal", "metric"]):
            return "Product Management", ["goal_setting"]
        elif any(word in combined for word in ["data", "analytics", "measurement"]):
            return "Product Management", ["data_analytics"]
        else:
            return "Product Management", ["product_strategy"]
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is running and model is available"""
        if not self.use_llm_summarization:
            return True
            
        try:
            # Test connection
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            if response.status_code != 200:
                print(f"Warning: Ollama not available (status {response.status_code})")
                return False
            
            # Check model availability
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model.get('name', '') for model in models]
                
                if self.model_name not in available_models:
                    print(f"Warning: Model '{self.model_name}' not available")
                    print(f"Available models: {', '.join(available_models)}")
                    return False
            
            print(f"✓ Ollama connection successful with model '{self.model_name}'")
            return True
            
        except Exception as e:
            print(f"Warning: Ollama connection failed: {e}")
            return False
    
    def scrape_content_firecrawl(self, url: str) -> Optional[str]:
        """Scrape content using Firecrawl MCP (if available)"""
        if not FIRECRAWL_AVAILABLE:
            return None
        
        try:
            # This would use the MCP Firecrawl integration
            # Implementation depends on your MCP setup
            print(f"  Attempting Firecrawl scraping for {url}")
            # TODO: Implement MCP Firecrawl call here
            return None
        except Exception as e:
            print(f"  Firecrawl failed: {e}")
            return None
    
    def scrape_content_requests(self, url: str) -> Optional[str]:
        """Basic content scraping using requests + BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"  Attempting requests scraping for {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Basic HTML parsing (simplified version)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text content
            content = soup.get_text()
            
            # Basic cleaning
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            
            if len(content) > 500:  # Minimum content threshold
                return content
            else:
                return None
                
        except Exception as e:
            print(f"  Requests scraping failed: {e}")
            return None
    
    def scrape_content_selenium(self, url: str) -> Optional[str]:
        """Advanced content scraping using Selenium (fallback method)"""
        if not self.use_selenium:
            return None
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from bs4 import BeautifulSoup
            
            print(f"  Attempting Selenium scraping for {url}")
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(url)
                time.sleep(3)  # Wait for content to load
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "header", "footer", "sidebar"]):
                    element.decompose()
                
                content = soup.get_text()
                
                # Clean content
                lines = (line.strip() for line in content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = '\n'.join(chunk for chunk in chunks if chunk)
                
                if len(content) > 500:
                    return content
                else:
                    return None
                    
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"  Selenium scraping failed: {e}")
            return None
    
    def scrape_article_content(self, article: Dict) -> str:
        """
        Scrape article content using multiple methods (hybrid approach)
        Tries Firecrawl → Requests → Selenium in order
        """
        url = article['url']
        title = article['title']
        
        print(f"Scraping content for: {title}")
        
        # Method 1: Try Firecrawl MCP first
        content = self.scrape_content_firecrawl(url)
        if content:
            print(f"  ✓ Firecrawl successful ({len(content)} chars)")
            return self.clean_content_for_audio(content)
        
        # Method 2: Try basic requests scraping
        content = self.scrape_content_requests(url)
        if content:
            print(f"  ✓ Requests successful ({len(content)} chars)")
            return self.clean_content_for_audio(content)
        
        # Method 3: Try Selenium as fallback
        content = self.scrape_content_selenium(url)
        if content:
            print(f"  ✓ Selenium successful ({len(content)} chars)")
            return self.clean_content_for_audio(content)
        
        print(f"  ✗ All scraping methods failed for {url}")
        return ""
    
    def clean_content_for_audio(self, content: str) -> str:
        """
        Enhanced content cleaning for audio synthesis
        Combines best features from fix_content_cleaning.py and comprehensive_scraper.py
        """
        if not content:
            return ""
        
        # Remove navigation and UI elements
        nav_elements = [
            r'Sign up', r'Sign in', r'Follow', r'Subscribe', r'Share', r'Listen', 
            r'Medium Logo', r'Write', r'Open in app', r'Follow publication',
            r'View comments?\s*\(\d*\)', r'See all from', r'More from', r'Recommended from Medium',
            r'Help', r'Status', r'About', r'Careers', r'Press', r'Blog', r'Privacy', r'Rules', r'Terms',
            r'protected by \*\*reCAPTCHA\*\*', r'reCAPTCHA', r'Recaptcha requires verification'
        ]
        
        for element in nav_elements:
            content = re.sub(element, '', content, flags=re.IGNORECASE)
        
        # Symbol replacements for audio
        replacements = {
            '&': ' and ', '@': ' at ', '#': ' number ', '%': ' percent ',
            '+': ' plus ', '=': ' equals ', '<': ' less than ', '>': ' greater than ',
            '|': ' or ', '\\': ' backslash ', '/': ' slash ', '^': ' caret ',
            '~': ' tilde ', '`': '', '$': ' dollars ', '€': ' euros ',
            '£': ' pounds ', '¥': ' yen ', '[': ' ', ']': ' ', '{': ' ', 
            '}': ' ', '(': ' ', ')': ' ', '_': ' ', '*': ' ',
            '"': ' ', '"': ' ', '"': ' ', ''': ' ', ''': ' ',
            '◦': '. ', '→': ' to ', '←': ' from ', '↑': ' up ', '↓': ' down ',
            '…': ' ', '–': ' ', '—': ' ', '×': ' times ', '÷': ' divided by ',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Clean up URLs and email addresses
        content = re.sub(r'https?://[^\s]+', ' web link ', content)
        content = re.sub(r'www\.[^\s]+', ' web link ', content)
        content = re.sub(r'\S+@\S+\.\S+', ' email address ', content)
        
        # Clean up code blocks
        content = re.sub(r'```[^`]*```', ' code block ', content)
        content = re.sub(r'`[^`]+`', ' code ', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\n ', '\n', content)
        content = re.sub(r' \n', '\n', content)
        
        return content.strip()
    
    def extract_main_image(self, url: str, content: str) -> Dict:
        """
        Enhanced image extraction combining best methods
        From comprehensive_scraper.py and batch_update_articles.py
        """
        # Look for Medium images first
        medium_images = re.findall(r'https://miro\.medium\.com/[^)"\s\]]+', content)
        if medium_images:
            for img_url in medium_images:
                # Skip small profile images
                if any(small in img_url for small in ['resize:fill:64:64', 'resize:fill:32:32', 'resize:fill:80:80']):
                    continue
                
                # Look for larger content images
                if ('resize:fit:' in img_url and '/1*' in img_url) or 'resize:fill:96:96' in img_url:
                    # Extract dimensions from URL if available
                    width_match = re.search(r'resize:fit:(\d+)', img_url)
                    width = int(width_match.group(1)) if width_match else 608
                    height = int(width * 0.6)  # Approximate aspect ratio
                    
                    return {
                        "url": img_url,
                        "caption": "",
                        "width": width,
                        "height": height
                    }
        
        # Look for other image patterns
        other_images = re.findall(r'https://[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)', content, re.IGNORECASE)
        if other_images:
            return {
                "url": other_images[0],
                "caption": "",
                "width": 1200,
                "height": 630
            }
        
        # Default image structure
        return {
            "url": "",
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
    def generate_llm_summary(self, title: str, full_content: str) -> str:
        """
        Generate enhanced summary using Ollama LLM
        Enhanced version from mindtheproduct_scraper.py
        """
        if not self.use_llm_summarization or not full_content or len(full_content.strip()) < 200:
            return ""
        
        try:
            # Truncate content if too long
            max_content_length = 8000
            content_to_summarize = full_content[:max_content_length] if len(full_content) > max_content_length else full_content
            
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
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200,
                    "top_p": 0.9
                }
            }
            
            print(f"  Generating LLM summary...")
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=180)
            response.raise_for_status()
            
            result = response.json()
            summary = result.get('response', '').strip()
            
            # Clean up response
            if summary:
                summary = summary.replace('Summary:', '').strip()
                if summary.startswith('"') and summary.endswith('"'):
                    summary = summary[1:-1]
                
                print(f"  ✓ Generated summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
                return summary
            else:
                return ""
                
        except Exception as e:
            print(f"  Warning: LLM summary generation failed: {e}")
            return ""
    
    def calculate_read_time(self, content: str) -> str:
        """Calculate read time based on word count"""
        if not content:
            return "5 min read"
        
        words = len(content.split())
        minutes = max(1, round(words / 200))  # 200 words per minute
        return f"{minutes} min read"
    
    def process_articles(self, markdown_file: str, output_file: str, 
                        start_from: int = 1, limit: int = None) -> bool:
        """
        Complete article processing pipeline
        """
        print("=== Master Article Processor ===")
        print(f"Input: {markdown_file}")
        print(f"Output: {output_file}")
        
        # Test Ollama connection
        if self.use_llm_summarization:
            if not self.test_ollama_connection():
                print("Warning: Continuing without LLM summarization")
                self.use_llm_summarization = False
        
        # Step 1: Parse markdown
        articles = self.parse_markdown_articles(markdown_file)
        
        if limit:
            articles = articles[:limit]
            print(f"Limited processing to {limit} articles")
        
        # Step 2: Process each article
        processed_count = 0
        
        for i, article in enumerate(articles, 1):
            if i < start_from:
                continue
            
            title = article['title']
            url = article['url']
            
            print(f"\n[{i}/{len(articles)}] Processing: {title}")
            
            # Step 2a: Scrape content
            full_content = self.scrape_article_content(article)
            article['full_content'] = full_content
            
            if full_content:
                # Step 2b: Generate LLM summary
                if self.use_llm_summarization:
                    llm_summary = self.generate_llm_summary(title, full_content)
                    if llm_summary:
                        article['summary'] = llm_summary
                    else:
                        article['summary'] = f"In-depth analysis of {title.lower()}"  # Fallback
                else:
                    article['summary'] = f"Comprehensive guide on {title.lower()}"
                
                # Step 2c: Extract main image
                main_image = self.extract_main_image(url, full_content)
                article['main_image'] = main_image
                
                # Step 2d: Calculate read time
                article['read_time'] = self.calculate_read_time(full_content)
                
                processed_count += 1
                print(f"  ✓ Successfully processed")
            else:
                print(f"  ✗ Failed to get content")
                # Keep basic structure even if scraping fails
                article['summary'] = f"Essential insights on {title.lower()}"
            
            # Save progress every 5 articles
            if i % 5 == 0:
                self.save_articles(articles, output_file)
                print(f"  Progress saved ({i}/{len(articles)})")
        
        # Final save
        self.save_articles(articles, output_file)
        
        print(f"\n=== Processing Complete ===")
        print(f"Successfully processed: {processed_count}/{len(articles)} articles")
        print(f"Output saved to: {output_file}")
        
        return True
    
    def save_articles(self, articles: List[Dict], output_file: str):
        """Save articles to JSON file with exact format matching"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving articles: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Master Article Content Processor - Consolidates all scraping functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all articles with LLM summaries
  python master_article_processor.py --input curated_list.md --output articles.json
  
  # Process first 5 articles for testing
  python master_article_processor.py --input curated_list.md --output test.json --limit 5
  
  # Process without LLM (faster, basic summaries)
  python master_article_processor.py --input curated_list.md --output articles.json --no-llm
  
  # Resume processing from article 10
  python master_article_processor.py --input curated_list.md --output articles.json --start-from 10
        """
    )
    
    parser.add_argument('--input', '-i', 
                       default='../Content/articles/raw/Curated Content List for Audiobook App.markdown',
                       help='Input markdown file with curated articles')
    parser.add_argument('--output', '-o',
                       default='../Content/articles/raw_metadata/articles_with_summaries.json', 
                       help='Output JSON file')
    parser.add_argument('--model', '-m', default='llama3.2',
                       help='Ollama model name for summaries (default: llama3.2)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama server URL (default: http://localhost:11434)')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM summary generation (faster processing)')
    parser.add_argument('--no-selenium', action='store_true',
                       help='Disable Selenium fallback scraping')
    parser.add_argument('--start-from', type=int, default=1,
                       help='Start processing from article number (for resuming)')
    parser.add_argument('--limit', type=int,
                       help='Limit number of articles to process (for testing)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize processor
    processor = MasterArticleProcessor(
        ollama_url=args.ollama_url,
        model_name=args.model,
        use_llm=not args.no_llm,
        use_selenium=not args.no_selenium
    )
    
    # Process articles
    success = processor.process_articles(
        args.input, 
        args.output, 
        args.start_from, 
        args.limit
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()