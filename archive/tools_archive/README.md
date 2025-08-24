# Tools Archive

Archived Tools directory files - moved during repository cleanup to focus on core pipeline tools.

## Archive Organization

### `/utilities/` - Specialized Utility Scripts

**`add_gender_labels.py`**
- **Purpose**: Adds gender field to articles JSON based on author names
- **Status**: ✅ **Functionality preserved** - integrated into `master_article_processor.py`
- **Original usage**: `python add_gender_labels.py` (processed articles_with_summaries.json)

**`fixed_ssml_chunker.py`** 
- **Purpose**: Advanced SSML content chunking for large files
- **Status**: ✅ **Functionality preserved** - integrated into `TTS-extraction.py`
- **Features**: Smart paragraph breaks, SSML structure preservation

**`minimax_voice_discovery.py`**
- **Purpose**: Discovery and testing of MiniMax TTS voices
- **Status**: 📦 **Archived** - specialized utility for voice exploration
- **Usage**: Voice research and testing

**`parse_elevenlabs_voices.py`**
- **Purpose**: Parse and organize ElevenLabs voice data
- **Status**: 📦 **Archived** - voice configuration utility
- **Output**: Structured voice metadata

### `/experimental/` - Alternative Implementations

**`batch_audio_generator.py`**
- **Purpose**: Alternative batch audio processing implementation  
- **Status**: 🔄 **Superseded** by `batch_tts_processor.py`
- **Differences**: Different approach to batch processing, experimental features

**`cached_tts_wrapper.py`**
- **Purpose**: Caching wrapper for TTS API calls
- **Status**: 🔄 **Experimental** - performance optimization
- **Features**: Local caching, API rate limiting, cost reduction

**`parallel_content_extractor.py`**
- **Purpose**: Multi-threaded version of content extraction
- **Status**: 🔄 **Alternative** to `content_extractor.py`
- **Features**: Parallel processing, faster large-scale extraction

### `/voice_configs/` - Configuration and Reference Files

**`TTS Library-voices.txt`**
- **Purpose**: Comprehensive list of available TTS voices across providers
- **Status**: 📚 **Reference** - voice selection guide
- **Content**: Voice names, IDs, and characteristics

**`elevenlabs_shared_voices.json`**
- **Purpose**: ElevenLabs voice configuration data
- **Status**: 📚 **Reference** - voice metadata and settings
- **Format**: JSON with voice parameters, IDs, and capabilities

**`track_list_template.json`**
- **Purpose**: Template structure for track/article JSON
- **Status**: 📚 **Reference** - schema documentation
- **Usage**: Data structure reference for development

### `/test_files/` - Test Data and Development Files

**`test.mp3`** - Audio test output
**`test.txt`** - Text test input  
**`test.tsx`** - Code test file
**`test_urls.txt`** - URL test data
**`test_master.json`** - Master processor test output

## Migration Notes

### ✅ **Features Preserved in Core Tools**

- **Gender detection** → `master_article_processor.py`
- **SSML chunking** → `TTS-extraction.py` 
- **Content extraction** → `content_extractor.py`
- **Batch processing** → `batch_tts_processor.py`

### 📦 **Archived Features Available If Needed**

- **Voice discovery utilities** - for exploring new voices
- **Caching wrappers** - for cost optimization
- **Parallel processing** - for large-scale operations
- **Alternative implementations** - for specialized use cases

### 🔄 **Experimental Features**

These tools contained experimental or alternative approaches that weren't integrated into the main pipeline but could be useful for future development or specialized use cases.

## Recovery Instructions

If you need any archived functionality:

1. **Check if integrated**: Most features are now in core tools
2. **Copy from archive**: Individual files can be moved back to Tools/
3. **Update dependencies**: May need requirements.txt updates
4. **Test compatibility**: Ensure compatibility with current data formats

---
*Archived during Tools directory cleanup - August 22, 2025*