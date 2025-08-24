#!/usr/bin/env python3
"""
Parallel Content Extractor - Enhanced version with concurrent processing
"""
import json
import os
import argparse
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

# Import original content_extractor functions
from content_extractor import (
    create_ssml_markup, clean_for_audio_synthesis, 
    sanitize_filename, TTS_PROVIDERS
)

# Thread-safe counter
class ProgressCounter:
    def __init__(self, total):
        self.total = total
        self.processed = 0
        self.failed = 0
        self.lock = Lock()
    
    def increment_processed(self):
        with self.lock:
            self.processed += 1
            print(f"Progress: {self.processed}/{self.total} processed, {self.failed} failed")
    
    def increment_failed(self):
        with self.lock:
            self.failed += 1
            print(f"Progress: {self.processed}/{self.total} processed, {self.failed} failed")

def process_single_article(article, output_dir, provider, progress_counter):
    """Process a single article - thread-safe version"""
    try:
        # Extract required fields
        track_id = article.get('track_id', 0)
        title = article.get('title', 'Untitled')
        full_content = article.get('full_content', '')
        
        if not full_content:
            print(f"⚠️  Warning: No full_content found for article ID {track_id}")
            progress_counter.increment_failed()
            return False
        
        # Clean content for audio synthesis
        cleaned_content = clean_for_audio_synthesis(full_content)
        
        if not cleaned_content:
            print(f"⚠️  Warning: Content is empty after cleaning for article ID {track_id}")
            progress_counter.increment_failed()
            return False
        
        # Get provider configuration
        provider_config = TTS_PROVIDERS.get(provider, TTS_PROVIDERS['google'])
        
        # Apply provider-specific formatting
        final_content = create_ssml_markup(cleaned_content, title, provider)
        file_extension = provider_config['extension']
        
        # Create filename based on date and title
        release_date = article.get('releaseDate', '')
        creator = article.get('creator', '')
        
        if release_date and creator:
            filename_base = f"{release_date}_{sanitize_filename(creator)}_{sanitize_filename(title)}"
        elif release_date:
            filename_base = f"{release_date}_{sanitize_filename(title)}"
        elif creator:
            filename_base = f"{sanitize_filename(creator)}_{sanitize_filename(title)}"
        else:
            filename_base = sanitize_filename(title)
        
        filename = f"{filename_base}{file_extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Check content length limits for the provider
        max_length = provider_config.get('max_input_length', 5000)
        if len(final_content) > max_length:
            print(f"⚠️  Warning: Content for '{title}' ({len(final_content)} chars) exceeds {provider} limit ({max_length} chars)")
            
        # Save content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        progress_counter.increment_processed()
        return True
        
    except Exception as e:
        print(f"❌ Error processing article {article.get('track_id', 'unknown')}: {e}")
        progress_counter.increment_failed()
        return False

def parallel_extract_and_process_content(json_file, output_dir, provider="google", max_workers=5):
    """
    Extract content from JSON and save as individual text files using parallel processing
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{json_file}': {e}")
        return False
    
    if not isinstance(data, list):
        print("Error: JSON file should contain a list of articles.")
        return False
    
    print(f"🚀 Starting parallel processing of {len(data)} articles using {max_workers} workers...")
    start_time = time.time()
    
    progress_counter = ProgressCounter(len(data))
    
    # Process articles in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = {
            executor.submit(process_single_article, article, output_dir, provider, progress_counter): article
            for article in data
        }
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total articles: {len(data)}")
    print(f"   Successfully processed: {progress_counter.processed}")
    print(f"   Failed: {progress_counter.failed}")
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Average per article: {processing_time/len(data):.2f} seconds")
    print(f"   Output directory: '{output_dir}'")
    
    return progress_counter.failed == 0

def main():
    parser = argparse.ArgumentParser(
        description='Parallel Content Extractor - Enhanced version with concurrent processing'
    )
    
    parser.add_argument('json_file', help='Path to JSON file containing articles')
    parser.add_argument('-p', '--provider', choices=['google', 'elevenlabs', 'minimax'], 
                       default='google', help='TTS provider (default: google)')
    parser.add_argument('-o', '--output-dir', 
                       help='Output directory for files (default: provider-specific directory)')
    parser.add_argument('-w', '--workers', type=int, default=5,
                       help='Number of parallel workers (default: 5)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_file):
        print(f"Error: File '{args.json_file}' does not exist.")
        sys.exit(1)
    
    # Set default output directory based on provider
    if not args.output_dir:
        provider_dirs = {
            'google': '../Content/articles/google_tts',
            'elevenlabs': '../Content/articles/elevenlabs',
            'minimax': '../Content/articles/minimax'
        }
        args.output_dir = provider_dirs.get(args.provider, '../Content/articles/output')
    
    # Print provider info
    provider_config = TTS_PROVIDERS[args.provider]
    print(f"🎯 Using TTS Provider: {provider_config['name']}")
    print(f"📝 Output Format: {provider_config['format']}")
    print(f"📄 File Extension: {provider_config['extension']}")
    print(f"👥 Workers: {args.workers}")
    if provider_config.get('note'):
        print(f"📌 Note: {provider_config['note']}")
    print()
    
    success = parallel_extract_and_process_content(
        args.json_file, 
        args.output_dir, 
        args.provider,
        args.workers
    )
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()