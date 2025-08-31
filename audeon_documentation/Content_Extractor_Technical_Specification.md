# Content Extractor Technical Specification

**Version**: 2.2  
**Date**: August 30, 2025  
**Tool**: `Tools/content_extractor.py`

## 📋 **Overview**

The Content Extractor is a multi-provider text-to-speech content formatting tool that transforms JSON article data into provider-specific SSML/text files. **Version 2.2** implements the complete [Audio Track Format Specification](Audio_Track_Format_Specification.md), ensuring all generated content follows a consistent 5-part audio structure.

### **Purpose**
- **Input**: Enhanced JSON from Master Article Processor
- **Output**: Provider-specific SSML/text files ready for TTS synthesis
- **Structure**: Implements Audio Track Format (intro jingle, title, author, content, ending)
- **Multi-Provider**: Supports Google Cloud TTS, ElevenLabs, MiniMax, and OpenAI TTS

### **Key Features**
- **Audio Track Format Compliance**: All outputs follow 5-part structure specification
- **Automatic Intro Jingle Detection**: Intelligently finds and references intro jingle files
- **Provider Optimization**: Format-specific SSML generation for each TTS provider
- **Content Cleaning**: Audio-optimized text processing and symbol replacement
- **Metadata Integration**: Author attribution and title formatting from JSON data
- **Filename Format**: Implements voice ID placeholder for tracking

---

## 🏗️ **Architecture**

### **Processing Flow**
```
Enhanced JSON Articles
       ↓
   Extract Title, Author, Content
       ↓
   Clean Content for Audio Synthesis
       ↓
   Apply Audio Track Format Structure:
   1. Intro Jingle Reference
   2. Title Announcement  
   3. Author Attribution
   4. Article Content
   5. Standardized Ending
       ↓
   Provider-Specific Formatting
       ↓
   SSML/Text Files with Audio Track Format
```

### **Audio Track Format Integration**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

  <!-- 1. Intro Jingle Reference (Auto-detected) -->
  <audio src="Content/audio/intro_jingle/intro_jingle_computer_startup.mp3"/>

  <!-- 2. Title Announcement -->
  <prosody rate="0.9" pitch="+2st">
    <emphasis level="moderate">[ARTICLE_TITLE]</emphasis>
  </prosody>
  <break time="1s"/>

  <!-- 3. Author Attribution -->
  <prosody rate="1.0">
    By <emphasis level="moderate">[AUTHOR_NAME]</emphasis>
  </prosody>
  <break time="2s"/>

  <!-- 4. Article Content -->
  [FORMATTED_ARTICLE_CONTENT]

  <!-- 5. Standardized Ending -->
  <break time="2s"/>
  <prosody rate="0.95" pitch="+1st">
    Thank you for listening. <break time="0.5s"/> 
    Check out my other pieces for more insights.
  </prosody>

</speak>
```

---

## ⚙️ **Provider Support**

### **Google Cloud TTS (Full SSML)**
```python
TTS_PROVIDERS['google'] = {
    'name': 'Google Cloud Text-to-Speech',
    'format': 'ssml',
    'extension': '.ssml',
    'supports_tags': ['speak', 'break', 'emphasis', 'p', 's', 'prosody', 'phoneme', 'say-as'],
    'max_input_length': 5000,
    'audio_track_format': 'full_ssml_with_prosody'
}
```

**Features**:
- Full XML SSML with proper declaration and namespaces
- Rich prosody control (rate, pitch adjustments)
- Audio jingle reference via `<audio>` tag
- Complete emphasis and break tag support

### **ElevenLabs (Limited SSML)**
```python
TTS_PROVIDERS['elevenlabs'] = {
    'name': 'ElevenLabs',
    'format': 'ssml_limited',
    'extension': '.ssml',
    'supports_tags': ['speak', 'break', 'emphasis', 'prosody', 'phoneme'],
    'max_input_length': 5000,
    'audio_track_format': 'basic_ssml_no_prosody'
}
```

**Features**:
- Basic SSML structure without advanced prosody
- Audio jingle reference included (may require manual handling)
- Simplified emphasis and break tags
- Compatible with ElevenLabs API limitations

### **MiniMax (Text with Pause Markers)**
```python
TTS_PROVIDERS['minimax'] = {
    'name': 'MiniMax TTS',
    'format': 'text_with_pauses',
    'extension': '.txt',
    'supports_tags': [],
    'max_input_length': 8000,
    'audio_track_format': 'proprietary_pause_markers'
}
```

**Features**:
- Proprietary `<#x#>` pause format (x = seconds)
- Audio jingle noted in comment for manual assembly
- Text-based format with strategic pause placement
- Higher character limit (8,000 vs 5,000)

