# TTS-Extraction Technical Specification

**Version**: 1.0  
**Date**: 2025-01-21  
**Document**: TTS-Extraction Audio Generation Tool Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Provider Support](#provider-support)
4. [Core Functions](#core-functions)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Advanced Features](#advanced-features)
8. [Error Handling](#error-handling)
9. [Integration Guide](#integration-guide)
10. [Troubleshooting](#troubleshooting)

---

## Overview

TTS-Extraction is a comprehensive audio generation tool that converts text and SSML content to speech using multiple TTS providers. It handles large content processing, multi-voice synthesis, and audio file management with advanced chunking and combination capabilities.

### Key Features
- **Multi-Provider Support**: Google Cloud TTS, ElevenLabs, MiniMax TTS
- **Format Support**: Plain text, SSML, provider-specific formats
- **Large Content Handling**: Automatic chunking for content over API limits
- **Multi-Voice Processing**: Supports SSML with multiple voice sections
- **Audio Combination**: Seamless merging of audio chunks using ffmpeg
- **Flexible Output**: File output or direct audio playback

### Current Provider Support
- **Google Cloud TTS** ✅ Full Support
- **ElevenLabs** ✅ Full Support  
- **MiniMax TTS** ❌ **Requires Implementation**

---

## Architecture

### Core Components

```
TTS-Extraction Architecture

Input Layer:
├── Text Input (-t)
├── File Input (-f)
└── SSML Detection

Processing Layer:
├── Content Analysis
├── Provider Selection
├── Format Validation
└── Size Optimization

Provider Layer:
├── Google Cloud TTS API
├── ElevenLabs API
└── MiniMax API (To be implemented)

Output Layer:
├── Audio Generation
├── Chunk Combination
└── File Management
```

### Data Flow

```
Text/SSML Input → Content Analysis → Provider Routing → API Calls → Audio Generation → File Output
                     ↓
                 Size Check → Chunking → Multi-API Calls → Audio Combination
                     ↓
                Multi-Voice → Voice Separation → Per-Voice Processing → Audio Merging
```

---

## Provider Support

### Google Cloud TTS (Implemented)

#### API Configuration
```python
# Environment Variable Required
GOOGLE_TTS_API_KEY=your_api_key_here

# API Endpoint
https://texttospeech.googleapis.com/v1/text:synthesize
```

#### Supported Parameters
```python
{
    "input": {"text": "content" or "ssml": "content"},
    "voice": {
        "languageCode": "en-US",
        "name": "en-US-Studio-O",
        "ssmlGender": "NEUTRAL"
    },
    "audioConfig": {
        "audioEncoding": "MP3|LINEAR16|OGG_OPUS",
        "speakingRate": 0.25-4.0,
        "pitch": -20.0-20.0,
        "volumeGainDb": -96.0-16.0
    }
}
```

#### Features
- **Full SSML Support**: All SSML tags supported
- **Content Limit**: 5,000 bytes per request
- **Voice Selection**: 220+ voices across 40+ languages
- **Audio Formats**: MP3, LINEAR16, OGG_OPUS
- **Multi-Voice**: Supported via SSML `<voice>` tags

### ElevenLabs (Implemented)

#### API Configuration
```python
# Environment Variable Required
ELEVENLABS_API_KEY=your_api_key_here

# API Endpoint
https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
```

#### Supported Parameters
```python
{
    "text": "content",
    "model_id": "eleven_flash_v2_5|eleven_turbo_v2_5|eleven_v3",
    "voice_settings": {
        "stability": 0.0-1.0,
        "similarity_boost": 0.0-1.0,
        "style": 0.0-1.0,
        "use_speaker_boost": true/false
    }
}
```

#### Features
- **Limited SSML Support**: Basic tags only
- **Content Limit**: 5,000 characters per request
- **Voice Selection**: 120+ voices, voice cloning
- **Audio Format**: MP3 only
- **Models**: Flash v2.5 (75ms latency), Turbo v2.5, v3

### MiniMax TTS (To Be Implemented)

#### Proposed API Configuration
```python
# Environment Variable Required
MINIMAX_API_KEY=your_api_key_here

# API Endpoint  
https://api.minimax.chat/v1/t2a_pro
```

#### Proposed Parameters
```python
{
    "model": "speech-02-hd",
    "text": "content with <#0.5#> pause markers",
    "voice_setting": {
        "voice_id": "female-shaonv",
        "speed": 0.1-3.0,
        "vol": 0.1-2.0,
        "pitch": -12-12,
        "emotion": "happy|sad|angry|fearful|disgusted|surprised|neutral"
    },
    "audio_setting": {
        "format": "mp3|pcm|flac|wav",
        "sample_rate": 8000-44100,
        "bitrate": 64000-320000,
        "channel": 1-2
    }
}
```

#### Proposed Features
- **No SSML Support**: Uses proprietary pause format `<#x#>`
- **Content Limit**: 8,000 characters per request
- **Voice Selection**: 100+ voices with emotion control
- **Audio Formats**: MP3, PCM, FLAC, WAV
- **Emotion Control**: 7 emotion types with auto-detection

---

## Core Functions

### 1. Content Analysis Functions

#### `is_ssml(text)` 
```python
def is_ssml(text):
    """Detect if input text is SSML format"""
    text_stripped = text.strip()
    return (text_stripped.startswith('<?xml') or 
            text_stripped.startswith('<speak')) and '<speak' in text_stripped
```

#### `split_ssml_by_breaks(ssml_text, max_bytes)`
```python
def split_ssml_by_breaks(ssml_text, max_bytes):
    """Split SSML content into valid chunks by logical breaks"""
    # Splits by <break> tags first, then by sentences if needed
    # Maintains SSML structure integrity
    # Returns list of valid SSML chunks
```

### 2. Provider-Specific Functions

#### Google Cloud TTS
```python
def text_to_speech_single(text, output_file, lang='en-US', voice_name=None, 
                         audio_format='MP3', speaking_rate=1.0, pitch=0.0, 
                         volume_gain_db=0.0, force_ssml=False, provider='google'):
    """Single API call to Google Cloud TTS"""
```

#### ElevenLabs
```python
def elevenlabs_tts_single(text, output_file, voice_id=None, 
                         model_id="eleven_turbo_v2_5", stability=0.5, 
                         similarity_boost=0.5, style=0.0, use_speaker_boost=True):
    """Single API call to ElevenLabs TTS"""
```

#### MiniMax (To Be Implemented)
```python
def minimax_tts_single(text, output_file, voice_id=None, model_id="speech-02-hd",
                      speed=1.0, pitch=0, volume=1.0, emotion="happy", 
                      audio_format="mp3", sample_rate=32000):
    """Single API call to MiniMax TTS - NEEDS IMPLEMENTATION"""
```

### 3. Content Processing Functions

#### Large Content Processing
```python
def process_large_ssml(ssml_text, output_file, lang='en-US', voice_name=None,
                      audio_format='MP3', speaking_rate=1.0, pitch=0.0, 
                      volume_gain_db=0.0, provider='google'):
    """Process large SSML by splitting into chunks and combining audio"""
```

#### Multi-Voice Processing
```python
def process_multi_voice_ssml(ssml_text, output_file, lang='en-US', 
                           audio_format='MP3', speaking_rate=1.0, pitch=0.0, 
                           volume_gain_db=0.0, provider='google'):
    """Process SSML with multiple voice tags"""
```

### 4. Audio Management Functions

#### Audio Combination
```python
def combine_audio_files(input_files, output_file):
    """Combine multiple audio files using ffmpeg"""
    # Creates temporary filelist for ffmpeg concat
    # Handles file path escaping
    # Returns success/failure status
```

---

## Usage Examples

### Command Line Interface

#### Basic Text Conversion
```bash
# Google Cloud TTS (default)
python TTS-extraction.py -t "Hello world" -o output.mp3

# ElevenLabs
python TTS-extraction.py -t "Hello world" -o output.mp3 --provider elevenlabs

# MiniMax (when implemented)
python TTS-extraction.py -t "Hello world" -o output.mp3 --provider minimax
```

#### File-Based Conversion
```bash
# Convert SSML file
python TTS-extraction.py -f article.ssml -o output.mp3 --provider google

# Convert plain text file  
python TTS-extraction.py -f article.txt -o output.mp3 --provider elevenlabs
```

#### Advanced Parameters
```bash
# Google with custom voice and audio settings
python TTS-extraction.py -f content.ssml -o output.mp3 \
  --provider google \
  --voice "en-US-Studio-O" \
  --rate 1.2 \
  --pitch 2.0 \
  --volume -5.0 \
  --format LINEAR16

# ElevenLabs with voice ID
python TTS-extraction.py -f content.txt -o output.mp3 \
  --provider elevenlabs \
  --voice "21m00Tcm4TlvDq8ikWAM"
```

### Python API Usage

#### Basic Usage
```python
from TTS_extraction import text_to_speech

# Simple conversion
success = text_to_speech(
    text="Hello world", 
    output_file="output.mp3",
    provider="google"
)

# Advanced conversion
success = text_to_speech(
    text=ssml_content,
    output_file="output.mp3", 
    lang="en-US",
    voice_name="en-US-Studio-O",
    audio_format="MP3",
    speaking_rate=1.2,
    pitch=2.0,
    provider="google"
)
```

---

## Configuration

### Environment Variables

#### Required API Keys
```bash
# .env file
GOOGLE_TTS_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here  
MINIMAX_API_KEY=your_minimax_api_key_here  # When implemented
```

#### Optional Configuration
```bash
# Default audio settings
DEFAULT_AUDIO_FORMAT=MP3
DEFAULT_SPEAKING_RATE=1.0
DEFAULT_PITCH=0.0
DEFAULT_VOLUME=0.0

# Processing limits
MAX_CHUNK_SIZE=4500
MAX_CONCURRENT_REQUESTS=5
```

### Provider Configuration

#### Google Cloud TTS
```python
GOOGLE_CONFIG = {
    "max_bytes": 5000,
    "supported_formats": ["MP3", "LINEAR16", "OGG_OPUS"],
    "default_voice": None,  # Auto-select
    "chunk_size": 4500
}
```

#### ElevenLabs
```python
ELEVENLABS_CONFIG = {
    "max_chars": 5000,
    "supported_formats": ["MP3"],
    "default_voice": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "default_model": "eleven_flash_v2_5",
    "chunk_size": 4500
}
```

#### MiniMax (Proposed)
```python
MINIMAX_CONFIG = {
    "max_chars": 8000,
    "supported_formats": ["mp3", "pcm", "flac", "wav"],
    "default_voice": "female-shaonv",
    "default_model": "speech-02-hd",
    "chunk_size": 7500
}
```

---

## Advanced Features

### 1. Multi-Voice SSML Processing

#### Supported SSML Structure
```xml
<speak>
  <voice name="en-US-Studio-O" provider="google">
    <emphasis level="strong">Narrator voice</emphasis>
    <break time="1s"/>
  </voice>
  
  <voice name="21m00Tcm4TlvDq8ikWAM" provider="elevenlabs">
    Character dialogue here.
  </voice>
  
  <voice name="female-shaonv" provider="minimax">
    Another character speaking.
  </voice>
</speak>
```

#### Processing Flow
1. **Parse SSML**: Extract voice sections and providers
2. **Route to Providers**: Send each section to appropriate TTS service
3. **Generate Audio**: Create audio files for each voice section
4. **Combine Audio**: Merge all sections into final output

### 2. Large Content Chunking

#### Chunking Strategy
```python
# Priority order for splitting:
1. SSML <break> tags
2. Paragraph boundaries (</p>)
3. Sentence endings (. ! ?)
4. Word boundaries (last resort)
```

#### Chunk Size Limits
- **Google Cloud TTS**: 4,500 bytes (safety buffer)
- **ElevenLabs**: 4,500 characters
- **MiniMax**: 7,500 characters (proposed)

### 3. Audio Format Support

#### Format Matrix
| Provider | MP3 | LINEAR16 | OGG_OPUS | PCM | FLAC | WAV |
|----------|-----|----------|----------|-----|------|-----|
| Google | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| ElevenLabs | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| MiniMax | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## Error Handling

### API Error Responses

#### Google Cloud TTS Errors
```python
Common Error Codes:
- 400: Invalid request (malformed SSML, invalid parameters)
- 401: Authentication failed (invalid API key)
- 403: Permission denied (quota exceeded)
- 429: Rate limit exceeded
- 500: Internal server error
```

#### ElevenLabs Errors  
```python
Common Error Codes:
- 400: Invalid request (unsupported voice, invalid parameters)
- 401: Invalid API key
- 422: Unprocessable content (quota exceeded, voice not found)
- 429: Rate limit exceeded
- 500: Server error
```

#### MiniMax Errors (Proposed)
```python
Common Error Codes:
- 400: Invalid request parameters
- 401: Authentication failed
- 403: Insufficient quota/permissions
- 429: Rate limit exceeded  
- 500: Server error
```

### Error Recovery Strategies

#### Automatic Retry Logic
```python
def retry_with_backoff(func, max_retries=3, backoff_factor=2):
    """Exponential backoff retry for API calls"""
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
```

#### Chunk Size Reduction
```python
def reduce_chunk_size_on_error(original_size):
    """Reduce chunk size when encountering content limit errors"""
    return min(original_size * 0.8, original_size - 500)
```

---

## Integration Guide

### With Content Extractor Pipeline

#### Complete Workflow
```bash
# Step 1: Generate formatted content
python Tools/content_extractor.py articles.json -p google -o ./google_content

# Step 2: Convert to audio
for file in ./google_content/*.ssml; do
  python Tools/TTS-extraction.py -f "$file" -o "./audio/$(basename "$file" .ssml).mp3" --provider google
done
```

#### Batch Processing Script
```python
#!/usr/bin/env python3
"""
Batch audio generation from content extractor output
"""
import os
import glob
from TTS_extraction import text_to_speech

def batch_convert_to_audio(input_dir, output_dir, provider="google"):
    """Convert all text files in directory to audio"""
    
    # Get file extension based on provider
    extensions = {
        "google": "*.ssml",
        "elevenlabs": "*.ssml", 
        "minimax": "*.txt"
    }
    
    pattern = os.path.join(input_dir, extensions.get(provider, "*.txt"))
    files = glob.glob(pattern)
    
    for file_path in files:
        # Read content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}.mp3")
        
        # Convert to audio
        print(f"Converting: {base_name}")
        success = text_to_speech(
            content, 
            output_file,
            provider=provider
        )
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed: {base_name}")

if __name__ == "__main__":
    batch_convert_to_audio("./google_content", "./audio", "google")
```

---

## Troubleshooting

### Common Issues

#### 1. API Authentication Failures
**Problem**: "API key not found" or "Authentication failed"
**Solution**: 
```bash
# Check environment variables
echo $GOOGLE_TTS_API_KEY
echo $ELEVENLABS_API_KEY

# Verify .env file exists and is properly formatted
cat .env
```

#### 2. Content Too Large Errors
**Problem**: "Request payload too large"
**Solution**:
- Content automatically chunked, but check chunk size settings
- Reduce `MAX_CHUNK_SIZE` in configuration
- Use `split_ssml_by_breaks()` function manually

#### 3. Audio Combination Failures
**Problem**: "Error combining audio files"  
**Solution**:
```bash
# Check ffmpeg installation
which ffmpeg
ffmpeg -version

# Install if missing (macOS)
brew install ffmpeg
```

#### 4. Voice Not Found Errors
**Problem**: "Voice name not supported"
**Solution**:
```python
# List available voices for provider
# Google Cloud TTS
curl -X GET "https://texttospeech.googleapis.com/v1/voices?key=${GOOGLE_TTS_API_KEY}"

# ElevenLabs
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}"
```

### Performance Optimization

#### 1. Concurrent Processing
```python
# Process multiple chunks concurrently
import concurrent.futures
import asyncio

async def process_chunks_async(chunks, provider):
    """Process multiple chunks concurrently"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(text_to_speech_single, chunk, f"temp_{i}.mp3", provider=provider)
            for i, chunk in enumerate(chunks)
        ]
        results = await asyncio.gather(*futures)
    return results
```

#### 2. Caching Strategy
```python
# Cache audio files to avoid regeneration
import hashlib

def get_content_hash(content):
    """Generate hash for content caching"""
    return hashlib.md5(content.encode()).hexdigest()

def check_cache(content, provider, voice_settings):
    """Check if audio already exists in cache"""
    content_hash = get_content_hash(content + str(voice_settings))
    cache_file = f"cache/{provider}_{content_hash}.mp3"
    return cache_file if os.path.exists(cache_file) else None
```

---

## MiniMax Implementation Requirements

### Required Code Additions

#### 1. Add MiniMax Support Constant
```python
# At top of TTS-extraction.py
PROVIDER_MINIMAX = "minimax"
```

#### 2. Implement MiniMax TTS Function
```python
def minimax_tts_single(text, output_file, voice_id=None, model_id="speech-02-hd",
                      speed=1.0, pitch=0, volume=1.0, emotion="happy", 
                      audio_format="mp3", sample_rate=32000, bitrate=128000):
    """
    Convert text to speech using MiniMax API (single request)
    """
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("Error: MINIMAX_API_KEY not found in environment variables")
        return False
    
    # Default voice if none specified
    if not voice_id:
        voice_id = "female-shaonv"
    
    try:
        url = "https://api.minimax.chat/v1/t2a_pro"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "text": text,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": volume,
                "pitch": pitch,
                "emotion": emotion
            },
            "audio_setting": {
                "format": audio_format,
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "channel": 1
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # MiniMax returns audio data differently - check response format
            audio_data = response.content  # or response.json()['audio_data'] if base64
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            return True
        else:
            print(f"Error with MiniMax TTS: API request failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with MiniMax TTS: {e}")
        return False
```

#### 3. Update Provider Routing
```python
# In text_to_speech_single function
def text_to_speech_single(text, output_file, lang='en-US', voice_name=None, audio_format='MP3', 
                         speaking_rate=1.0, pitch=0.0, volume_gain_db=0.0, force_ssml=False, provider=PROVIDER_GOOGLE):
    """Convert text to speech using specified provider"""
    
    if provider == PROVIDER_MINIMAX:
        # Convert MiniMax proprietary format from content_extractor
        # text already contains <#x#> pause markers
        return minimax_tts_single(
            text=text,
            output_file=output_file, 
            voice_id=voice_name,
            speed=speaking_rate,
            pitch=pitch,
            volume=1.0 + (volume_gain_db / 20),  # Convert dB to linear scale
            audio_format=audio_format.lower()
        )
    elif provider == PROVIDER_ELEVENLABS:
        return elevenlabs_tts_single(text, output_file, voice_name, force_ssml=force_ssml)
    else:
        # Default to Google TTS
        # ... existing Google implementation
```

#### 4. Update Command Line Arguments
```python
# In main() function
parser.add_argument('--provider', choices=[PROVIDER_GOOGLE, PROVIDER_ELEVENLABS, PROVIDER_MINIMAX], 
                   default=PROVIDER_GOOGLE, help='TTS provider (default: google)')
```

#### 5. Update Environment Check
```python
# In text_to_speech function
if provider == PROVIDER_MINIMAX:
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("Error: MINIMAX_API_KEY not found in environment variables")
        print("Make sure your .env file contains: MINIMAX_API_KEY=your_api_key_here")
        sys.exit(1)
```

---

## Conclusion

The TTS-Extraction tool provides a robust foundation for multi-provider audio generation with advanced content processing capabilities. With the addition of MiniMax support, it will offer comprehensive coverage of major TTS providers while maintaining consistent API and processing workflows.

### Implementation Priority
1. **High Priority**: MiniMax API integration
2. **Medium Priority**: Performance optimizations (concurrent processing)
3. **Low Priority**: Advanced caching and batch processing utilities

### Testing Requirements  
- API integration testing for all three providers
- Large content processing validation
- Multi-voice SSML testing
- Audio quality verification across providers

---

**End of Document**

*This document should be updated as new features are implemented and providers are added.*