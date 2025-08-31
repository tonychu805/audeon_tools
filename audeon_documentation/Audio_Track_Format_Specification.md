# Audio Track Format Specification

## Overview
This document defines the structured format for converting articles to SSML format, ensuring consistent audio track production across all content.

## Audio Track Structure

### 1. Intro Jingle
- **Purpose**: Brand recognition and audio transition
- **Duration**: 3-5 seconds
- **Format**: Pre-recorded audio clip (MP3, WAV, M4A, AAC, OGG, FLAC)
- **Location**: `/Content/audio/intro_jingle/` (auto-detected)
- **Implementation**: Automatically inserted at the beginning of every track
- **Detection**: Intelligent file discovery via `find_intro_jingle()` function

### 2. Title Announcement
- **Content**: Full article title
- **Voice**: Primary narrator voice
- **Tone**: Clear, professional
- **Pacing**: Slightly slower than normal reading speed
- **SSML Tags**: 
  ```xml
  <prosody rate="0.9" pitch="+2st">
    <emphasis level="moderate">[Article Title]</emphasis>
  </prosody>
  ```

### 3. Author Attribution
- **Content**: Author name with "by" prefix
- **Voice**: Same as primary narrator
- **Format**: "By [Author Name]"
- **Pacing**: Normal reading speed
- **SSML Tags**:
  ```xml
  <prosody rate="1.0">
    By <emphasis level="moderate">[Author Name]</emphasis>
  </prosody>
  ```

### 4. Article Content
- **Content**: Full article text converted to SSML
- **Voice**: Primary narrator voice
- **Processing**: 
  - Remove HTML tags
  - Convert to natural speech patterns
  - Add appropriate pauses for paragraphs
  - Handle special characters and formatting
- **SSML Features**:
  - Paragraph breaks: `<break time="1s"/>`
  - Emphasis for important points
  - Natural prosody adjustments

### 5. Ending Segment
- **Content**: Standardized closing message
- **Voice**: Same as primary narrator
- **Standard Text**: "Thank you for listening. Check out my other pieces for more insights."
- **Tone**: Warm, inviting
- **SSML Tags**:
  ```xml
  <prosody rate="0.95" pitch="+1st">
    Thank you for listening. <break time="0.5s"/> 
    Check out my other pieces for more insights.
  </prosody>
  ```

## Implementation Guidelines

### Current Implementation Status
✅ **IMPLEMENTED** in `Tools/content_extractor.py` (Version 2.1, August 30, 2025)

The Audio Track Format Specification is fully implemented in the Content Extractor tool with automatic intro jingle detection and integrated into the complete Audeon Tools pipeline.

### File Naming Convention
- Format: `YYYY-MM-DD_[Author]_[Title]_[VoiceID].ssml`
- Example: `2025-08-28_John Smith_Product Strategy Guide_en-US-Neural2-J.ssml`
- **Current Implementation**: Files generated with `[VoiceID]` placeholder, replaced during TTS synthesis
- Voice ID Examples:
  - ElevenLabs: `21m00Tcm4TlvDq8ikWAM` (Rachel), `2EiwWnXFnvU5JabPnv8n` (Clyde), `Xb7hH8MSUJpSbSDYk0k2` (Alice)
  - Google Cloud TTS: `en-US-Neural2-J`, `en-GB-Neural2-A`, `en-US-Wavenet-F`
  - Azure: `en-US-JennyNeural`, `en-US-GuyNeural`
  - MiniMax: `audiobook_female_1`, `Charming_Lady`, `cute_boy`

### SSML Structure Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  
  <!-- Intro Jingle Reference (Auto-detected) -->
  <audio src="Content/audio/intro_jingle/intro_jingle_computer_startup.mp3"/>
  
  <!-- Title -->
  <prosody rate="0.9" pitch="+2st">
    <emphasis level="moderate">[ARTICLE_TITLE]</emphasis>
  </prosody>
  <break time="1s"/>
  
  <!-- Author -->
  <prosody rate="1.0">
    By <emphasis level="moderate">[AUTHOR_NAME]</emphasis>
  </prosody>
  <break time="2s"/>
  
  <!-- Article Content -->
  [ARTICLE_CONTENT_WITH_SSML_FORMATTING]
  
  <!-- Ending -->
  <break time="2s"/>
  <prosody rate="0.95" pitch="+1st">
    Thank you for listening. <break time="0.5s"/> 
    Check out my other pieces for more insights.
  </prosody>
  
</speak>
```

## Quality Standards
- **Consistency**: All tracks follow identical structure
- **Timing**: Appropriate pauses between sections
- **Voice Quality**: Professional, clear narration
- **Audio Levels**: Consistent volume across all segments
- **Duration**: Optimize for content comprehension without rushing

## Processing Workflow

### Current Implementation Workflow
The Audio Track Format is automatically applied by the Content Extractor in the Audeon Tools pipeline:

```bash
# Complete Pipeline with Audio Track Format
python Tools/master_article_processor.py              # Step 1: Generate enhanced JSON
python Tools/content_extractor.py articles.json -p google  # Step 2: Apply Audio Track Format  
python Tools/batch_tts_processor.py input output --provider google  # Step 3: Synthesize audio
```

### Detailed Processing Steps
1. **Extract Metadata**: Title and author from Master Article Processor JSON
2. **Detect Intro Jingle**: Automatic discovery via `find_intro_jingle()` function
3. **Clean Content**: Audio-optimized text processing via `clean_for_audio_synthesis()`
4. **Apply Format Structure**: Automatic insertion of 5-part Audio Track Format
5. **Provider Optimization**: Format-specific SSML/text generation with dynamic jingle paths
6. **Generate Files**: Output with voice ID placeholder in filename
7. **Pipeline Integration**: Ready for TTS synthesis with complete structure

### Provider-Specific Implementation
- **Google Cloud TTS**: Full SSML with prosody control and audio references
- **ElevenLabs**: Simplified SSML compatible with API limitations
- **MiniMax**: Text format with proprietary pause markers and assembly notes

### Quality Assurance
- **Format Compliance**: 100% of generated files include all 5 components
- **SSML Validation**: XML syntax checking for SSML-based providers
- **Content Integrity**: Maintains article readability while optimizing for audio synthesis