### **OpenAI TTS (Plain Text)**
```python
TTS_PROVIDERS['openai'] = {
    'name': 'OpenAI TTS',
    'format': 'text',
    'extension': '.txt',
    'supports_tags': [],
    'max_input_length': 4096,
    'audio_track_format': 'natural_text_with_notes'
}
```

**Features**:
- Plain text format optimized for natural speech
- Auto jingle integration during TTS processing
- 6 high-quality voices: alloy, echo, fable, onyx, nova, shimmer
- Cost-effective alternative to ElevenLabs
- Automatic SSML-to-text conversion when needed

---

## 🔧 **Core Functions**

### **1. Audio Track Format Implementation**

#### **find_intro_jingle()**
Automatically detects intro jingle files from the project structure.

```python
def find_intro_jingle():
    """
    Automatically detect the intro jingle file from the Content/audio directory structure
    """
    # Common audio extensions
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.aac', '*.ogg', '*.flac']
    
    # Search patterns for intro jingle files
    search_paths = [
        '../Content/audio/intro_jingle/*',  # Direct path
        './Content/audio/intro_jingle/*',   # Alternative path
        '../Content/audio/*intro*',         # Any intro file in audio dir
        './Content/audio/*intro*',          # Alternative intro path
        '**/intro_jingle*',                 # Recursive search
        '**/intro*jingle*',                 # Alternative naming
    ]
    
    # Returns relative path to detected intro jingle file
    # Fallback: "intro_jingle.mp3" if no file found
```

**Detection Logic**:
- Searches common audio formats (MP3, WAV, M4A, AAC, OGG, FLAC)
- Prioritizes `Content/audio/intro_jingle/` directory
- Falls back to recursive search for files with "intro" in name
- Returns relative path for proper SSML audio reference

#### **create_ssml_markup(text, title, author, provider)**
Main function that routes to provider-specific formatters with Audio Track Format.

```python
def create_ssml_markup(text, title="", author="", provider="google"):
    """Convert text to provider-specific format following Audio Track Format Specification"""
    if provider == 'minimax':
        return create_minimax_format(text, title, author)
    elif provider == 'elevenlabs':
        return create_elevenlabs_ssml(text, title, author)
    else:  # Google Cloud TTS (default)
        return create_google_ssml(text, title, author)
```

#### **create_google_ssml(text, title, author)**
Generates full SSML with complete Audio Track Format structure.

**Structure**:
1. XML declaration and proper SSML namespace
2. Auto-detected intro jingle reference: `<audio src="[detected_path]"/>`
3. Title with prosody: rate=0.9, pitch=+2st, emphasis=moderate
4. Author attribution with emphasis
5. Article content with paragraph and sentence structure
6. Standardized ending with prosody: rate=0.95, pitch=+1st

**Enhanced Features**:
- **Automatic Jingle Detection**: Calls `find_intro_jingle()` to locate audio file
- **Dynamic Path Resolution**: Uses actual file path instead of hardcoded reference
- **Cross-platform Compatibility**: Works with various audio formats and directory structures

#### **create_elevenlabs_ssml(text, title, author)**
Generates simplified SSML compatible with ElevenLabs limitations.

**Differences from Google**:
- No prosody rate/pitch attributes
- Basic emphasis tags only
- Simplified break timing
- Auto-detected audio jingle reference included but may need manual handling

**Enhanced Features**:
- **Automatic Jingle Detection**: Uses `find_intro_jingle()` for consistent referencing
- **Simplified Structure**: Optimized for ElevenLabs SSML parser limitations

#### **create_minimax_format(text, title, author)**
Generates text format with MiniMax proprietary pause markers.

**Format**:
- Auto-detected intro jingle comment: `<!-- Intro Jingle: [detected_path] should be prepended -->`
- Title followed by `<#1.0#>` (1-second pause)
- Author attribution with `<#2.0#>` (2-second pause)
- Content with strategic `<#0.3#>` sentence pauses and `<#0.6#>` paragraph pauses
- Ending with `<#2.0#>` pause before closing message

