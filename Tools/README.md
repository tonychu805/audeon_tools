# Audeon Tools - Core Processing Tools

Essential tools for the complete article-to-audio pipeline.

## 🎯 **Core Tools** (Main Workflow)

### 1. **master_article_processor.py** - Primary Content Processor
**Purpose**: Complete pipeline from curated markdown to rich article JSON
**Replaces**: All legacy scrapers (see archive/)

**Features:**
- Hybrid scraping (Firecrawl → Requests → Selenium fallback)
- LLM summary generation using Ollama
- Advanced content cleaning for audio
- Smart image extraction with dimensions
- Progress saving and resumption
- Gender detection
- Exact JSON format compatibility

**Usage:**
```bash
# Process all articles with LLM summaries
python master_article_processor.py

# Test mode (first 3 articles)
python master_article_processor.py --limit 3

# Without LLM (faster processing)
python master_article_processor.py --no-llm

# Resume from specific article
python master_article_processor.py --start-from 10
```

**Output**: `articles_with_summaries.json` with enhanced summaries

---

### 2. **content_extractor.py** - Multi-Provider Format Converter
**Purpose**: Convert articles to TTS provider-specific formats

**Supported Providers:**
- **Google Cloud TTS**: Full SSML with complex markup
- **ElevenLabs**: Limited SSML with emphasis/breaks
- **MiniMax**: Text with proprietary pause markers `<#x#>`

**Features:**
- Provider-specific optimizations
- Audio-friendly text cleaning
- Symbol replacement for speech
- Bullet point conversion to natural language
- SSML structure generation

**Usage:**
```bash
# Google TTS (SSML)
python content_extractor.py articles.json -p google -o ./google_output

# ElevenLabs (Limited SSML)
python content_extractor.py articles.json -p elevenlabs -o ./elevenlabs_output

# MiniMax (Text + Pauses)
python content_extractor.py articles.json -p minimax -o ./minimax_output

# List provider info
python content_extractor.py --list-providers
```

**Output**: Provider-specific files ready for TTS

---

### 3. **TTS-extraction.py** - Core TTS Engine
**Purpose**: Convert text/SSML to high-quality audio

**Features:**
- Multi-provider support (Google, ElevenLabs, MiniMax)
- SSML support with voice switching
- Automatic content chunking for large files
- Audio segment combination using ffmpeg
- Multi-voice content handling

**Usage:**
```bash
# Single file conversion
python TTS-extraction.py -f input.ssml -o output.mp3 --provider google

# With specific voice
python TTS-extraction.py -f input.txt -o output.mp3 --provider elevenlabs --voice "Rachel"

# Play directly (no output file)
python TTS-extraction.py -t "Hello world" --provider google
```

**Requirements**: API keys in `.env` file

---

### 4. **batch_tts_processor.py** - Batch Audio Generation
**Purpose**: Process entire directories of content files into audio

**Features:**
- Recursive directory processing
- Maintains directory structure in output
- Provider-specific processing
- Progress tracking and error reporting
- Automatic file naming

**Usage:**
```bash
# Process all SSML files in directory
python batch_tts_processor.py "../Content/articles/ssml_format" "../Content/audio/output" --provider google

# Process with specific voice
python batch_tts_processor.py input_dir output_dir --provider elevenlabs --voice "Rachel"

# Process with custom format
python batch_tts_processor.py input_dir output_dir --provider minimax --format MP3
```

**Output**: Directory tree of audio files

---

## 🔧 **Setup Requirements**

### **Python Dependencies**
```bash
pip install -r requirements.txt
```

### **API Keys** (create `.env` file)
```bash
GOOGLE_TTS_API_KEY=your_google_key
ELEVENLABS_API_KEY=your_elevenlabs_key
MINIMAX_API_KEY=your_minimax_key
```

### **LLM Setup** (for enhanced summaries)
```bash
# Install Ollama
brew install ollama

# Pull model
ollama pull llama3.2

# Start server
ollama serve
```

### **System Dependencies**
- **ffmpeg** (for audio combining): `brew install ffmpeg`
- **Chrome/Chromium** (for Selenium fallback scraping)

---

## 📋 **Complete Workflow**

```bash
# 1. Process articles (markdown → rich JSON)
python master_article_processor.py

# 2. Convert to TTS format
python content_extractor.py ../Content/articles/raw_metadata/articles_with_summaries.json -p google

# 3. Generate audio files
python batch_tts_processor.py "../Content/articles/ssml_format" "../Content/audio/output" --provider google
```

---

## 📁 **Archive**

Moved to `../archive/tools_archive/`:

### **Utilities** (Specialized tools)
- `add_gender_labels.py` - Gender detection (now integrated in master processor)
- `fixed_ssml_chunker.py` - SSML chunking (now in TTS-extraction.py)
- `minimax_voice_discovery.py` - Voice discovery utility
- `parse_elevenlabs_voices.py` - Voice parsing utility

### **Experimental** (Alternative implementations)
- `batch_audio_generator.py` - Alternative batch processor
- `cached_tts_wrapper.py` - Caching wrapper
- `parallel_content_extractor.py` - Parallel processing version

### **Voice Configs** (Configuration files)
- `TTS Library-voices.txt` - Voice listings
- `elevenlabs_shared_voices.json` - ElevenLabs voice data
- `track_list_template.json` - Template files

### **Test Files**
- Various test files and outputs

---

**Core Pipeline**: `master_article_processor.py` → `content_extractor.py` → `batch_tts_processor.py` → Audio files