#!/usr/bin/env python3
"""
Script to populate full_content field using Firecrawl API
"""
import json
import time
from typing import Dict, List, Any, Optional

def load_articles(file_path: str) -> List[Dict[str, Any]]:
    """Load articles from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_articles(file_path: str, articles: List[Dict[str, Any]]) -> None:
    """Save articles to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

def needs_content(article: Dict[str, Any]) -> bool:
    """Check if article needs full_content populated"""
    return not article.get('full_content') or not article['full_content'].strip()

def process_articles_with_firecrawl():
    """Process articles and show which ones need scraping"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    
    # Load articles
    articles = load_articles(file_path)
    
    # Find articles needing content
    articles_needing_content = [article for article in articles if needs_content(article)]
    
    print(f"Found {len(articles_needing_content)} articles needing full_content")
    print("\nArticles that need content:")
    
    for i, article in enumerate(articles_needing_content[:10], 1):
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print()
    
    if len(articles_needing_content) > 10:
        print(f"... and {len(articles_needing_content) - 10} more articles")
    
    return articles_needing_content

def update_article_content(articles: List[Dict[str, Any]], track_id: int, content: str) -> bool:
    """Update specific article with scraped content"""
    for article in articles:
        if article['track_id'] == track_id:
            article['full_content'] = content
            
            # Update read time based on content length
            words = len(content.split())
            minutes = max(1, round(words / 200))  # 200 words per minute
            article['read_time'] = f"{minutes} min read"
            
            return True
    return False

if __name__ == "__main__":
    articles_needing_content = process_articles_with_firecrawl()
    print(f"\n🚀 Ready to scrape {len(articles_needing_content)} articles with Firecrawl!")