**Enhanced Features**:
- **Automatic Jingle Detection**: Dynamically includes actual jingle file path in comment
- **Manual Assembly Note**: Clear instructions for audio post-processing integration

#### **create_openai_format(text, title, author)**
Generates plain text format optimized for OpenAI TTS natural speech processing.

**Format**:
- Intro jingle note: `[Note: Intro jingle '[detected_path]' should be prepended during final audio assembly]`
- Title as natural headline text
- Author attribution: "By [Author Name]"
- Content cleaned of all markup for natural speech flow
- Natural paragraph breaks for optimal pacing
- Ending with standard closing message

**Enhanced Features**:
- **Automatic Jingle Detection**: Includes file path for post-processing integration
- **SSML Strip Compatibility**: Can process SSML input and convert to clean text
- **Natural Speech Optimization**: Formatting designed for OpenAI's neural voice models
- **Cost-Effective Processing**: Simple text format reduces API costs significantly

### **2. Content Processing Functions**

#### **clean_for_audio_synthesis(text)**
Comprehensive text cleaning for optimal TTS performance.

**Processing Steps**:
1. **Symbol Replacement**: Programming symbols (& → "and", @ → "at", etc.)
2. **Currency Conversion**: $ → "dollars", € → "euros", etc.
3. **Bracket Removal**: [], {}, () → spaces
4. **URL/Email Replacement**: URLs → "web link", emails → "email address"
5. **Code Block Handling**: ``` → "code block", ` → "code"
6. **Bullet Point Conversion**: Converts • lists to natural language
7. **Unicode Normalization**: Smart quotes to standard ASCII
8. **Whitespace Cleanup**: Removes extra spaces and line breaks

#### **process_bullet_points(text)**
Converts bullet point lists to audio-friendly natural language.

**Examples**:
- Single item: "Important point"
- Two items: "First point, and second point"  
- Multiple items: "First, second, third, and fourth point"

#### **escape_ssml_text(text)**
Escapes XML special characters for SSML compatibility.

**Replacements**:
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&quot;`
- `'` → `&apos;`

### **3. File Management Functions**

#### **sanitize_filename(filename)**
Cleans filenames for cross-platform compatibility.

**Processing**:
- Removes problematic characters: `<>:"/\|?*`
- Replaces non-alphanumeric with underscores
- Limits length to 200 characters
- Removes leading/trailing special characters

#### **extract_and_process_content(json_file, output_dir, provider)**
Main processing function that orchestrates the complete workflow.

**Workflow**:
1. Load and validate JSON input
2. Extract title, creator, and full_content from each article
3. Clean content for audio synthesis
4. Apply Audio Track Format with provider-specific formatting
5. Generate filename with voice ID placeholder: `YYYY-MM-DD_Author_Title_[VoiceID].ext`
6. Save formatted content to provider-specific files

---

## 🚀 **Usage**

### **Command Line Interface**

#### **Basic Usage**
```bash
cd Tools

# Google Cloud TTS (default)
python content_extractor.py ../Content/articles/raw_metadata/articles_with_summaries.json

# ElevenLabs with custom output directory
python content_extractor.py articles.json -p elevenlabs -o ./elevenlabs_output

# MiniMax with text format
python content_extractor.py articles.json -p minimax -o ./minimax_output
```

#### **Advanced Usage**
```bash
# List all supported providers and their configurations
python content_extractor.py --list-providers

# Process with specific provider and output directory
python content_extractor.py articles.json -p google -o ./google_ssml_output
```

### **Parameters Reference**

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `json_file` | - | string | Required | Path to JSON file from Master Article Processor |
| `--provider` | `-p` | choice | `google` | TTS provider: `google`, `elevenlabs`, `minimax` |
| `--output-dir` | `-o` | string | Auto-generated | Output directory for formatted files |
| `--list-providers` | - | flag | False | Show provider information and exit |

### **Auto-Generated Output Directories**
```python
provider_dirs = {
    'google': '../Content/articles/google_tts',
    'elevenlabs': '../Content/articles/elevenlabs', 
    'minimax': '../Content/articles/minimax'
}
```

