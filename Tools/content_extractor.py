#!/usr/bin/env python3
"""
Multi-Provider Content Extractor for Audio Synthesis
Extracts full content from JSON, cleans it for TTS, and saves as separate text files.
Supports Google Cloud TTS, ElevenLabs, and MiniMax with provider-specific formatting.
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# TTS Provider configurations
TTS_PROVIDERS = {
    'google': {
        'name': 'Google Cloud Text-to-Speech',
        'format': 'ssml',
        'extension': '.ssml',
        'supports_tags': ['speak', 'break', 'emphasis', 'p', 's', 'prosody', 'phoneme', 'say-as'],
        'max_input_length': 5000,
        'break_format': '<break time="{}"/>',
        'emphasis_format': '<emphasis level="{}">{}</emphasis>'
    },
    'elevenlabs': {
        'name': 'ElevenLabs',
        'format': 'ssml_limited',
        'extension': '.ssml',
        'supports_tags': ['speak', 'break', 'emphasis', 'prosody', 'phoneme'],
        'max_input_length': 5000,
        'break_format': '<break time="{}"/>',
        'emphasis_format': '<emphasis>{}</emphasis>',
        'note': 'Phoneme tags only work with Eleven Flash v2, Eleven Turbo v2, and Eleven English v1 models'
    },
    'minimax': {
        'name': 'MiniMax TTS',
        'format': 'text_with_pauses',
        'extension': '.txt',
        'supports_tags': [],
        'max_input_length': 8000,
        'break_format': '<#{}#>',
        'emphasis_format': '{}',
        'note': 'Uses proprietary pause format <#x#> where x is seconds (0.01-99.99)'
    }
}

def create_ssml_markup(text, title="", provider="google"):
    """
    Convert text to provider-specific format
    """
    if not text:
        return ""
    
    if provider == 'minimax':
        return create_minimax_format(text, title)
    elif provider == 'elevenlabs':
        return create_elevenlabs_ssml(text, title)
    else:  # Google Cloud TTS (default)
        return create_google_ssml(text, title)

def create_google_ssml(text, title=""):
    """
    Create Google Cloud TTS compatible SSML
    """
    if not text:
        return ""
    
    ssml = '<speak>\n'
    
    # Add title with emphasis if provided
    lines = text.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    if title and title.strip() != first_line:
        ssml += f'  <emphasis level="strong">{escape_ssml_text(title)}</emphasis>\n'
        ssml += '  <break time="1s"/>\n'
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Skip if this paragraph is the same as the title we already added
        if title and paragraph.strip() == title.strip():
            continue
            
        # Check if paragraph looks like a heading
        is_heading = (len(paragraph) < 100 and 
                     not paragraph.endswith('.') and 
                     not paragraph.endswith('!') and 
                     not paragraph.endswith('?') and
                     '\n' not in paragraph and
                     paragraph != title)
        
        if is_heading:
            # Format as heading with emphasis and sentence wrapper
            ssml += f'  <s>\n'
            ssml += f'    <emphasis level="moderate">{escape_ssml_text(paragraph)}</emphasis>\n'
            ssml += f'  </s>\n'
            ssml += '  <break time="800ms"/>\n'
        else:
            # Regular paragraph - wrap full sentences in <s> tags
            sentences = split_into_sentences(paragraph)
            ssml += f'  <p>\n'
            for sentence in sentences:
                if sentence.strip():
                    ssml += f'    <s>{escape_ssml_text(sentence.strip())}</s>\n'
            ssml += f'  </p>\n'
            
            # Add pause between paragraphs
            if i < len(paragraphs) - 1:
                ssml += '  <break time="500ms"/>\n'
    
    ssml += '</speak>'
    return ssml

def create_elevenlabs_ssml(text, title=""):
    """
    Create ElevenLabs compatible SSML (limited tag support)
    """
    if not text:
        return ""
    
    ssml = '<speak>\n'
    
    # Add title with emphasis if provided
    lines = text.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    if title and title.strip() != first_line:
        ssml += f'  <emphasis>{escape_ssml_text(title)}</emphasis>\n'
        ssml += '  <break time="1s"/>\n'
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Skip if this paragraph is the same as the title we already added
        if title and paragraph.strip() == title.strip():
            continue
            
        # Check if paragraph looks like a heading
        is_heading = (len(paragraph) < 100 and 
                     not paragraph.endswith('.') and 
                     not paragraph.endswith('!') and 
                     not paragraph.endswith('?') and
                     '\n' not in paragraph and
                     paragraph != title)
        
        if is_heading:
            # Format as heading with emphasis (no <s> tags as they may not be supported)
            ssml += f'  <emphasis>{escape_ssml_text(paragraph)}</emphasis>\n'
            ssml += '  <break time="800ms"/>\n'
        else:
            # Regular paragraph - simpler format without <p> and <s> tags
            sentences = split_into_sentences(paragraph)
            for j, sentence in enumerate(sentences):
                if sentence.strip():
                    ssml += f'  {escape_ssml_text(sentence.strip())}\n'
                    # Add small pause between sentences
                    if j < len(sentences) - 1:
                        ssml += '  <break time="300ms"/>\n'
            
            # Add pause between paragraphs
            if i < len(paragraphs) - 1:
                ssml += '  <break time="600ms"/>\n'
    
    ssml += '</speak>'
    return ssml

def create_minimax_format(text, title=""):
    """
    Create MiniMax compatible text format with pause markers
    """
    if not text:
        return ""
    
    formatted_text = ""
    
    # Add title if provided
    lines = text.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    if title and title.strip() != first_line:
        formatted_text += title.strip() + " <#1.0#> "
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Skip if this paragraph is the same as the title we already added
        if title and paragraph.strip() == title.strip():
            continue
            
        # Check if paragraph looks like a heading
        is_heading = (len(paragraph) < 100 and 
                     not paragraph.endswith('.') and 
                     not paragraph.endswith('!') and 
                     not paragraph.endswith('?') and
                     '\n' not in paragraph and
                     paragraph != title)
        
        if is_heading:
            # Format as heading with pause
            formatted_text += paragraph + " <#0.8#> "
        else:
            # Regular paragraph with natural pauses
            sentences = split_into_sentences(paragraph)
            for j, sentence in enumerate(sentences):
                if sentence.strip():
                    formatted_text += sentence.strip()
                    # Add pause between sentences
                    if j < len(sentences) - 1:
                        formatted_text += " <#0.3#> "
                    else:
                        formatted_text += " "
            
            # Add pause between paragraphs
            if i < len(paragraphs) - 1:
                formatted_text += "<#0.6#> "
    
    return formatted_text.strip()

def split_into_sentences(text):
    """
    Split text into sentences for proper SSML structure
    """
    # Simple sentence splitting - can be improved with more sophisticated logic
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def escape_ssml_text(text):
    """
    Escape special characters for SSML
    """
    if not text:
        return ""
    
    # Escape XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

def process_bullet_points(text):
    """
    Process bullet points to make them more audio-friendly
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    processed_lines = []
    in_bullet_section = False
    bullet_items = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # Check if this line is a bullet point
        if stripped_line.startswith('•') and len(stripped_line) > 2:
            if not in_bullet_section:
                # Starting a new bullet section
                in_bullet_section = True
                bullet_items = []
            
            # Extract bullet content (remove bullet marker)
            bullet_content = stripped_line[1:].strip()
            bullet_items.append(bullet_content)
            
        else:
            # Not a bullet point
            if in_bullet_section:
                # We were in a bullet section, now format it for audio
                if bullet_items:
                    if len(bullet_items) == 1:
                        processed_lines.append(bullet_items[0])
                    elif len(bullet_items) == 2:
                        processed_lines.append(f"{bullet_items[0]}, and {bullet_items[1]}")
                    else:
                        # Multiple items: "First, second, third, and fourth"
                        formatted_list = ", ".join(bullet_items[:-1]) + f", and {bullet_items[-1]}"
                        processed_lines.append(formatted_list)
                    
                bullet_items = []
                in_bullet_section = False
            
            # Add the current line if it's not empty
            if stripped_line:
                processed_lines.append(line)
            else:
                processed_lines.append("")  # Preserve empty lines for paragraph breaks
    
    # Handle case where text ends with bullet points
    if in_bullet_section and bullet_items:
        if len(bullet_items) == 1:
            processed_lines.append(bullet_items[0])
        elif len(bullet_items) == 2:
            processed_lines.append(f"{bullet_items[0]}, and {bullet_items[1]}")
        else:
            formatted_list = ", ".join(bullet_items[:-1]) + f", and {bullet_items[-1]}"
            processed_lines.append(formatted_list)
    
    return '\n'.join(processed_lines)

