#!/usr/bin/env python3
"""
Mind the Product Editorial Scraper
Scrapes articles from https://www.mindtheproduct.com/articles/
Extracts titles, URLs, authors, dates, categories, summaries, and full content
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse
import sys
import subprocess
import os
from pathlib import Path
from typing import Optional

# Try to import Selenium for JavaScript-rendered content
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class MindTheProductScraper:
    def __init__(self, use_llm_summarization: bool = True, ollama_url: str = "http://localhost:11434", model_name: str = "mistral:latest"):
        self.base_url = "https://www.mindtheproduct.com"
        self.articles_url = "https://www.mindtheproduct.com/articles/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.articles = []
        self.use_llm_summarization = use_llm_summarization
        self.ollama_url = ollama_url
        self.model_name = model_name
        
        # Test Ollama connection if LLM summarization is enabled
        if use_llm_summarization:
            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [model['name'] for model in models]
                    if model_name in model_names:
                        print(f"Connected to Ollama. Using model: {model_name}")
                    else:
                        print(f"Warning: Model {model_name} not found. Available models: {model_names}")
                        print("LLM summarization will be disabled.")
                        self.use_llm_summarization = False
                else:
                    print(f"Warning: Cannot connect to Ollama at {ollama_url}. LLM summarization will be disabled.")
                    self.use_llm_summarization = False
            except requests.RequestException:
                print(f"Warning: Cannot connect to Ollama at {ollama_url}. LLM summarization will be disabled.")
                self.use_llm_summarization = False
    
    def setup_selenium_driver(self, headless=True):
        """Setup Chrome WebDriver for JavaScript-rendered content"""
        if not SELENIUM_AVAILABLE:
            print("Warning: Selenium not available. Install with: pip install selenium")
            return None
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"Warning: Failed to setup Chrome driver: {e}")
            print("Please install ChromeDriver: brew install chromedriver")
            return None
        
    def get_page_content(self, url, retries=3):
        """Fetch page content with retries"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return None
    
    def generate_llm_summary(self, full_content: str, title: str) -> str:
        """Generate a summary using Ollama local LLM"""
        if not self.use_llm_summarization:
            return ""
        
        if not full_content or len(full_content.strip()) < 100:
            return ""
        
        try:
            # Truncate content if it's too long
            max_content_length = 12000  # Llama can handle more tokens than GPT-3.5
            content_to_summarize = full_content[:max_content_length] if len(full_content) > max_content_length else full_content
            
            prompt = f"""Please write a concise 2-3 sentence summary of this product management article titled "{title}". 
Focus on the main insights, key takeaways, or practical advice presented in the article.

Article content:
{content_to_summarize}

Summary:"""
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            summary = result.get('response', '').strip()
            
            if summary:
                print(f"  Generated summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
                return summary
            else:
                print("  Warning: Empty summary generated")
                return ""
            
        except Exception as e:
            print(f"  Warning: Failed to generate LLM summary: {e}")
            return ""
                    
    def extract_article_list_selenium(self):
        """Extract article metadata from the articles page using Selenium"""
        print("Fetching articles list with Selenium...")
        driver = self.setup_selenium_driver()
        if not driver:
            return []
        
        try:
            driver.get(self.articles_url)
            # Wait for content to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Additional wait for dynamic content
            
            # Try to wait for specific content to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
            except TimeoutException:
                print("Warning: No links found on page, continuing anyway...")
            
            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            
            # Debug: Count total links found
            all_links = soup.find_all('a', href=True)
            print(f"Debug: Found {len(all_links)} total links on page")
            
        except Exception as e:
            print(f"Error fetching articles page with Selenium: {e}")
            driver.quit()
            return []
        finally:
            driver.quit()
        
        return self._parse_article_list(soup)
    
    def extract_article_list(self):
        """Extract article metadata from the articles page"""
        print("Fetching articles list...")
        content = self.get_page_content(self.articles_url)
        if not content:
            print("Failed to fetch articles page with regular request, trying Selenium...")
            return self.extract_article_list_selenium()
            
        soup = BeautifulSoup(content, 'html.parser')
        return self._parse_article_list(soup)
    
    def _parse_article_list(self, soup):
        """Parse article list from BeautifulSoup object"""
        articles = []
        
        # Find all article links - Mind the Product articles have descriptive URLs
        links = soup.find_all('a', href=True)
        article_links = []
        
        for link in links:
            href = link.get('href', '')
            # Skip unwanted links
            if any(skip in href for skip in ['/onboarding/', '/articles/', '/category/', '/tag/', '/author/', '/profile/', '/wp-', '/feed', '#', '.jpg', '.png', '.gif', 'mailto:', 'javascript:', 'tel:']):
                continue
            # Look for article-like URLs (descriptive paths ending with /)
            if (href.startswith('https://www.mindtheproduct.com/') or href.startswith('/')) and href.endswith('/') and href.count('/') >= 3:
                # Filter out navigation and non-article pages
                path = href.replace('https://www.mindtheproduct.com', '')
                if not any(nav in path for nav in ['/page/', '/search/', '/login', '/register', '/contact']):
                    article_links.append(link)
        
        print(f"Found {len(article_links)} potential article links")
        
        # Extract metadata from article links
        seen_urls = set()
        for link in article_links:  # Process all found article links
            href = urljoin(self.base_url, link.get('href', ''))
            if href in seen_urls:
                continue
            seen_urls.add(href)
            
            title = link.get_text(strip=True)
            if title and len(title) > 10:  # Filter out short titles
                article = {
                    'title': title,
                    'url': href,
                    'author': '',
                    'date': '',
                    'category': '',
                    'summary': '',
                    'read_time': ''
                }
                
                # Try to find metadata in parent containers
                parent = link.find_parent()
                if parent:
                    # Look for author
                    author_text = parent.get_text()
                    author_match = re.search(r'by\s+([A-Z][a-zA-Z\s]+)', author_text)
                    if author_match:
                        article['author'] = author_match.group(1).strip()
                    
                    # Look for read time
                    read_time_match = re.search(r'(\d+)\s*min\s*read', author_text, re.I)
                    if read_time_match:
                        article['read_time'] = f"{read_time_match.group(1)} min read"
                
                articles.append(article)
        
        # If still no good articles, try JSON-LD
        if len(articles) < 5:
            json_articles = self.extract_from_json_ld(soup)
            articles.extend(json_articles)
            
        return articles
        
    def extract_article_metadata(self, element):
        """Extract metadata from a single article element"""
        article = {}
        
        # Title and URL
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|headline'))
        if not title_elem:
            title_elem = element.find('a')
            
        if title_elem:
            if title_elem.name == 'a':
                article['title'] = title_elem.get_text(strip=True)
                article['url'] = urljoin(self.base_url, title_elem.get('href', ''))
            else:
                article['title'] = title_elem.get_text(strip=True)
                link = title_elem.find('a') or element.find('a')
                if link:
                    article['url'] = urljoin(self.base_url, link.get('href', ''))
                    
        # Author
        author_elem = element.find(class_=re.compile(r'author|byline|writer'))
        if author_elem:
            article['author'] = author_elem.get_text(strip=True)
            
        # Date
        date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time|published'))
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
            article['date'] = self.parse_date(date_text)
            
        # Category/Tags
        category_elem = element.find(class_=re.compile(r'category|tag|label'))
        if category_elem:
            article['category'] = category_elem.get_text(strip=True)
            
        # Summary/Excerpt
        summary_elem = element.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description'))
        if summary_elem:
            article['summary'] = summary_elem.get_text(strip=True)
            
        # Read time
        read_time_elem = element.find(class_=re.compile(r'read.?time|duration'))
        if read_time_elem:
            article['read_time'] = read_time_elem.get_text(strip=True)
            
        return article if article.get('title') and article.get('url') else None
        
    def extract_from_json_ld(self, soup):
        """Try to extract article data from JSON-LD structured data"""
        articles = []
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['Article', 'BlogPosting']:
                            articles.append(self.parse_json_ld_article(item))
                elif data.get('@type') in ['Article', 'BlogPosting']:
                    articles.append(self.parse_json_ld_article(data))
            except (json.JSONDecodeError, AttributeError):
                continue
                
        return articles
        
    def parse_json_ld_article(self, data):
        """Parse article from JSON-LD structured data"""
        article = {}
        article['title'] = data.get('headline', data.get('name', ''))
        article['url'] = data.get('url', data.get('@id', ''))
        article['summary'] = data.get('description', '')
        article['date'] = data.get('datePublished', data.get('dateCreated', ''))
        
        author = data.get('author')
        if author:
            if isinstance(author, dict):
                article['author'] = author.get('name', '')
            elif isinstance(author, list) and author:
                article['author'] = author[0].get('name', '') if isinstance(author[0], dict) else str(author[0])
            else:
                article['author'] = str(author)
                
        return article
        
    def parse_date(self, date_string):
        """Parse various date formats"""
        if not date_string:
            return ''
            
        # Common date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\w+ \d{1,2}, \d{4})',
            r'(\d{1,2} \w+ \d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_string)
            if match:
                return match.group(1)
                
        return date_string
        
    def scrape_full_article(self, url, debug=False):
        """Scrape full content from individual article page"""
        print(f"Scraping full content from: {url}")
        content = self.get_page_content(url)
        if not content:
            return '', '', '', '', '', ''
            
        soup = BeautifulSoup(content, 'html.parser')
        
        if debug:
            # Check for lists in the entire page before any processing
            all_lists = soup.find_all(['ul', 'ol'])
            print(f"\n🔍 RAW HTML ANALYSIS:")
            print(f"  Total lists in entire page: {len(all_lists)}")
            
            # Check specifically for wp-block-list with different approaches
            wp_lists_exact = soup.find_all('ul', class_='wp-block-list')
            wp_lists_contains = soup.find_all('ul', class_=lambda x: x and 'wp-block-list' in x)
            wp_lists_attr = soup.find_all('ul', attrs={'class': lambda x: x and 'wp-block-list' in str(x)})
            print(f"  wp-block-list (exact): {len(wp_lists_exact)}")
            print(f"  wp-block-list (contains): {len(wp_lists_contains)}")
            print(f"  wp-block-list (attr): {len(wp_lists_attr)}")
            
            # Look for ANY element with wp-block-list class
            any_wp_block = soup.find_all(attrs={'class': lambda x: x and 'wp-block-list' in str(x)})
            print(f"  Any elements with wp-block-list: {len(any_wp_block)}")
            for elem in any_wp_block[:3]:
                print(f"    {elem.name} with class {elem.get('class', [])}: {elem.get_text(strip=True)[:50]}")
            
            # Show ALL lists in the page to see where they are
            print(f"  Analyzing all {len(all_lists)} lists:")
            for i, ul in enumerate(all_lists):
                items = ul.find_all('li')
                classes = ul.get('class', [])
                parent_class = ul.parent.get('class', []) if ul.parent else []
                print(f"    List {i+1}: {len(items)} items, classes: {classes}, parent: {parent_class}")
                if items:
                    first_item_text = items[0].get_text(strip=True)[:80]
                    print(f"      First item: {first_item_text}")
                else:
                    print(f"      (empty list)")
        
        # Check for embedded videos and skip if found
        video_selectors = [
            'video', 'iframe[src*="youtube"]', 'iframe[src*="vimeo"]', 
            'iframe[src*="wistia"]', 'iframe[src*="loom"]',
            '.video-embed', '.youtube-embed', '.vimeo-embed',
            '[class*="video"]', '[class*="embed"]'
        ]
        
        has_video = False
        for selector in video_selectors:
            if soup.select(selector):
                has_video = True
                break
        
        if has_video:
            print(f"  Skipping article with embedded video: {url}")
            return 'SKIPPED_VIDEO', '', '', '', '', ''
        
        # Extract category from multiple possible selectors
        category = ''
        category_selectors = [
            'div[class*="text-[1rem]"] a[href*="/category/"]',
            '.category a',
            '.post-categories a',
            '[class*="category"] a',
            'a[href*="/category/"]'
        ]
        
        for selector in category_selectors:
            category_links = soup.select(selector)
            if category_links:
                categories = [link.get_text(strip=True) for link in category_links]
                category = ', '.join(categories)
                break
        
        # Extract author with multiple fallback selectors
        author = ''
        author_selectors = [
            'a[href*="/profile/"]',
            '.author-name',
            '.post-author',
            '[class*="author"] a',
            '.byline a',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                break
        
        # Extract date with multiple fallback selectors
        date = ''
        date_selectors = [
            '[itemprop="datePublished"]',
            'time[datetime]',
            '.post-date',
            '.date',
            '[class*="date"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date = date_elem.get('datetime') or date_elem.get_text(strip=True)
                break
        
        # Extract read time
        read_time = ''
        read_time_selectors = [
            '[class*="read-time"]',
            '[class*="reading-time"]',
            '.read-time',
            '.reading-time'
        ]
        
        for selector in read_time_selectors:
            read_time_elem = soup.select_one(selector)
            if read_time_elem:
                read_time = read_time_elem.get_text(strip=True)
                break
        
        # Try to extract read time from text content
        if not read_time:
            text_content = soup.get_text()
            read_time_match = re.search(r'(\d+)\s*min\s*read', text_content, re.I)
            if read_time_match:
                read_time = f"{read_time_match.group(1)} min read"
        
        # Extract clean title from the page
        clean_title = ''
        title_selectors = ['h1', 'h1.title', '.post-title', '.article-title', '[itemprop="headline"]', '.entry-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                clean_title = title_elem.get_text(strip=True)
                break
        
        # Remove unwanted elements before content extraction
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', '.sidebar', '.comments', '.social-share', '.related-posts']):
            element.decompose()
            
        # Look for main content with improved selectors
        content_selectors = [
            'article .entry-content',
            '.post-content', 
            '.entry-content',
            '.article-content',
            '.wp-block-post-content',  # WordPress Gutenberg blocks
            '.entry-content .wp-block-group',
            'article',
            'main .content',
            '[role="main"] .content',
            'main',
            '[role="main"]',
            '.content',
            'body'  # Last resort - get everything
        ]
        
        article_content = ''
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                if debug:
                    print(f"  Found content with selector: {selector}")
                    # Check for list elements
                    lists = content_elem.find_all(['ul', 'ol'])
                    print(f"  Found {len(lists)} list elements")
                    
                    # Check specifically for WordPress block lists
                    wp_lists = content_elem.find_all('ul', class_='wp-block-list')
                    print(f"  Found {len(wp_lists)} wp-block-list elements")
                    
                    # Show all list elements found
                    for i, ul in enumerate(lists[:5]):
                        items = ul.find_all('li')
                        classes = ul.get('class', [])
                        print(f"    List {i+1}: {len(items)} items, classes: {classes}")
                        for j, li in enumerate(items[:3]):
                            print(f"      Item {j+1}: {li.get_text(strip=True)[:50]}")
                    
                    # Show what paragraphs exist in content
                    all_paragraphs = content_elem.find_all('p')
                    print(f"  Found {len(all_paragraphs)} paragraph elements")
                    for i, p in enumerate(all_paragraphs[10:15]):  # Show middle paragraphs
                        p_text = p.get_text(strip=True)[:60]
                        print(f"    P{i+10}: {p_text}")
                        
                    # Check for any elements that might be bullet content
                    potential_bullets = content_elem.find_all(string=lambda text: text and any(skill in text.lower() for skill in ['deep user empathy', 'market analysis', 'competitive positioning', 'brand and marketing']))
                    print(f"  Found {len(potential_bullets)} elements containing expected bullet text")
                    for bullet_text in potential_bullets:
                        parent = bullet_text.parent if bullet_text.parent else None
                        parent_tag = parent.name if parent else 'unknown'
                        parent_class = parent.get('class', []) if parent else []
                        print(f"    Bullet text: '{bullet_text.strip()[:80]}' in <{parent_tag}> class={parent_class}")
                
                # Extract content preserving structure including lists
                article_content = self.extract_structured_content(content_elem, debug=debug)
                
                # If no lists found via HTML structure, try to detect text-based bullet points
                if debug and '•' not in article_content:
                    print(f"  No bullet points found in extracted content, checking for text-based bullets...")
                    all_text = content_elem.get_text()
                    lines_with_bullets = [line for line in all_text.split('\n') if line.strip().startswith(('•', '●', '◦', '-', '*'))]
                    print(f"    Found {len(lines_with_bullets)} lines starting with bullet characters")
                
                # If we got substantial content, break
                if len(article_content) > 500:
                    break
                    
        # If still no substantial content, try a broader approach
        if len(article_content) < 500:
            # Remove navigation and other non-content elements more aggressively
            for element in soup.select('nav, .nav, .navigation, .menu, .sidebar, .widget, .advertisement, .ads'):
                element.decompose()
            
            # Try to find the main text content
            body = soup.find('body')
            if body:
                # Get all paragraph-like content
                paragraphs = body.find_all(['p', 'div'], recursive=True)
                content_paragraphs = []
                
                for p in paragraphs:
                    # Use separator=' ' to preserve spaces between HTML elements
                    text = p.get_text(separator=' ', strip=True)
                    # Only include paragraphs with substantial text
                    if len(text) > 50 and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'subscribe', 'newsletter', 'follow us']):
                        content_paragraphs.append(text)
                
                if content_paragraphs:
                    article_content = '\n\n'.join(content_paragraphs[:20])  # Limit to first 20 substantial paragraphs
                
        return article_content, category, author, date, clean_title, read_time
    
    def scrape_full_article_selenium(self, url, debug=False):
        """Scrape full content using Selenium to handle JavaScript-rendered content"""
        print(f"Scraping with Selenium: {url}")
        
        driver = self.setup_selenium_driver(headless=not debug)
        if not driver:
            print("Falling back to regular scraping...")
            return self.scrape_full_article(url, debug)
        
        try:
            # Load the page
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for article content
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                if debug:
                    print("Timeout waiting for article content")
            
            # Additional wait for JavaScript content
            time.sleep(2)
            
            if debug:
                # Check for wp-block-list elements
                wp_lists = driver.find_elements(By.CSS_SELECTOR, "ul.wp-block-list")
                print(f"Selenium found {len(wp_lists)} wp-block-list elements")
                
                for i, ul in enumerate(wp_lists[:3]):
                    items = ul.find_elements(By.TAG_NAME, "li")
                    print(f"  List {i+1}: {len(items)} items")
                    for j, li in enumerate(items[:3]):
                        li_text = li.text.strip()[:60]
                        print(f"    Item {j+1}: {li_text}")
            
            # Extract title
            clean_title = ""
            try:
                title_elem = driver.find_element(By.TAG_NAME, "h1")
                clean_title = title_elem.text.strip()
            except:
                pass
            
            # Extract basic metadata (simplified for now)
            author = ""
            date = ""
            category = ""
            read_time = ""
            
            # Try to find author
            try:
                author_elem = driver.find_element(By.CSS_SELECTOR, 'a[href*="/profile/"]')
                author = author_elem.text.strip()
            except:
                pass
            
            # Find main content element
            content_element = None
            content_selectors = [
                "article",
                "main", 
                ".entry-content",
                ".post-content",
                ".wp-block-post-content"
            ]
            
            for selector in content_selectors:
                try:
                    content_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if debug:
                        print(f"Found content with selector: {selector}")
                    break
                except:
                    continue
            
            if not content_element:
                print("No content element found with Selenium")
                return '', '', '', '', '', ''
            
            # Extract structured content including wp-block-list elements
            article_content = self.extract_selenium_content(content_element, debug=debug)
            
            return article_content, category, author, date, clean_title, read_time
            
        except Exception as e:
            print(f"Error during Selenium scraping: {e}")
            return '', '', '', '', '', ''
        finally:
            driver.quit()
    
    def extract_selenium_content(self, element, debug=False):
        """Extract content from Selenium WebElement preserving wp-block-list elements"""
        content_parts = []
        
        # Get all child elements
        child_elements = element.find_elements(By.XPATH, ".//*")
        processed_elements = set()
        
        for elem in child_elements:
            try:
                tag_name = elem.tag_name.lower()
                elem_class = elem.get_attribute('class') or ''
                
                # Create unique key for this element
                elem_key = f"{tag_name}_{elem.location}_{elem_class}"
                if elem_key in processed_elements:
                    continue
                
                text = elem.text.strip()
                if not text or len(text) < 10:
                    continue
                
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    content_parts.append(f"\n{text}\n")
                    processed_elements.add(elem_key)
                    
                elif tag_name == 'ul':
                    # Check if this is a wp-block-list or any other list
                    if 'wp-block-list' in elem_class or len(elem_class) > 0:
                        if debug:
                            print(f"  Processing list with class: {elem_class}")
                        
                        # Get list items
                        li_elements = elem.find_elements(By.TAG_NAME, "li")
                        if li_elements:
                            content_parts.append("")  # Spacing before list
                            for li in li_elements:
                                li_text = li.text.strip()
                                if li_text and len(li_text) > 3:
                                    content_parts.append(f"• {li_text}")
                                    if debug:
                                        print(f"    List item: {li_text[:50]}")
                            content_parts.append("")  # Spacing after list
                        processed_elements.add(elem_key)
                    
                elif tag_name == 'p':
                    # Skip if this paragraph is inside a list we already processed
                    try:
                        parent_ul = elem.find_element(By.XPATH, "./ancestor::ul")
                        # Skip if parent ul was already processed
                        if parent_ul:
                            continue
                    except:
                        pass
                    
                    content_parts.append(text)
                    processed_elements.add(elem_key)
                        
            except Exception as e:
                if debug:
                    print(f"Error processing element: {e}")
                continue
        
        # Join and clean up content
        content = '\n\n'.join(content_parts)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content
    
    def extract_structured_content(self, content_elem, debug=False):
        """
        Extract content while preserving structure including lists, headings, and paragraphs
        """
        content_parts = []
        processed_elements = set()
        
        # Process elements in document order but avoid duplicates
        for element in content_elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'div'], recursive=True):
            # Skip if already processed
            if id(element) in processed_elements:
                continue
            
            element_text = element.get_text(separator=' ', strip=True)
            if not element_text or len(element_text) < 10:
                continue
                
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Headings
                content_parts.append(f"\n{element_text}\n")
                processed_elements.add(id(element))
                
            elif element.name in ['ul', 'ol']:
                # Process lists - ensure we don't have nested ul/ol within this one
                if not element.find_parent(['ul', 'ol']):
                    list_items = element.find_all('li', recursive=True)  # Get all nested li elements
                    if debug:
                        print(f"  Processing {element.name} with {len(list_items)} items")
                    if list_items:
                        content_parts.append("")  # Add spacing before list
                        for li in list_items:
                            li_text = li.get_text(separator=' ', strip=True)
                            if debug and li_text:
                                print(f"    List item: {li_text[:100]}")
                            if li_text and len(li_text) > 5:
                                # Add bullet point marker for audio-friendly format
                                content_parts.append(f"• {li_text}")
                                processed_elements.add(id(li))  # Mark li as processed
                        content_parts.append("")  # Add spacing after list
                    processed_elements.add(id(element))
                    
            elif element.name == 'p':
                # Regular paragraphs - but skip if already processed as part of a list
                if not element.find_parent(['ul', 'ol']):
                    # Check if paragraph contains bullet-like text patterns
                    if element_text.strip().startswith(('•', '●', '◦', '- ', '* ')):
                        # This is a text-based bullet point
                        content_parts.append(f"• {element_text.strip()}")
                        if debug:
                            print(f"    Found text-based bullet: {element_text[:50]}")
                    else:
                        content_parts.append(element_text)
                    processed_elements.add(id(element))
                    
            elif element.name == 'div':
                # Divs - only if they contain substantial unique content and not nested in lists
                if (not element.find_parent(['ul', 'ol', 'p']) and 
                    not element.find(['ul', 'ol', 'p']) and
                    not element.find_parent(['div'])):  # Avoid nested divs
                    # This is a standalone div with text content
                    content_parts.append(element_text)
                    processed_elements.add(id(element))
        
        # Join parts and clean up
        content = '\n\n'.join(content_parts)
        
        # Clean up excessive whitespace but preserve paragraph breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Max 2 consecutive newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single space
        content = content.strip()
        
        # Detect CSS-generated bullet points by pattern analysis
        content = self.detect_css_bullet_patterns(content, debug=debug)
        
        return content
    
    def detect_css_bullet_patterns(self, content, debug=False):
        """
        Detect CSS-generated bullet points by analyzing text patterns
        Looks for sequences of short paragraphs after trigger phrases like "require:" or "need:"
        """
        lines = content.split('\n\n')
        processed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for trigger phrases that typically precede bullet lists
            trigger_phrases = [
                'require:', 'need:', 'requires:', 'needs:', 'include:', 'includes:', 
                'involve:', 'involves:', 'focus on:', 'emphasize:', 'centered around:',
                'blends:', 'focused on:', 'typically require:', 'you\'ll need:',
                'requiring:', 'emphasize:', 'focus intensely on:'
            ]
            
            if any(line.lower().endswith(phrase) for phrase in trigger_phrases):
                if debug:
                    print(f"  Found trigger phrase in: {line[:60]}")
                
                processed_lines.append(line)
                i += 1
                
                # Look ahead for potential bullet items (short paragraphs)
                bullet_candidates = []
                j = i
                
                while j < len(lines) and j < i + 8:  # Look at next 8 paragraphs max
                    next_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop if we hit "Examples:" or similar section headers
                    if (next_line.lower().startswith(('examples:', 'example:', 'note:', 'important:')) or 
                        len(next_line) > 150):  # Too long to be a bullet point
                        break
                    
                    # Short paragraphs (< 100 chars) are likely bullet items
                    if len(next_line) < 100 and not next_line.endswith('.'):
                        bullet_candidates.append(next_line)
                        j += 1
                    else:
                        break
                
                # If we found 2+ short paragraphs, treat them as bullets
                if len(bullet_candidates) >= 2:
                    if debug:
                        print(f"    Converting {len(bullet_candidates)} items to bullets")
                        for bullet in bullet_candidates[:3]:
                            print(f"      • {bullet[:50]}")
                    
                    processed_lines.append("")  # Spacing before list
                    for bullet in bullet_candidates:
                        processed_lines.append(f"• {bullet}")
                    processed_lines.append("")  # Spacing after list
                    
                    i = j  # Skip the processed bullet candidates
                else:
                    # Not enough candidates, process normally
                    continue
            else:
                processed_lines.append(line)
                i += 1
        
        return '\n\n'.join(processed_lines)
        
    def scrape_all(self, include_full_content=True, max_articles=None, use_selenium=False):
        """Main scraping method"""
        print("Starting Mind the Product scraper...")
        
        # Get article list
        articles = self.extract_article_list()
        print(f"Found {len(articles)} articles")
        
        if max_articles:
            articles = articles[:max_articles]
            
        # Scrape full content if requested
        if include_full_content:
            if use_selenium:
                print("Scraping full article content with Selenium (slower but more complete)...")
            else:
                print("Scraping full article content with hybrid approach...")
                
            articles_to_keep = []
            selenium_retry_count = 0
            
            for i, article in enumerate(articles, 1):
                print(f"Processing article {i}/{len(articles)}: {article.get('title', 'No title')}")
                
                # Step 1: Try regular scraping first
                full_content, category, author, date, clean_title, read_time = self.scrape_full_article(article['url'])
                
                if full_content == 'SKIPPED_VIDEO':
                    print(f"  Article skipped due to embedded video")
                    continue  # Skip this article entirely
                
                # Step 2: Check if we got bullet points (for hybrid approach)
                needs_selenium_retry = False
                if not use_selenium and full_content:
                    bullet_count = full_content.count('•')
                    # Check for trigger phrases that should have bullet points
                    trigger_phrases = ['typically require:', 'you\'ll need:', 'emphasize:', 'requiring:', 'centered around:', 'blends:']
                    has_triggers = any(phrase in full_content.lower() for phrase in trigger_phrases)
                    
                    if has_triggers and bullet_count < 3:
                        print(f"  Regular scraping found {bullet_count} bullets but content suggests more. Retrying with Selenium...")
                        needs_selenium_retry = True
                
                # Step 3: Retry with Selenium if needed
                if (use_selenium or needs_selenium_retry) and SELENIUM_AVAILABLE:
                    try:
                        if not use_selenium:  # Only show this message for hybrid retries
                            selenium_retry_count += 1
                        
                        selenium_content, selenium_category, selenium_author, selenium_date, selenium_title, selenium_read_time = self.scrape_full_article_selenium(article['url'])
                        
                        # Use Selenium results if they're better
                        if selenium_content and len(selenium_content) > len(full_content):
                            selenium_bullets = selenium_content.count('•')
                            regular_bullets = full_content.count('•')
                            
                            if selenium_bullets > regular_bullets:
                                print(f"  Selenium found {selenium_bullets} bullets vs {regular_bullets} from regular scraping. Using Selenium results.")
                                full_content = selenium_content
                                if selenium_category: category = selenium_category
                                if selenium_author: author = selenium_author
                                if selenium_date: date = selenium_date
                                if selenium_title: clean_title = selenium_title
                                if selenium_read_time: read_time = selenium_read_time
                            else:
                                print(f"  Selenium didn't improve results. Using regular scraping.")
                        
                    except Exception as e:
                        print(f"  Selenium retry failed: {e}. Using regular scraping results.")
                
                # Update article with scraped content
                article['full_content'] = full_content
                if category and not article.get('category'):
                    article['category'] = category
                if author and not article.get('author'):
                    article['author'] = author
                if date and not article.get('date'):
                    article['date'] = date
                if clean_title:
                    article['title'] = clean_title  # Replace messy title with clean one
                if read_time and not article.get('read_time'):
                    article['read_time'] = read_time
                
                # Generate LLM summary if content is available and no existing summary
                if full_content and not article.get('summary'):
                    print(f"  Generating LLM summary...")
                    llm_summary = self.generate_llm_summary(full_content, article['title'])
                    if llm_summary:
                        article['summary'] = llm_summary
                
                articles_to_keep.append(article)
                time.sleep(1)  # Be respectful
            
            articles = articles_to_keep
            
            if not use_selenium and selenium_retry_count > 0:
                print(f"\nHybrid approach completed: {selenium_retry_count} articles were improved with Selenium")
                
        self.articles = articles
        return articles
        
    def transform_to_audio_format(self, articles):
        """Transform articles to match the expected audio format"""
        transformed_articles = []
        
        for i, article in enumerate(articles, 1):
            # Map category to sub_category array
            sub_categories = []
            category_lower = article.get('category', '').lower()
            
            # Add relevant sub-categories based on content and category
            if 'communication' in category_lower:
                sub_categories = ['product_management', 'communication']
            elif 'community' in category_lower:
                sub_categories = ['events', 'community']
            elif 'guest post' in category_lower:
                if 'career' in article.get('title', '').lower() or 'skill' in article.get('title', '').lower():
                    sub_categories = ['career_development', 'product_skills']
                elif 'strategy' in article.get('title', '').lower():
                    sub_categories = ['product_strategy', 'hospitality_tech'] if 'hospitality' in article.get('title', '').lower() else ['product_strategy']
                elif 'naming' in article.get('title', '').lower() or 'brand' in article.get('title', '').lower():
                    sub_categories = ['product_naming', 'branding']
                elif 'internal' in article.get('title', '').lower() or 'tool' in article.get('title', '').lower():
                    sub_categories = ['internal_tools', 'product_infrastructure']
                else:
                    sub_categories = ['guest_content']
            elif 'product management' in category_lower:
                if 'curated' in article.get('title', '').lower() or 'read' in article.get('title', '').lower():
                    sub_categories = ['curated_content', 'industry_insights']
                elif 'news' in article.get('title', '').lower() or 'roundup' in article.get('title', '').lower():
                    sub_categories = ['industry_news', 'weekly_roundup']
                elif 'learning' in article.get('title', '').lower() or 'framework' in article.get('title', '').lower():
                    sub_categories = ['learning', 'frameworks']
                elif 'team' in article.get('title', '').lower() or 'behavioral' in article.get('title', '').lower():
                    sub_categories = ['team_building', 'behavioral_science']
                else:
                    sub_categories = ['product_management']
            elif 'product discovery' in category_lower:
                sub_categories = ['early_stage', 'customer_validation']
            elif 'a/b testing' in category_lower:
                sub_categories = ['experimentation', 'testing_strategy']
            elif 'artificial intelligence' in category_lower or 'ai' in category_lower:
                sub_categories = ['ai_news', 'industry_updates']
            elif 'data' in category_lower:
                sub_categories = ['data_analysis', 'product_insights']
            else:
                sub_categories = ['general']
            
            # Parse date to YYYY-MM-DD format
            release_date = self.parse_release_date(article.get('date', ''))
            
            # Generate filename-friendly title
            title_slug = self.generate_filename_slug(article.get('title', ''))
            creator_slug = self.generate_filename_slug(article.get('author', 'unknown'))
            category_slug = self.generate_filename_slug(article.get('category', 'general'))
            
            # Note: voices array will be added after TTS generation with real data
            
            transformed_article = {
                "track_id": i,
                "title": article.get('title', ''),
                "url": article.get('url', ''),
                "creator": article.get('author', ''),
                "category": article.get('category', ''),
                "sub_category": sub_categories,
                "summary": article.get('summary', ''),
                "releaseDate": release_date,
                "full_content": article.get('full_content', ''),
                "read_time": article.get('read_time', ''),
                "voices": []  # Will be populated by TTS-extraction.py after audio generation
            }
            
            transformed_articles.append(transformed_article)
        
        return transformed_articles
    
    def parse_release_date(self, date_string):
        """Parse date to YYYY-MM-DD format"""
        if not date_string:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Try to parse various date formats
        patterns = [
            '%Y-%m-%d',
            '%m/%d/%Y', 
            '%B %d, %Y',
            '%d %B %Y',
            '%b %d, %Y',
            '%d %b %Y'
        ]
        
        for pattern in patterns:
            try:
                parsed_date = datetime.strptime(date_string.strip(), pattern)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no pattern matches, return current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def generate_filename_slug(self, text):
        """Generate a filename-friendly slug from text"""
        if not text:
            return 'unknown'
        
        # Handle special characters and clean the text
        slug = text.lower()
        # Replace problematic characters
        slug = re.sub(r'[&\(\)\[\]{}]', '', slug)
        slug = re.sub(r'[^\w\s-]', '_', slug)
        slug = re.sub(r'\s+', '_', slug)
        slug = re.sub(r'_{2,}', '_', slug)
        slug = slug.strip('_')
        
        # Handle specific category mappings
        category_mappings = {
            'artificial_intelligence_ai_machine_learning_ml': 'ai_ml',
            'product_management': 'product_mgmt',
            'communication': 'comm',
            'community': 'community',
            'guest_post': 'guest',
            'product_discovery': 'discovery',
            'a_b_testing': 'ab_testing',
            'data': 'data'
        }
        
        for long_name, short_name in category_mappings.items():
            if slug.startswith(long_name):
                slug = short_name
                break
        
        # Limit length for filename compatibility
        return slug[:30] if slug else 'unknown'

    def export_to_json(self, filename='../audeon_tools/Content/articles/raw_metadata/mindtheproduct_articles_with_summaries.json'):
        """Export articles to JSON in the expected audio format"""
        transformed_articles = self.transform_to_audio_format(self.articles)
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transformed_articles, f, indent=2, ensure_ascii=False)
        print(f"Articles exported to {filename}")
        

    def generate_audio_files(self, content_dir='../Content/articles/ssml_format', output_dir='../Content/audio', 
                           voice=None, lang='en-US', rate=1.0, pitch=0.0, volume=0.0):
        """
        Generate TTS audio files for all articles using proper naming convention
        Note: This method is kept for backward compatibility but TTS generation 
        should now be done using TTS-extraction.py directly for better control.
        """
        print("Note: For better control, consider using TTS-extraction.py directly:")
        print("python TTS-extraction.py -f content.ssml -o audio.mp3 --voice emma --update-json metadata.json --track-id 1")
        
        if not self.articles:
            print("No articles available. Run scrape_all() first.")
            return False
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Transform articles to get proper filenames
        transformed_articles = self.transform_to_audio_format(self.articles)
        
        processed_count = 0
        
        for article in transformed_articles:
            try:
                track_id = article.get('track_id', 0)
                title = article.get('title', 'Untitled')
                release_date = article.get('releaseDate', '')
                creator = article.get('creator', '')
                
                # Generate filename base consistent with content_extractor.py
                if release_date and creator:
                    filename_base = f"{release_date}_{self.sanitize_content_filename(creator)}_{self.sanitize_content_filename(title)}"
                elif release_date:
                    filename_base = f"{release_date}_{self.sanitize_content_filename(title)}"
                elif creator:
                    filename_base = f"{self.sanitize_content_filename(creator)}_{self.sanitize_content_filename(title)}"
                else:
                    filename_base = self.sanitize_content_filename(title)
                
                # Find content file
                content_filename = f"{filename_base}.ssml"
                content_path = os.path.join(content_dir, content_filename)
                
                if not os.path.exists(content_path):
                    print(f"Warning: Content file not found: {content_path}")
                    continue
                
                # Create audio filename - simple naming without voice suffix
                audio_filename = f"{filename_base}.mp3"
                output_path = os.path.join(output_dir, audio_filename)
                
                # Use specified voice if provided, otherwise use default
                tts_voice = voice if voice else 'en-US-Wavenet-F'  # Default voice
                
                print(f"Processing Track {track_id}: {title}")
                
                # Build TTS command
                cmd = [
                    'python', 'TTS-extraction.py',
                    '-f', content_path,
                    '-o', output_path,
                    '--lang', lang,
                    '--voice', tts_voice
                ]
                
                # Add optional parameters
                if rate != 1.0:
                    cmd.extend(['--rate', str(rate)])
                if pitch != 0.0:
                    cmd.extend(['--pitch', str(pitch)])
                if volume != 0.0:
                    cmd.extend(['--volume', str(volume)])
                
                try:
                    # Run TTS command
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"  ✓ Generated: {audio_filename}")
                        processed_count += 1
                    else:
                        print(f"  ✗ Error generating {audio_filename}:")
                        print(f"    {result.stderr}")
                
                except subprocess.TimeoutExpired:
                    print(f"  ✗ Timeout processing {audio_filename}")
                except Exception as e:
                    print(f"  ✗ Error processing {audio_filename}: {e}")
                
            except Exception as e:
                print(f"Error processing article {article.get('track_id', 'unknown')}: {e}")
                continue
        
        print(f"\nTTS Generation completed: {processed_count} audio files generated in '{output_dir}'")
        return True
    
    def sanitize_content_filename(self, filename):
        """
        Sanitize filename to match content_extractor output
        """
        if not filename:
            return 'unknown'
        
        # Replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'[^\w\s\-_\.]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)  # Multiple underscores
        sanitized = sanitized.strip('_. ')  # Remove leading/trailing chars
        
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        
        return sanitized

    def extract_content_files(self, json_file='../audeon_tools/Content/articles/raw_metadata/mindtheproduct_articles_with_summaries.json', output_dir='../audeon_tools/Content/articles/ssml_format'):
        """
        Extract and clean content by calling the external content_extractor.py script
        """
        if not os.path.exists(json_file):
            print(f"Error: JSON file '{json_file}' not found.")
            return False
        
        print(f"Running content extraction on {json_file}...")
        
        # Build command to run content_extractor.py
        cmd = [
            'python', 'content_extractor.py',
            json_file,
            '--output-dir', output_dir
        ]
        
        try:
            # Run content extractor
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("Content extraction completed successfully!")
                print(result.stdout)
                return True
            else:
                print("Content extraction failed:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("Content extraction timed out")
            return False
        except Exception as e:
            print(f"Error running content extraction: {e}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Mind the Product scraper with content extraction and TTS generation')
    parser.add_argument('--scrape', action='store_true', help='Scrape articles from website')
    parser.add_argument('--test-url', type=str, help='Test scraping a single article URL')
    parser.add_argument('--use-selenium', action='store_true', help='Use Selenium for JavaScript-rendered content')
    parser.add_argument('--extract-content', action='store_true', help='Extract and clean content to text files')
    parser.add_argument('--generate-tts', action='store_true', help='Generate TTS audio files')
    parser.add_argument('--max-articles', type=int, default=50, help='Maximum articles to scrape')
    parser.add_argument('--voice', help='Override voice for TTS generation')
    parser.add_argument('--lang', default='en-US', help='Language code for TTS')
    parser.add_argument('--rate', type=float, default=1.0, help='Speaking rate')
    parser.add_argument('--pitch', type=float, default=0.0, help='Pitch adjustment')
    parser.add_argument('--volume', type=float, default=0.0, help='Volume gain')
    parser.add_argument('--output-dir', type=str, default='../Content/articles/raw_metadata', 
                       help='Output directory for JSON file (used with --test-url)')
    
    args = parser.parse_args()
    
    # If no specific action, default to scraping
    if not args.scrape and not args.extract_content and not args.generate_tts and not args.test_url:
        args.scrape = True
    
    # Configuration
    include_full_content = True
    use_llm_summarization = True  # Enable LLM summarization by default
    
    # Initialize scraper with Ollama support
    scraper = MindTheProductScraper(use_llm_summarization=use_llm_summarization)
    
    try:
        if args.test_url:
            # Test single article
            print(f"Testing scraper on single article: {args.test_url}")
            
            if args.use_selenium:
                print("Using Selenium for JavaScript-rendered content...")
                content, category, author, date, title, read_time = scraper.scrape_full_article_selenium(args.test_url, debug=True)
            else:
                content, category, author, date, title, read_time = scraper.scrape_full_article(args.test_url, debug=True)
            
            if content == 'SKIPPED_VIDEO':
                print("Article was skipped due to embedded video")
                return
            
            print(f"\n✓ Successfully scraped article:")
            print(f"  Title: {title}")
            print(f"  Author: {author}")
            print(f"  Date: {date}")
            print(f"  Category: {category}")
            print(f"  Read time: {read_time}")
            print(f"  Content length: {len(content)} characters")
            
            # Check for bullet points
            lines = content.split('\n')
            bullet_lines = [line for line in lines if line.strip().startswith('•')]
            print(f"  Bullet points found: {len(bullet_lines)}")
            
            if bullet_lines:
                print("\n📋 First few bullet points:")
                for i, bullet in enumerate(bullet_lines[:5]):
                    print(f"    {i+1}. {bullet.strip()}")
                if len(bullet_lines) > 5:
                    print(f"    ... and {len(bullet_lines) - 5} more")
            
            # Create test article data
            test_article = {
                'track_id': 1,
                'title': title,
                'url': args.test_url,
                'creator': author,
                'category': category,
                'sub_category': ['test'],
                'summary': 'Test article scraped individually',
                'releaseDate': date or '2025-01-01',
                'full_content': content,
                'read_time': read_time,
                'voices': []
            }
            
            # Save to JSON file
            import os
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, 'test_single_article.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([test_article], f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test article saved to: {output_file}")
            print(f"\nYou can now run content extraction on this file:")
            print(f"python content_extractor.py '{output_file}' --output-dir ../Content/articles/ssml_format/test")
            
            return
            
        elif args.scrape:
            articles = scraper.scrape_all(include_full_content=include_full_content, max_articles=args.max_articles, use_selenium=args.use_selenium)
            
            if articles:
                # Export to JSON format
                scraper.export_to_json()
                print(f"\nScraping completed! Found {len(articles)} articles.")
                
                # Show summary statistics
                articles_with_summaries = len([a for a in articles if a.get('summary')])
                print(f"Articles with LLM-generated summaries: {articles_with_summaries}/{len(articles)}")
                print(f"\nNext steps:")
                print(f"  1. Extract content: python content_extractor.py ../Content/articles/raw_metadata/mindtheproduct_articles_with_summaries.json")
                print(f"  2. Generate TTS: python TTS-extraction.py -f content.ssml -o audio.mp3 --voice emma")
            else:
                print("No articles found. The website structure may have changed.")
        
        if args.extract_content:
            # Extract content to text files using external script
            print("\nExtracting content to text files...")
            if not scraper.extract_content_files():
                print("Content extraction failed!")
                return
        
        if args.generate_tts:
            # Check if we have articles loaded
            if not hasattr(scraper, 'articles') or not scraper.articles:
                # Try to load from existing JSON
                try:
                    with open('../Content/articles/raw_metadata/mindtheproduct_articles_with_summaries.json', 'r') as f:
                        articles_data = json.load(f)
                    # Convert back to scraper format
                    scraper.articles = []
                    for article in articles_data:
                        scraper.articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'author': article.get('creator', ''),
                            'category': article.get('category', ''),
                            'summary': article.get('summary', ''),
                            'date': article.get('releaseDate', ''),
                            'full_content': article.get('full_content', ''),
                            'read_time': article.get('read_time', '')
                        })
                    print("Loaded articles from existing JSON file.")
                except FileNotFoundError:
                    print("No existing articles found. Please run scraping first.")
                    return
            
            # Check if content files exist
            content_dir = '../Content/articles/ssml_format'
            if not os.path.exists(content_dir) or not os.listdir(content_dir):
                print(f"Error: No content files found in '{content_dir}' directory.")
                print("Please run content extraction first using --extract-content")
                return
            
            # Generate TTS audio files
            print("\nGenerating TTS audio files...")
            scraper.generate_audio_files(
                voice=args.voice,
                lang=args.lang,
                rate=args.rate,
                pitch=args.pitch,
                volume=args.volume
            )
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()