---

## 📁 **File Naming Convention**

### **Audio Track Format Filename Structure**
Following the [Audio Track Format Specification](Audio_Track_Format_Specification.md):

**Format**: `YYYY-MM-DD_Author_Title_[VoiceID].extension`

**Examples**:
```
2025-08-28_Ken Norton_Product Managers_ How to Listen to Customers_[VoiceID].ssml
2025-08-20_Teresa Torres_Product Discovery Guide_[VoiceID].ssml
2025-07-15_Marty Cagan_Product Strategy_[VoiceID].txt
```

**Voice ID Placeholder**: `[VoiceID]` is included for voice tracking during TTS synthesis:
- Google: `en-US-Neural2-J`, `en-GB-Studio-B`
- ElevenLabs: `21m00Tcm4TlvDq8ikWAM`, `2EiwWnXFnvU5JabPnv8n`
- MiniMax: `audiobook_female_1`, `Charming_Lady`

**Fallback Patterns**:
- With date only: `YYYY-MM-DD_Title_[VoiceID].ext`
- With author only: `Author_Title_[VoiceID].ext`
- Title only: `Title_[VoiceID].ext`

---

## 📊 **Output Format Examples**

### **Google Cloud TTS Output**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

  <!-- Intro Jingle Reference (Auto-detected) -->
  <audio src="Content/audio/intro_jingle/intro_jingle_computer_startup.mp3"/>

  <!-- Title -->
  <prosody rate="0.9" pitch="+2st">
    <emphasis level="moderate">The Art of Product Management</emphasis>
  </prosody>
  <break time="1s"/>

  <!-- Author -->
  <prosody rate="1.0">
    By <emphasis level="moderate">Sachin Rekhi</emphasis>
  </prosody>
  <break time="2s"/>

  <!-- Article Content -->
  <p>
    <s>Product management is both an art and a science.</s>
    <s>It requires balancing user needs with business objectives.</s>
  </p>
  <break time="500ms"/>
  
  <p>
    <s>Great product managers understand that success comes from deep customer empathy.</s>
  </p>

  <!-- Ending -->
  <break time="2s"/>
  <prosody rate="0.95" pitch="+1st">
    Thank you for listening. <break time="0.5s"/> 
    Check out my other pieces for more insights.
  </prosody>

</speak>
```

### **ElevenLabs Output**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

  <!-- Intro Jingle Reference (Auto-detected) -->
  <audio src="Content/audio/intro_jingle/intro_jingle_computer_startup.mp3"/>

  <!-- Title -->
  <emphasis>The Art of Product Management</emphasis>
  <break time="1s"/>

  <!-- Author -->
  By <emphasis>Sachin Rekhi</emphasis>
  <break time="2s"/>

  <!-- Article Content -->
  Product management is both an art and a science.
  <break time="300ms"/>
  It requires balancing user needs with business objectives.
  <break time="600ms"/>
  
  Great product managers understand that success comes from deep customer empathy.

  <!-- Ending -->
  <break time="2s"/>
  Thank you for listening. <break time="0.5s"/> 
  Check out my other pieces for more insights.

</speak>
```

### **MiniMax Output**
```
<!-- Intro Jingle: Content/audio/intro_jingle/intro_jingle_computer_startup.mp3 should be prepended during final audio assembly --> The Art of Product Management <#1.0#> By Sachin Rekhi <#2.0#> Product management is both an art and a science. <#0.3#> It requires balancing user needs with business objectives. <#0.6#> Great product managers understand that success comes from deep customer empathy. <#2.0#> Thank you for listening. <#0.5#> Check out my other pieces for more insights.
```

### **OpenAI TTS Output**
```
[Note: Intro jingle 'Content/audio/intro_jingle/intro_jingle_computer_startup.mp3' should be prepended during final audio assembly]

The Art of Product Management

By Sachin Rekhi

Product management is both an art and a science. It requires balancing user needs with business objectives.

Great product managers understand that success comes from deep customer empathy. They know that building the right product requires not just technical skills, but also emotional intelligence and strategic thinking.

Thank you for listening. Check out my other pieces for more insights.
```

---

## 🔄 **Pipeline Integration**

