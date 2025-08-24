#!/usr/bin/env python3
"""
Fix content cleaning issues in generated SSML files
"""
import re

def improved_clean_for_audio_synthesis(text):
    """
    Improved text cleaning that handles numbered lists and formatting better
    """
    if not text:
        return ""
    
    # Smart replacements that consider context
    replacements = {
        # Technical symbols - but be smart about context
        '&': ' and ',
        '@': ' at ',
        '%': ' percent ',
        '+': ' plus ',
        '=': ' equals ',
        '<': ' less than ',
        '>': ' greater than ',
        '|': ' or ',
        '\\': ' backslash ',
        '^': ' caret ',
        '~': ' tilde ',
        '`': '',
        
        # Currency
        '$': ' dollars ',
        '€': ' euros ',
        '£': ' pounds ',
        
        # Brackets and punctuation
        '[': ' ',
        ']': ' ',
        '{': ' ',
        '}': ' ',
        '(': ' ',
        ')': ' ',
        '_': ' ',
        '*': ' ',
        
        # Arrows and symbols
        '→': ' to ',
        '←': ' from ',
        '↑': ' up ',
        '↓': ' down ',
        '…': ' ',
        '–': ' ',
        '—': ' ',
    }
    
    # Apply basic replacements
    cleaned_text = text
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    # Smart handling of numbered lists
    # Replace patterns like "### 1." with "Number 1."
    cleaned_text = re.sub(r'#{1,6}\s*(\d+)\.', r'Number \1.', cleaned_text)
    
    # Handle markdown-style headers
    cleaned_text = re.sub(r'^#{1,6}\s*(.+)$', r'\1', cleaned_text, flags=re.MULTILINE)
    
    # Fix broken words (common OCR/extraction errors)
    word_fixes = {
        'ure on': 'pressure on',
        'ure,': 'pressure,',
        'ure ': 'pressure ',
        'slash ': '/',
        ' slash': '/',
        'number number': 'Number',
        'dot ': '. ',
    }
    
    for broken, fixed in word_fixes.items():
        cleaned_text = cleaned_text.replace(broken, fixed)
    
    # Clean up URLs and emails
    cleaned_text = re.sub(r'https?://[^\s]+', ' web link ', cleaned_text)
    cleaned_text = re.sub(r'www\.[^\s]+', ' web link ', cleaned_text)
    cleaned_text = re.sub(r'\S+@\S+\.\S+', ' email address ', cleaned_text)
    
    # Clean up code blocks
    cleaned_text = re.sub(r'```[^`]*```', ' code block ', cleaned_text)
    cleaned_text = re.sub(r'`[^`]+`', ' code ', cleaned_text)
    
    # Fix spacing and line breaks
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\n ', '\n', cleaned_text)
    cleaned_text = re.sub(r' \n', '\n', cleaned_text)
    
    return cleaned_text.strip()

# Example usage and testing
if __name__ == "__main__":
    test_text = """
    ### 1. Promise a new feature to a customer
    
    The pressure on you is intense to say yes.
    
    ### 2. Generalize customer interviews
    
    You take notes, learn, and draw maps.
    """
    
    result = improved_clean_for_audio_synthesis(test_text)
    print("Cleaned text:")
    print(result)