def clean_for_audio_synthesis(text):
    """
    Clean text to make it more audio-synthesis friendly
    """
    if not text:
        return ""
    
    # Remove or replace problematic characters and symbols
    replacements = {
        # Programming/technical symbols
        '&': ' and ',
        '@': ' at ',
        '#': ' number ',
        '%': ' percent ',
        '+': ' plus ',
        '=': ' equals ',
        '<': ' less than ',
        '>': ' greater than ',
        '|': ' or ',
        '\\': ' backslash ',
        '/': ' slash ',
        '^': ' caret ',
        '~': ' tilde ',
        '`': '',
        
        # Currency and numbers
        '$': ' dollars ',
        '€': ' euros ',
        '£': ' pounds ',
        '¥': ' yen ',
        
        # Brackets and special punctuation
        '[': ' ',
        ']': ' ',
        '{': ' ',
        '}': ' ',
        '(': ' ',
        ')': ' ',
        '_': ' ',
        '*': ' ',
        
        # Quotes and similar
        '"': ' ',
        '"': ' ',
        '"': ' ',
        ''': ' ',
        ''': ' ',
        '`': ' ',
        
        # Other symbols - preserve bullet points differently
        '◦': '. ',
        '→': ' to ',
        '←': ' from ',
        '↑': ' up ',
        '↓': ' down ',
        '…': ' ',
        '–': ' ',
        '—': ' ',
        '×': ' times ',
        '÷': ' divided by ',
        '±': ' plus or minus ',
    }
    
    # Apply replacements
    cleaned_text = text
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    # Handle bullet points for better audio synthesis
    cleaned_text = process_bullet_points(cleaned_text)
    
    # Clean up URLs and email addresses
    cleaned_text = re.sub(r'https?://[^\s]+', ' web link ', cleaned_text)
    cleaned_text = re.sub(r'www\.[^\s]+', ' web link ', cleaned_text)
    cleaned_text = re.sub(r'\S+@\S+\.\S+', ' email address ', cleaned_text)
    
    # Clean up code-like patterns
    cleaned_text = re.sub(r'```[^`]*```', ' code block ', cleaned_text)
    cleaned_text = re.sub(r'`[^`]+`', ' code ', cleaned_text)
    
    # Remove standalone dots and formatting artifacts
    cleaned_text = re.sub(r'^\s*\.\s*$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^\s*[-=_]+\s*$', '', cleaned_text, flags=re.MULTILINE)
    
    # Fix Unicode smart quotes to regular quotes for better TTS
    cleaned_text = cleaned_text.replace("'", "'")  # Right single quote to apostrophe
    cleaned_text = cleaned_text.replace("'", "'")  # Left single quote to apostrophe
    cleaned_text = cleaned_text.replace(""", '"')  # Left double quote
    cleaned_text = cleaned_text.replace(""", '"')  # Right double quote
    
    # Basic punctuation spacing (should be minimal now that scraper is fixed)
    cleaned_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', cleaned_text)
    
    # Clean up whitespace and line breaks
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)  # Multiple line breaks
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Multiple spaces/tabs
    cleaned_text = re.sub(r'\n ', '\n', cleaned_text)  # Space at start of line
    cleaned_text = re.sub(r' \n', '\n', cleaned_text)  # Space at end of line
    
    # Remove empty lines at start and end
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def sanitize_filename(filename):
    """
    Sanitize filename by removing/replacing problematic characters
    """
    # Replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'[^\w\s\-_\.]', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)  # Multiple underscores
    sanitized = sanitized.strip('_. ')  # Remove leading/trailing chars
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized

def extract_and_process_content(json_file, output_dir, provider="google", config=None):
    """
    Extract content from JSON and save as individual text files for specified TTS provider
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
    
    processed_count = 0
    
    for article in data:
        try:
            # Extract required fields
            track_id = article.get('track_id', 0)
            title = article.get('title', 'Untitled')
            full_content = article.get('full_content', '')
            
            if not full_content:
                print(f"Warning: No full_content found for article ID {track_id}")
                continue
            
            # Clean content for audio synthesis
            cleaned_content = clean_for_audio_synthesis(full_content)
            
            if not cleaned_content:
                print(f"Warning: Content is empty after cleaning for article ID {track_id}")
                continue
            
            # Get provider configuration
            provider_config = TTS_PROVIDERS.get(provider, TTS_PROVIDERS['google'])
            
            # Apply provider-specific formatting
            final_content = create_ssml_markup(cleaned_content, title, provider)
            file_extension = provider_config['extension']
            
            # Create filename based on date and title (no track_id)
            release_date = article.get('releaseDate', '')
            creator = article.get('creator', '')
            
            # Format: YYYY-MM-DD_creator_title or just title if no date/creator
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
                print(f"Warning: Content for '{title}' ({len(final_content)} chars) exceeds {provider} limit ({max_length} chars)")
                
            # Save content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            print(f"Processed ({provider}): {filename}")
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing article {article.get('track_id', 'unknown')}: {e}")
            continue
    
    print(f"\nCompleted: {processed_count} files processed and saved to '{output_dir}'")
    return True

def print_provider_info():
    """Print information about supported TTS providers"""
    print("\n=== Supported TTS Providers ===")
    for provider_key, config in TTS_PROVIDERS.items():
        print(f"\n{provider_key.upper()}:")
        print(f"  Name: {config['name']}")
        print(f"  Format: {config['format']}")
        print(f"  Extension: {config['extension']}")
        print(f"  Max Length: {config['max_input_length']} characters")
        if config.get('note'):
            print(f"  Note: {config['note']}")
        if config.get('supports_tags'):
            print(f"  Supported Tags: {', '.join(config['supports_tags'])}")

def main():
    parser = argparse.ArgumentParser(
        description='Multi-Provider Content Extractor for Audio Synthesis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Google Cloud TTS (default)
  python content_extractor.py articles.json -p google

  # ElevenLabs with custom output directory
  python content_extractor.py articles.json -p elevenlabs -o ./elevenlabs_output

  # MiniMax with text format and pauses
  python content_extractor.py articles.json -p minimax -o ./minimax_output

  # Show provider information
  python content_extractor.py --list-providers
        """
    )
    
    parser.add_argument('json_file', nargs='?', help='Path to JSON file containing articles')
    parser.add_argument('-p', '--provider', choices=['google', 'elevenlabs', 'minimax'], 
                       default='google', help='TTS provider (default: google)')
    parser.add_argument('-o', '--output-dir', 
                       help='Output directory for files (default: provider-specific directory)')
    parser.add_argument('--list-providers', action='store_true',
                       help='List all supported TTS providers and their configurations')
    
    args = parser.parse_args()
    
    # Handle list providers command
    if args.list_providers:
        print_provider_info()
        sys.exit(0)
    
    # Validate required arguments
    if not args.json_file:
        parser.error("JSON file argument is required (unless using --list-providers)")
    
    if not os.path.exists(args.json_file):
        print(f"Error: File '{args.json_file}' does not exist.")
        sys.exit(1)
    
    # Set default output directory based on provider
    if not args.output_dir:
        provider_dirs = {
            'google': '../audeon_tools/Content/articles/google_tts',
            'elevenlabs': '../audeon_tools/Content/articles/elevenlabs',
            'minimax': '../audeon_tools/Content/articles/minimax'
        }
        args.output_dir = provider_dirs.get(args.provider, '../audeon_tools/Content/articles/output')
    
    # Print provider info
    provider_config = TTS_PROVIDERS[args.provider]
    print(f"Using TTS Provider: {provider_config['name']}")
    print(f"Output Format: {provider_config['format']}")
    print(f"File Extension: {provider_config['extension']}")
    if provider_config.get('note'):
        print(f"Note: {provider_config['note']}")
    print()
    
    success = extract_and_process_content(args.json_file, args.output_dir, args.provider)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()