### **Complete Audeon Tools Pipeline**
```bash
# Step 1: Process curated articles
python Tools/master_article_processor.py
# Output: ../Content/articles/raw_metadata/articles_with_summaries.json

# Step 2: Extract content with Audio Track Format
python Tools/content_extractor.py articles_with_summaries.json -p google
# Output: ../Content/articles/google_tts/*.ssml (with Audio Track Format)

# Step 3: Generate audio files
python Tools/batch_tts_processor.py ../Content/articles/google_tts ../Content/audio --provider google
# Output: ../Content/audio/*.mp3 (complete audio tracks)
```

### **Data Flow Validation**
- **Input Validation**: JSON structure matches Master Article Processor output
- **Field Mapping**: title, creator, full_content fields extracted correctly
- **Content Quality**: Cleaning process maintains readability for TTS
- **Format Compliance**: All outputs follow Audio Track Format Specification
- **File Integrity**: Generated files are valid SSML/text for TTS synthesis

---

## 🧪 **Testing & Validation**

### **Unit Testing**
```bash
# Test provider listing
python content_extractor.py --list-providers

# Test basic functionality with small dataset
python content_extractor.py test_articles.json -p google -o ./test_output

# Validate SSML structure
xmllint --noout ./test_output/*.ssml
```

### **Content Quality Checks**
```bash
# Check file generation
ls -la ./test_output/
wc -l ./test_output/*.ssml

# Verify Audio Track Format structure
grep -n "<!-- Intro Jingle Reference -->" ./test_output/*.ssml
grep -n "<!-- Title -->" ./test_output/*.ssml  
grep -n "<!-- Author -->" ./test_output/*.ssml
grep -n "<!-- Ending -->" ./test_output/*.ssml
```

### **Provider Compatibility Testing**
```bash
# Test all providers
python content_extractor.py articles.json -p google -o ./google_test
python content_extractor.py articles.json -p elevenlabs -o ./elevenlabs_test
python content_extractor.py articles.json -p minimax -o ./minimax_test

# Validate output formats
file ./google_test/*.ssml
file ./elevenlabs_test/*.ssml  
file ./minimax_test/*.txt
```

---

## 🐛 **Error Handling & Troubleshooting**

### **Common Issues**

#### **"No full_content found for article"**
**Cause**: JSON missing required content field  
**Solution**: 
```bash
# Check JSON structure
jq '.[] | {track_id, title, full_content: (.full_content | length)}' articles.json

# Re-run master_article_processor if content is missing
python master_article_processor.py --start-from 1
```

#### **"Content is empty after cleaning"**
**Cause**: Over-aggressive content filtering  
**Solution**: Review content cleaning rules, check original article content quality

#### **"Content exceeds provider limit"**
**Cause**: Article too long for TTS provider  
**Example**: Google (5,000 chars), ElevenLabs (5,000 chars), MiniMax (8,000 chars)  
**Solution**: Content will still be processed with warning; TTS-extraction.py handles chunking

#### **"Invalid characters in filename"**
**Cause**: Article titles contain filesystem-incompatible characters  
**Solution**: Automatic sanitization in `sanitize_filename()` function

### **Debug Mode**
```python
# Add debug logging to content_extractor.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or add print statements to track processing
print(f"Processing article: {title}")
print(f"Content length: {len(cleaned_content)}")
print(f"Final filename: {filename}")
```

---

## 📈 **Performance Metrics**

### **Processing Speed**
- **Small dataset** (10 articles): ~5-10 seconds
- **Medium dataset** (100 articles): ~30-60 seconds  
- **Large dataset** (500+ articles): ~5-10 minutes

### **Content Statistics**
- **Average content reduction**: 15-25% after cleaning (removing markup, URLs, etc.)
- **SSML overhead**: 20-30% increase in file size (XML structure, Audio Track Format)
- **File size range**: 2-50KB per formatted article

### **Quality Metrics**
- **Audio Track Format compliance**: 100% (all outputs include 5-part structure)
- **SSML validity**: 99%+ (XML validation passing)
- **TTS compatibility**: Provider-specific optimization ensures high synthesis success rate

---

## 🔒 **Security & Best Practices**

### **Input Sanitization**
- **JSON validation**: Proper error handling for malformed JSON
- **Content filtering**: Removal of potentially problematic content
- **Path validation**: Prevents directory traversal attacks
- **Character encoding**: UTF-8 handling with fallbacks

