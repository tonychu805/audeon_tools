#!/usr/bin/env python3
"""
Process articles using available MCP tools for Firecrawl
"""
import json
import sys
import importlib

def load_articles():
    """Load the articles file"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    return articles, file_path

def get_missing_content_urls():
    """Get URLs that need content"""
    articles, _ = load_articles()
    urls_needed = []
    
    for i, article in enumerate(articles):
        if not article.get('full_content') or not article['full_content'].strip():
            urls_needed.append({
                'index': i,
                'track_id': article['track_id'], 
                'title': article['title'],
                'url': article['url']
            })
    
    return urls_needed

if __name__ == "__main__":
    urls = get_missing_content_urls()
    print(f"Found {len(urls)} URLs that need content:")
    
    # Print first 5 for processing
    for i, item in enumerate(urls[:5]):
        print(f"\n{i+1}. Track {item['track_id']}: {item['title']}")
        print(f"   URL: {item['url']}")