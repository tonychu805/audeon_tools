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
                "releaseDate": "",  # Will be extracted from article content
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
    
    def scrape_content_firecrawl(self, url: str) -> Optional[Dict]:
        """Scrape content using Firecrawl MCP (if available)"""
        try:
            print(f"  Attempting Firecrawl scraping for {url}")
            # Use the MCP Firecrawl tool for clean content extraction with metadata
            # This would ideally call the firecrawl tool directly
            # For now, return None to fall back to other methods
            # 
            # Expected implementation:
            # result = mcp_firecrawl_scrape(url, formats=['markdown', 'screenshot'], onlyMainContent=True)
            # if result:
            #     return {
            #         'content': result.get('markdown', ''),
            #         'metadata': {
            #             'publication_date': extract_date_from_firecrawl(result),
            #             'images': extract_images_from_firecrawl(result),
            #             'title': result.get('title'),
            #             'description': result.get('description')
            #         }
            #     }
            return None
        except Exception as e:
            print(f"  Firecrawl failed: {e}")
            return None
    
    def scrape_content_requests(self, url: str) -> Optional[Dict]:
        """Enhanced content scraping using requests + BeautifulSoup with article extraction"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"  Attempting requests scraping for {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata first (dates, images)
            metadata = self.extract_html_metadata(soup, url)
            
            # Try to extract main article content using multiple strategies
            article_content = self.extract_main_article_content(soup)
            
            if article_content and len(article_content) > 500:
                return {
                    'content': article_content,
                    'metadata': metadata
                }
            else:
                return None
                
        except Exception as e:
            print(f"  Requests scraping failed: {e}")
            return None
    
    def extract_html_metadata(self, soup, url: str) -> Dict:
        """
        Extract metadata from HTML including publication dates and images
        """
        metadata = {
            'publication_date': None,
            'images': [],
            'title': None,
            'description': None
        }
        
        # Extract publication date from meta tags
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[property="article:published"]', 
            'meta[name="article:published_time"]',
            'meta[name="published"]',
            'meta[name="date"]',
            'meta[name="publish_date"]',
            'meta[name="publication-date"]',
            'meta[property="og:published_time"]',
            'meta[property="article:modified_time"]',
            'meta[name="last-modified"]',
            'time[datetime]',
            '[datetime]',
            'time[pubdate]',
            '.date',
            '.post-date',
            '.publish-date',
            '.article-date'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for element in elements:
                date_value = element.get('content') or element.get('datetime') or element.get_text()
                if date_value:
                    # Try to parse the date
                    try:
                        from datetime import datetime
                        import re
                        
                        # Clean the date string
                        date_clean = re.sub(r'[T\s]\d{2}:\d{2}.*$', '', date_value.strip())
                        
                        # Try various date formats
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                            try:
                                dt = datetime.strptime(date_clean, fmt)
                                metadata['publication_date'] = dt.strftime('%Y-%m-%d')
                                print(f"    ✓ Found meta date: {metadata['publication_date']}")
                                break
                            except ValueError:
                                continue
                        if metadata['publication_date']:
                            break
                    except:
                        continue
            if metadata['publication_date']:
                break
        
        # Site-specific date extraction patterns
        if not metadata['publication_date']:
            site_specific_date = self.extract_site_specific_date(soup, url)
            if site_specific_date:
                metadata['publication_date'] = site_specific_date
        
        # Extract images from various sources
        image_selectors = [
            'meta[property="og:image"]',
            'meta[name="og:image"]', 
            'meta[property="twitter:image"]',
            'meta[name="twitter:image"]',
            'article img',
            'main img',
            '.post-content img',
            '.entry-content img',
            '.article-content img'
        ]
        
        found_images = set()  # Use set to avoid duplicates
        
        for selector in image_selectors:
            elements = soup.select(selector)
            for element in elements:
                img_url = element.get('content') or element.get('src')
                if img_url:
                    # Make absolute URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urljoin
                        img_url = urljoin(url, img_url)
                    
                    # Skip very small images or icons
                    if any(skip in img_url.lower() for skip in ['favicon', 'icon', '16x16', '32x32', 'logo-small']):
                        continue
                    
                    # Extract dimensions if available
                    width = element.get('width') or 1200
                    height = element.get('height') or 630
                    
                    try:
                        width = int(width)
                        height = int(height)
                    except:
                        width, height = 1200, 630
                    
                    # Skip very small images
                    if width < 100 or height < 100:
                        continue
                    
                    if img_url not in found_images:
                        found_images.add(img_url)
                        metadata['images'].append({
                            'url': img_url,
                            'width': width,
                            'height': height,
                            'alt': element.get('alt', ''),
                            'source': selector
                        })
                        
                        # Stop after finding first good image from meta tags
                        if 'meta' in selector and len(metadata['images']) >= 1:
                            break
        
        if metadata['images']:
            print(f"    ✓ Found {len(metadata['images'])} images")
        
        # Extract title and description
        title_element = soup.select_one('meta[property="og:title"]') or soup.select_one('title')
        if title_element:
            metadata['title'] = title_element.get('content') or title_element.get_text()
        
        desc_element = soup.select_one('meta[property="og:description"]') or soup.select_one('meta[name="description"]')
        if desc_element:
            metadata['description'] = desc_element.get('content')
        
        return metadata
    
    def extract_site_specific_date(self, soup, url: str) -> Optional[str]:
        """Extract publication date using site-specific patterns"""
        from datetime import datetime
        import re
        
        # LinkedIn specific patterns
        if 'linkedin.com' in url:
            # Look for date in various LinkedIn selectors
            linkedin_selectors = [
                '.update-components-text .visually-hidden',
                '.article-header-meta time',
                '[data-test-id="post-date"]',
                '.article-date'
            ]
            for selector in linkedin_selectors:
                elements = soup.select(selector)
                for el in elements:
                    date_text = el.get_text().strip()
                    if re.search(r'\d{4}|\d{1,2}/\d{1,2}', date_text):
                        parsed = self.parse_date_from_text(date_text)
                        if parsed:
                            print(f"    ✓ Found LinkedIn date: {parsed}")
                            return parsed
        
        # Substack specific patterns
        elif 'substack.com' in url:
            substack_selectors = [
                '.pencraft time',
                '.post-date',
                '[data-testid="post-date"]'
            ]
            for selector in substack_selectors:
                elements = soup.select(selector)
                for el in elements:
                    date_text = el.get('datetime') or el.get_text().strip()
                    parsed = self.parse_date_from_text(date_text)
                    if parsed:
                        print(f"    ✓ Found Substack date: {parsed}")
                        return parsed
        
        # PMArchive specific patterns  
        elif 'pmarchive.com' in url:
            # Look for dates in content headers
            content_text = soup.get_text()[:2000]  # First 2000 chars
            # Try "Posted on Month DD, YYYY" format first
            date_match = re.search(r'Posted on ([A-Za-z]+ \d{1,2}, \d{4})', content_text)
            if not date_match:
                # Try general "Month DD, YYYY" format
                date_match = re.search(r'((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})', content_text)
            
            if date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), '%B %d, %Y')
                    parsed_date = dt.strftime('%Y-%m-%d')
                    print(f"    ✓ Found PMArchive date: {parsed_date}")
                    return parsed_date
                except:
                    pass
        
        # Airtable blog specific patterns
        elif 'airtable.com' in url:
            airtable_selectors = [
                '.blog-post-date',
                '.post-meta time',
                '[data-testid="publish-date"]'
            ]
            for selector in airtable_selectors:
                elements = soup.select(selector)
                for el in elements:
                    date_text = el.get_text().strip()
                    parsed = self.parse_date_from_text(date_text)
                    if parsed:
                        print(f"    ✓ Found Airtable date: {parsed}")
                        return parsed
        
        return None
    
    def parse_date_from_text(self, date_text: str) -> Optional[str]:
        """Parse date from various text formats"""
        from datetime import datetime
        import re
        
        if not date_text:
            return None
            
        # Clean the text
        date_text = re.sub(r'[T\s]\d{2}:\d{2}.*$', '', date_text.strip())
        
        # Try various formats
        formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y',
            '%B %Y', '%b %Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_text, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return None
    
    def extract_main_article_content(self, soup) -> Optional[str]:
        """
        Extract main article content using multiple content identification strategies
        """
        # Strategy 1: Look for common article content selectors
        article_selectors = [
            'article', 
            '[role="main"]',
            '.post-content', 
            '.entry-content', 
            '.article-content',
            '.post-body',
            '.content',
            'main',
            '.main-content',
            '.story-body',
            '.article-body'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                main_element = elements[0]
                content = self.clean_article_element(main_element)
                if content and len(content) > 500:
                    print(f"    ✓ Found content using selector: {selector}")
                    return content
        
        # Strategy 2: Look for specific site patterns
        content = self.extract_site_specific_content(soup)
        if content:
            return content
        
        # Strategy 3: Find largest text block (fallback)
        content = self.extract_largest_text_block(soup)
        if content:
            return content
        
        return None
    
    def extract_site_specific_content(self, soup) -> Optional[str]:
        """Extract content using site-specific patterns"""
        
        # Medium.com specific extraction
        medium_selectors = [
            '[data-testid="storyContent"]',
            '.postArticle-content',
            'article section',
            '.section-content'
        ]
        
        for selector in medium_selectors:
            elements = soup.select(selector)
            if elements:
                content = self.clean_article_element(elements[0])
                if content and len(content) > 300:
                    print(f"    ✓ Medium content found with selector: {selector}")
                    return content
        
        # SVPG specific extraction  
        svpg_content = soup.find('div', class_='post-content')
        if svpg_content:
            content = self.clean_article_element(svpg_content)
            if content and len(content) > 300:
                print(f"    ✓ SVPG content found")
                return content
        
        # Harvard Business Review specific extraction
        hbr_selectors = [
            '.article-body',
            '[data-module="ArticleBody"]',
            '.article-content-container',
            '#main-content article'
        ]
        
        for selector in hbr_selectors:
            elements = soup.select(selector)
            if elements:
                content = self.clean_article_element(elements[0])
                if content and len(content) > 300:
                    print(f"    ✓ HBR content found with selector: {selector}")
                    return content
        
        # WordPress/blog specific
        wp_selectors = [
            '.entry-content',
            '.post-content', 
            '.content-area',
            '#content'
        ]
        
        for selector in wp_selectors:
            elements = soup.select(selector)
            if elements:
                content = self.clean_article_element(elements[0])
                if content and len(content) > 300:
                    print(f"    ✓ WordPress content found with selector: {selector}")
                    return content
        
        return None
    
    def extract_largest_text_block(self, soup) -> Optional[str]:
        """Find the largest coherent text block as fallback method"""
        
        # Remove unwanted elements first
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                            'sidebar', 'aside', 'form', 'button', 'input']):
            element.decompose()
        
        # Find all potential content containers
        containers = soup.find_all(['div', 'section', 'article', 'main'])
        
        best_content = ""
        best_score = 0
        
        for container in containers:
            # Skip if container has navigation-like classes
            classes = container.get('class', [])
            if any(nav_class in ' '.join(classes).lower() 
                  for nav_class in ['nav', 'sidebar', 'footer', 'header', 'menu', 'social', 'share']):
                continue
            
            text = container.get_text(strip=True)
            
            # Score based on length and paragraph structure
            paragraphs = text.split('\n\n')
            score = len(text) + (len(paragraphs) * 10)  # Bonus for paragraph structure
            
            if score > best_score and len(text) > 500:
                best_score = score
                best_content = self.clean_article_element(container)
        
        if best_content:
            print(f"    ✓ Largest text block found ({len(best_content)} chars)")
            return best_content
        
        return None
    
    def clean_article_element(self, element) -> str:
        """Clean and extract text from a BeautifulSoup element"""
        if not element:
            return ""
        
        # Remove unwanted child elements
        unwanted_elements = [
            'script', 'style', 'nav', 'header', 'footer', 'aside', 
            'form', 'button', 'input', 'select', 'textarea',
            '[class*="share"]', '[class*="social"]', '[class*="nav"]',
            '[class*="sidebar"]', '[class*="menu"]', '[class*="footer"]',
            '[class*="header"]', '.comments', '#comments',
            '.related', '.recommended', '.more-stories'
        ]
        
        for selector in unwanted_elements:
            for unwanted in element.select(selector):
                unwanted.decompose()
        
        # Get text with proper spacing
        text = element.get_text(separator='\n', strip=True)
        
        # Clean up the text
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not self.is_navigation_text(line):
                lines.append(line)
        
        # Join lines and clean up paragraph spacing
        content = '\n'.join(lines)
        
        # Remove multiple consecutive newlines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return content.strip()
    
    def is_navigation_text(self, text: str) -> bool:
        """Check if text looks like navigation/UI elements"""
        text_lower = text.lower().strip()
        
        # Common navigation patterns
        nav_patterns = [
            'follow', 'subscribe', 'sign up', 'sign in', 'login', 'register',
            'share on', 'tweet', 'facebook', 'linkedin', 'pinterest',
            'read more', 'see all', 'view all', 'show more', 'load more',
            'next article', 'previous article', 'related articles',
            'comments', 'leave a comment', 'post comment',
            'tags:', 'categories:', 'filed under',
            'about the author', 'author bio', 'more from',
            'menu', 'home', 'about', 'contact', 'privacy', 'terms',
            'cookie', 'gdpr', 'consent'
        ]
        
        # Check if text matches navigation patterns
        if any(pattern in text_lower for pattern in nav_patterns):
            return True
        
        # Check if text is very short (likely a button or link)
        if len(text.strip()) < 3:
            return True
        
        # Check if text is just numbers or symbols
        if re.match(r'^[\d\s\-\.\,\(\)]+$', text.strip()):
            return True
        
        return False
    
    def scrape_content_selenium(self, url: str) -> Optional[Dict]:
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
                
                # Extract metadata first
                metadata = self.extract_html_metadata(soup, url)
                
                # Extract main content
                article_content = self.extract_main_article_content(soup)
                
                if article_content and len(article_content) > 500:
                    return {
                        'content': article_content,
                        'metadata': metadata
                    }
                else:
                    return None
                    
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"  Selenium scraping failed: {e}")
            return None
    
    def scrape_article_content(self, article: Dict) -> Dict:
        """
        Scrape article content using multiple methods (hybrid approach)
        Tries Firecrawl → Requests → Selenium in order
        Returns dict with content and metadata
        """
        url = article['url']
        title = article['title']
        
        print(f"Scraping content for: {title}")
        
        # Method 1: Try Firecrawl MCP first
        result = self.scrape_content_firecrawl(url)
        if result and result.get('content'):
            content = result['content']
            print(f"  ✓ Firecrawl successful ({len(content)} chars)")
            return {
                'content': self.clean_content_for_audio(content),
                'metadata': result.get('metadata', {})
            }
        
        # Method 2: Try basic requests scraping
        result = self.scrape_content_requests(url)
        if result and result.get('content'):
            content = result['content']
            print(f"  ✓ Requests successful ({len(content)} chars)")
            return {
                'content': self.clean_content_for_audio(content),
                'metadata': result.get('metadata', {})
            }
        
        # Method 3: Try Selenium as fallback
        result = self.scrape_content_selenium(url)
        if result and result.get('content'):
            content = result['content']
            print(f"  ✓ Selenium successful ({len(content)} chars)")
            return {
                'content': self.clean_content_for_audio(content),
                'metadata': result.get('metadata', {})
            }
        
        print(f"  ✗ All scraping methods failed for {url}")
        return {'content': '', 'metadata': {}}
    
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
        
        # Handle markdown headers BEFORE general symbol replacement
        # Remove markdown headers (# ## ###) but keep the text
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Remove standalone # symbols that aren't part of headers
        content = re.sub(r'\s#\s', ' ', content)
        content = re.sub(r'^#\s*$', '', content, flags=re.MULTILINE)
        
        # Symbol replacements for audio (without harmful # replacement)
        replacements = {
            '&': ' and ', '@': ' at ', '%': ' percent ',
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
        Enhanced image extraction for various site types
        """
        # Try to use Firecrawl for better image extraction
        try:
            # This would ideally use Firecrawl to get structured content with images
            # For now, fall back to pattern matching
            pass
        except:
            pass
        
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
        
        # Look for various image patterns in content
        image_patterns = [
            r'https://[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)',  # Direct image URLs
            r'https://[^)"\s\]]+/[^)"\s\]]*\.(jpg|jpeg|png|webp|gif)',  # Images in paths
            r'!\[.*?\]\((https://[^)]+\.(jpg|jpeg|png|webp|gif))\)',  # Markdown images
            r'<img[^>]+src="(https://[^"]+\.(jpg|jpeg|png|webp|gif))"',  # HTML img tags
        ]
        
        for pattern in image_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Handle tuple returns from groups
                img_url = match[0] if isinstance(match, tuple) else match
                
                # Skip very small or icon images
                if any(skip in img_url.lower() for skip in ['icon', 'logo', 'avatar', '16x16', '32x32', 'favicon']):
                    continue
                
                # Extract dimensions if available in URL
                width = 1200  # Default
                height = 630  # Default
                
                width_match = re.search(r'(\d+)x(\d+)', img_url)
                if width_match:
                    width = int(width_match.group(1))
                    height = int(width_match.group(2))
                
                return {
                    "url": img_url,
                    "caption": "",
                    "width": width,
                    "height": height
                }
        
        # Try to get social media images from Open Graph or meta tags
        # (This would require parsing HTML, which basic content scraping might not provide)
        
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
    
    def extract_publication_date(self, url: str, content: str) -> str:
        """
        Extract publication date from article content and URL
        Returns date in YYYY-MM-DD format
        """
        import re
        from datetime import datetime
        
        # Try to extract date from URL patterns first
        url_date_patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',  # /2024/03/15/
            r'/(\d{4})-(\d{2})-(\d{2})',   # /2024-03-15
            r'/(\d{4})_(\d{2})_(\d{2})',   # /2024_03_15
        ]
        
        for pattern in url_date_patterns:
            match = re.search(pattern, url)
            if match:
                year, month, day = match.groups()
                try:
                    # Validate date
                    datetime(int(year), int(month), int(day))
                    return f"{year}-{month}-{day}"
                except ValueError:
                    continue
        
        # Try to extract date from content
        content_date_patterns = [
            # Common date formats in articles
            r'(?:Published|Posted|Date):\s*([A-Za-z]+ \d{1,2}, \d{4})',  # "Published: March 15, 2024"
            # Use explicit month names to avoid false matches
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4})',
            r'(\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4})',
            r'(\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4})',
            r'(\d{4}-\d{2}-\d{2})',         # "2024-03-15"
            r'(\d{1,2}/\d{1,2}/\d{4})',     # "3/15/2024" or "03/15/2024"
        ]
        
        for pattern in content_date_patterns:
            matches = re.findall(pattern, content[:2000])  # Check first 2000 chars
            for match in matches:
                try:
                    # Try to parse the date
                    if re.match(r'\d{4}-\d{2}-\d{2}', match):
                        # Already in YYYY-MM-DD format
                        return match
                    elif re.match(r'\d{2}/\d{2}/\d{4}', match):
                        # MM/DD/YYYY format
                        dt = datetime.strptime(match, '%m/%d/%Y')
                        return dt.strftime('%Y-%m-%d')
                    elif any(month in match for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                                                         'January', 'February', 'March', 'April',
                                                         'June', 'July', 'August', 'September', 
                                                         'October', 'November', 'December']):
                        # Month name formats
                        for fmt in ['%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y']:
                            try:
                                dt = datetime.strptime(match, fmt)
                                return dt.strftime('%Y-%m-%d')
                            except ValueError:
                                continue
                except (ValueError, AttributeError):
                    continue
        
        # Default fallback - return empty string to indicate no date found
        print(f"  ⚠ No publication date found for URL: {url}")
        return ""
    
    def calculate_read_time(self, content: str) -> str:
        """Calculate read time based on word count"""
        if not content:
            return "5 min read"
        
        words = len(content.split())
        minutes = max(1, round(words / 200))  # 200 words per minute
        return f"{minutes} min read"
    
    def get_main_image_from_metadata(self, metadata: Dict, url: str, content: str) -> Dict:
        """Get main image from metadata or fallback to content parsing"""
        # First, try to get image from metadata
        if metadata.get('images'):
            # Use the first image from metadata
            img_data = metadata['images'][0]
            return {
                "url": img_data['url'],
                "caption": img_data.get('alt', ''),
                "width": img_data.get('width', 1200),
                "height": img_data.get('height', 630)
            }
        
        # Fallback to original content parsing method
        return self.extract_main_image(url, content)
    
    def get_publication_date_from_metadata(self, metadata: Dict, url: str, content: str) -> str:
        """Get publication date from metadata or fallback to content parsing"""
        # First, try to get date from metadata
        if metadata.get('publication_date'):
            print(f"  ✓ Using metadata date: {metadata['publication_date']}")
            return metadata['publication_date']
        
        # Fallback to original content parsing method
        return self.extract_publication_date(url, content)
    
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
            
            # Step 2a: Scrape content with metadata
            scrape_result = self.scrape_article_content(article)
            full_content = scrape_result.get('content', '')
            metadata = scrape_result.get('metadata', {})
            
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
                
                # Step 2c: Extract main image (prefer metadata, fallback to content parsing)
                main_image = self.get_main_image_from_metadata(metadata, url, full_content)
                article['main_image'] = main_image
                
                # Step 2d: Extract publication date (prefer metadata, fallback to content parsing)
                publication_date = self.get_publication_date_from_metadata(metadata, url, full_content)
                article['releaseDate'] = publication_date
                
                # Step 2e: Calculate read time
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