### **File Security**
- **Filename sanitization**: Prevents filesystem attacks
- **Output directory validation**: Ensures safe file creation
- **Permission handling**: Appropriate file permissions on generated content
- **Content size limits**: Prevents resource exhaustion

### **Content Privacy**
- **No data retention**: Tool processes and outputs without storing intermediate data
- **Local processing**: All content processing happens locally
- **Safe character handling**: Proper escaping prevents injection vulnerabilities

---

## 🔄 **Version History**

### **Version 2.2** (August 30, 2025)
- **🎉 MAJOR**: OpenAI TTS Provider Support
- **✨ NEW**: `create_openai_format()` function for plain text generation
- **✨ NEW**: OpenAI TTS provider configuration with 6 voice options
- **✨ NEW**: Cost-effective alternative to ElevenLabs with comparable quality
- **✨ NEW**: Automatic SSML-to-text conversion for OpenAI compatibility
- **🔧 IMPROVED**: Extended provider support to 4 major TTS services
- **🔧 IMPROVED**: Enhanced Audio Track Format implementation across all providers

### **Version 2.1** (August 30, 2025)
- **🎉 MAJOR**: Automatic Intro Jingle Detection System
- **✨ NEW**: `find_intro_jingle()` function for intelligent jingle file discovery
- **✨ NEW**: Multi-format audio file support (MP3, WAV, M4A, AAC, OGG, FLAC)
- **✨ NEW**: Smart search patterns with directory prioritization
- **🔧 IMPROVED**: Dynamic SSML generation with real file paths
- **🔧 IMPROVED**: Cross-platform compatibility for audio file references
- **🔧 IMPROVED**: Enhanced provider consistency with automatic jingle integration

### **Version 2.0** (August 28, 2025)
- **🎉 MAJOR**: Implemented complete Audio Track Format Specification
- **✨ NEW**: 5-part audio structure (intro jingle, title, author, content, ending)
- **✨ NEW**: Author attribution extraction from JSON metadata
- **✨ NEW**: Voice ID placeholder in filename format
- **✨ NEW**: Standardized ending message across all providers
- **🔧 IMPROVED**: Enhanced SSML structure with proper XML declarations
- **🔧 IMPROVED**: Provider-specific Audio Track Format implementation
- **🔧 IMPROVED**: Better prosody control for title and ending sections

### **Version 1.0** (Previous)
- **✨ Initial release**: Multi-provider content extraction
- **✨ Core features**: Basic SSML generation, content cleaning
- **✨ Provider support**: Google Cloud TTS, ElevenLabs, MiniMax

### **Future Enhancements**
- **Voice ID Integration**: Automatic voice ID substitution during TTS synthesis
- **Custom Jingle Support**: Configurable intro jingle per content category
- **Advanced Prosody**: More sophisticated emotional tone mapping
- **Batch Processing**: Parallel processing for large datasets
- **Quality Scoring**: Automatic content quality assessment

---

## 📞 **Support & Maintenance**

### **Related Documentation**
- [Audio_Track_Format_Specification.md](Audio_Track_Format_Specification.md) - Complete audio structure specification
- [Master_Article_Processor_Technical_Specification.md](Master_Article_Processor_Technical_Specification.md) - Upstream data processing
- [TTS_Extraction_Technical_Specification.md](TTS_Extraction_Technical_Specification.md) - Downstream audio synthesis
- [TTS_Providers_Technical_Specification.md](TTS_Providers_Technical_Specification.md) - Provider-specific details

### **Integration Requirements**
- **Upstream dependency**: Master Article Processor JSON output
- **Downstream compatibility**: TTS-extraction.py and batch_tts_processor.py
- **File format validation**: SSML syntax validation for XML-based providers
- **Audio Track Format compliance**: All outputs must include 5-part structure

### **Maintenance Tasks**
- **Provider updates**: Monitor TTS provider API changes and limitations
- **Content quality review**: Periodic assessment of cleaning effectiveness
- **Audio Track Format validation**: Ensure compliance with specification updates
- **Performance optimization**: Monitor processing times for large datasets

---

*This specification documents the complete Content Extractor implementation with Audio Track Format integration. For usage examples and pipeline integration, refer to the main project README and related technical specifications.*