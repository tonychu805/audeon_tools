#!/usr/bin/env python3
"""
Check HTTP status codes for all remaining article URLs using curl
"""
import subprocess
import json
from typing import List, Dict

def get_remaining_urls():
    """Get all URLs that still need content"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    remaining = []
    for article in articles:
        if not article.get('full_content') or not article['full_content'].strip():
            remaining.append({
                'track_id': article['track_id'],
                'title': article['title'],
                'url': article['url']
            })
    
    return remaining

def check_url_with_curl(url: str) -> Dict:
    """Check HTTP status code using curl"""
    try:
        # Use curl to get just the headers and status code
        result = subprocess.run([
            'curl', '-I', '-s', '-o', '/dev/null', '-w', '%{http_code}', url
        ], capture_output=True, text=True, timeout=10)
        
        status_code = int(result.stdout.strip())
        
        return {
            'status_code': status_code,
            'accessible': status_code == 200
        }
    except Exception as e:
        return {
            'status_code': 'ERROR',
            'accessible': False,
            'error': str(e)
        }

def main():
    """Check status of all remaining URLs"""
    remaining = get_remaining_urls()
    
    print(f"Checking {len(remaining)} URLs for accessibility...\n")
    
    accessible = []
    not_found = []
    forbidden = []
    errors = []
    
    for i, item in enumerate(remaining, 1):
        print(f"Checking {i}/{len(remaining)}: Track {item['track_id']}")
        status = check_url_with_curl(item['url'])
        item.update(status)
        
        if status['status_code'] == 200:
            accessible.append(item)
            print(f"  ✅ 200 OK")
        elif status['status_code'] == 404:
            not_found.append(item)
            print(f"  🚫 404 Not Found")
        elif status['status_code'] == 403:
            forbidden.append(item)
            print(f"  🔒 403 Forbidden")
        else:
            errors.append(item)
            print(f"  ❌ {status['status_code']}")
    
    print(f"\n📊 STATUS SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Accessible (200): {len(accessible)}")
    print(f"🚫 Not Found (404): {len(not_found)}")
    print(f"🔒 Forbidden (403): {len(forbidden)}")
    print(f"❌ Other Errors: {len(errors)}")
    
    if not_found:
        print(f"\n🚫 NOT FOUND (404) - {len(not_found)} URLs:")
        print("="*60)
        for item in not_found:
            print(f"Track {item['track_id']}: {item['title']}")
            print(f"   URL: {item['url']}")
            print()
    
    if forbidden:
        print(f"\n🔒 FORBIDDEN (403) - {len(forbidden)} URLs:")
        print("="*60)
        for item in forbidden:
            print(f"Track {item['track_id']}: {item['title']}")
            print(f"   URL: {item['url']}")
            print()
    
    if accessible:
        print(f"\n✅ ACCESSIBLE (200) - {len(accessible)} URLs:")
        print("="*60)
        for item in accessible:
            print(f"Track {item['track_id']}: {item['title']}")
            print(f"   URL: {item['url']}")
            print()

if __name__ == "__main__":
    main()