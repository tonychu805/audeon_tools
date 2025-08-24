#!/usr/bin/env python3
"""
Update missing content for articles 6-14 in mindtheproduct_articles_with_summaries.json
"""

from mindtheproduct_scraper import MindTheProductScraper
import json
import time

def update_missing_content():
    """Update articles with missing full_content"""
    
    # Load existing articles
    with open('mindtheproduct_articles_with_summaries.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Initialize scraper without LLM to speed up
    scraper = MindTheProductScraper(use_llm_summarization=False)
    
    # Track which articles need updating (those with placeholder content)
    articles_to_update = []
    for article in articles:
        if "Content for track" in article.get('full_content', '') or len(article.get('full_content', '')) < 100:
            articles_to_update.append(article)
    
    print(f"Found {len(articles_to_update)} articles needing content updates")
    
    # Update each article
    updated_count = 0
    for i, article in enumerate(articles_to_update, 1):
        print(f"\nUpdating article {i}/{len(articles_to_update)}: {article['title']}")
        print(f"URL: {article['url']}")
        
        try:
            full_content, category, author, date, clean_title, read_time = scraper.scrape_full_article(article['url'])
            
            if full_content and full_content != 'SKIPPED_VIDEO' and len(full_content) > 100:
                # Update the article in the main list
                for main_article in articles:
                    if main_article['track_id'] == article['track_id']:
                        main_article['full_content'] = full_content
                        if read_time and not main_article.get('read_time'):
                            main_article['read_time'] = read_time
                        if category and not main_article.get('category'):
                            main_article['category'] = category
                        if author and not main_article.get('creator'):
                            main_article['creator'] = author
                        updated_count += 1
                        print(f"  ✓ Updated content ({len(full_content)} chars)")
                        break
            else:
                print(f"  ✗ Failed to extract content or content too short")
                
        except Exception as e:
            print(f"  ✗ Error updating article: {e}")
        
        # Small delay to be respectful
        time.sleep(1)
    
    # Save updated articles
    if updated_count > 0:
        with open('mindtheproduct_articles_with_summaries.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Successfully updated {updated_count} articles")
        print("Updated file saved as mindtheproduct_articles_with_summaries.json")
    else:
        print("\n✗ No articles were updated")

if __name__ == "__main__":
    update_missing_content()