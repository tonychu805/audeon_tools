#!/usr/bin/env python3
"""
Fixed SSML Chunker - Properly splits SSML while maintaining valid XML structure
"""
import xml.etree.ElementTree as ET
import re

def smart_split_ssml(ssml_text, max_bytes=4500):
    """
    Intelligently split SSML content while maintaining valid XML structure
    """
    try:
        # Parse the SSML to understand structure
        root = ET.fromstring(ssml_text)
        
        # Extract all content while preserving structure
        chunks = []
        current_chunk_elements = []
        current_size = len('<speak>\n</speak>')  # Base wrapper size
        
        for element in root:
            # Convert element to string to measure size
            element_str = ET.tostring(element, encoding='unicode', method='xml')
            element_size = len(element_str.encode('utf-8'))
            
            # Check if adding this element would exceed the limit
            if current_size + element_size > max_bytes and current_chunk_elements:
                # Create chunk from current elements
                chunk_content = create_chunk_from_elements(current_chunk_elements)
                chunks.append(chunk_content)
                
                # Start new chunk
                current_chunk_elements = [element]
                current_size = len('<speak>\n</speak>') + element_size
            else:
                # Add element to current chunk
                current_chunk_elements.append(element)
                current_size += element_size
        
        # Add the last chunk if it has content
        if current_chunk_elements:
            chunk_content = create_chunk_from_elements(current_chunk_elements)
            chunks.append(chunk_content)
        
        return chunks
        
    except ET.ParseError as e:
        print(f"Error parsing SSML: {e}")
        # Fallback to simple text splitting
        return fallback_text_split(ssml_text, max_bytes)

def create_chunk_from_elements(elements):
    """
    Create a valid SSML chunk from a list of elements
    """
    chunk_content = '<speak>\n'
    
    for element in elements:
        element_str = ET.tostring(element, encoding='unicode', method='xml')
        # Clean up the XML formatting
        element_str = element_str.replace('><', '>\n  <')
        if not element_str.startswith('  '):
            element_str = '  ' + element_str
        chunk_content += element_str + '\n'
    
    chunk_content += '</speak>'
    return chunk_content

def fallback_text_split(ssml_text, max_bytes):
    """
    Fallback method for splitting SSML when parsing fails
    """
    # Remove speak tags to get inner content
    if ssml_text.startswith('<speak>') and ssml_text.endswith('</speak>'):
        inner_content = ssml_text[7:-8].strip()
    else:
        inner_content = ssml_text
    
    # Split by break tags first, then by paragraphs
    if '<break time=' in inner_content:
        parts = re.split(r'(<break time="[^"]+"/>)', inner_content)
    elif '</p>' in inner_content:
        parts = re.split(r'(</p>\s*)', inner_content)
    else:
        # Split by sentences as last resort
        parts = re.split(r'(\.\s+)', inner_content)
    
    chunks = []
    current_chunk = ""
    
    for part in parts:
        test_chunk = current_chunk + part
        test_ssml = f'<speak>\n{test_chunk}\n</speak>'
        
        if len(test_ssml.encode('utf-8')) <= max_bytes or not current_chunk:
            current_chunk = test_chunk
        else:
            # Current chunk is full, save it and start new chunk
            if current_chunk:
                chunks.append(f'<speak>\n{current_chunk}\n</speak>')
            current_chunk = part
    
    # Add the last chunk
    if current_chunk:
        chunks.append(f'<speak>\n{current_chunk}\n</speak>')
    
    return chunks

def validate_ssml_chunk(chunk):
    """
    Validate that a chunk is proper SSML
    """
    try:
        ET.fromstring(chunk)
        return True, "Valid"
    except ET.ParseError as e:
        return False, str(e)

def fix_broken_ssml_chunk(chunk):
    """
    Attempt to fix common SSML issues in chunks
    """
    # Common fixes
    fixes = [
        # Fix unclosed emphasis tags
        (r'<emphasis level="[^"]*">\s*$', ''),
        (r'<emphasis>\s*$', ''),
        
        # Fix unclosed prosody tags
        (r'<prosody[^>]*>\s*$', ''),
        
        # Fix unclosed paragraph tags
        (r'<p>\s*$', ''),
        
        # Add missing closing tags for incomplete elements
        (r'<emphasis level="[^"]*">([^<]*)</speak>', r'<emphasis level="moderate">\1</emphasis></speak>'),
        (r'<emphasis>([^<]*)</speak>', r'<emphasis>\1</emphasis></speak>'),
        (r'<prosody[^>]*>([^<]*)</speak>', r'<prosody>\1</prosody></speak>'),
    ]
    
    fixed_chunk = chunk
    for pattern, replacement in fixes:
        fixed_chunk = re.sub(pattern, replacement, fixed_chunk, flags=re.DOTALL)
    
    return fixed_chunk

# Test the function
if __name__ == "__main__":
    # Test with sample SSML
    test_ssml = """<speak>
  <p>Hello everyone, I'm <emphasis level="moderate">Tony</emphasis>, Senior Product Manager at Synology.</p>
  <break time="500ms"/>
  <p>This is a test paragraph with <prosody rate="slow">slow speech</prosody>.</p>
  <break time="700ms"/>
  <p>Another paragraph here.</p>
</speak>"""
    
    print("Original SSML size:", len(test_ssml.encode('utf-8')), "bytes")
    chunks = smart_split_ssml(test_ssml, max_bytes=200)  # Small chunks for testing
    
    print(f"Split into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks, 1):
        is_valid, message = validate_ssml_chunk(chunk)
        print(f"Chunk {i}: {len(chunk.encode('utf-8'))} bytes - {'✅' if is_valid else '❌'} {message}")
        if not is_valid:
            print(f"Content: {chunk[:100]}...")