# Audeon Tools - Product Management Audiobook Content Pipeline

Complete pipeline for converting curated product management articles into high-quality audio content.

## 🎯 **Master Workflow**

**Complete Pipeline**: Curated markdown list → High-quality audio files

### **Prerequisites**
```bash
# 1. Setup API keys in Tools/.env
GOOGLE_TTS_API_KEY=your_google_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# 2. Optional: LLM for rich summaries
brew install ollama && ollama pull llama3.2 && ollama serve
```

### **3-Step Process**
```bash
cd Tools

# Step 1: Process Articles (markdown → rich JSON with LLM summaries)
python master_article_processor.py

# Step 2: Convert to TTS Format (JSON → provider-specific SSML/text)
python content_extractor.py ../Content/articles/raw_metadata/articles_with_summaries.json -p google

# Step 3: Generate Audio (SSML → high-quality audio files)
python batch_tts_processor.py "../Content/articles/ssml_format" "../Content/audio/output" --provider google
```

### **Key Features**
- 🧠 **LLM-generated summaries** (replaces basic descriptions)
- 🎭 **Multi-voice SSML support** (different voices per section)  
- 🔄 **Multi-provider flexibility** (Google, ElevenLabs, MiniMax)
- 📏 **Automatic content chunking** (handles large articles)
- 💾 **Progress saving & resumption** (can restart from any point)

### **Quick Options**
```bash
# Test mode (first 3 articles)
python master_article_processor.py --limit 3

# Without LLM (faster, basic summaries)  
python master_article_processor.py --no-llm

# Different providers
python content_extractor.py articles.json -p elevenlabs
python batch_tts_processor.py input_dir output_dir --provider minimax
```

## 📁 **Repository Structure**

```
audeon_tools/
├── Tools/                          # Main processing tools
│   ├── master_article_processor.py # 🎯 MAIN: Complete article pipeline
│   ├── content_extractor.py        # Convert to TTS-ready formats
│   ├── TTS-extraction.py           # Core TTS engine
│   └── batch_tts_processor.py      # Batch audio generation
├── Content/                        # Content and data
│   ├── articles/                   # Article content and metadata
│   └── audio/                      # Generated audio files
├── audeon_documentation/          # Technical specifications
└── archive/                        # Legacy scripts (archived)
```

## 🚀 **Key Tools**

### **master_article_processor.py** - Main Content Processor
Complete pipeline: markdown → scraping → LLM summaries → JSON

**Features:**
- Hybrid scraping (Firecrawl → Requests → Selenium)
- LLM summary generation (Ollama)
- Advanced content cleaning (TTS-optimized)
- Smart image extraction
- Progress saving & resumption

**Usage:**
```bash
# Process all articles with rich summaries
python master_article_processor.py

# Test mode (first 3 articles)
python master_article_processor.py --limit 3

# Resume from article 10
python master_article_processor.py --start-from 10

# Without LLM (faster)
python master_article_processor.py --no-llm
```

### **content_extractor.py** - TTS Format Converter
Converts articles to provider-specific formats (Google TTS, ElevenLabs, MiniMax).

**Usage:**
```bash
# Google TTS SSML format
python content_extractor.py articles.json -p google

# ElevenLabs format
python content_extractor.py articles.json -p elevenlabs

# MiniMax text format
python content_extractor.py articles.json -p minimax
```

### **TTS-extraction.py** - Audio Generation Engine
Multi-provider TTS with SSML support, voice switching, and large content handling.

**Usage:**
```bash
# Single file
python TTS-extraction.py -f input.ssml -o output.mp3 --provider google

# With specific voice
python TTS-extraction.py -f input.txt -o output.mp3 --provider elevenlabs --voice "Rachel"
```

### **batch_tts_processor.py** - Batch Audio Generation
Process entire directories of SSML files into audio.

**Usage:**
```bash
# Process all SSML files
python batch_tts_processor.py "../Content/articles/ssml_format" "../Content/audio/output" --provider google
```

## ⚙️ **Configuration**

### **Required API Keys** (in `Tools/.env`)
```bash
GOOGLE_TTS_API_KEY=your_google_key
ELEVENLABS_API_KEY=your_elevenlabs_key  
MINIMAX_API_KEY=your_minimax_key
```

### **LLM Setup** (Optional - for enhanced summaries)
```bash
# Install Ollama
brew install ollama

# Pull model
ollama pull llama3.2

# Run Ollama server
ollama serve
```

## 📊 **Data Flow**

1. **Input**: `Content/articles/raw/Curated Content List for Audiobook App.markdown`
2. **Processing**: `master_article_processor.py` → Rich content + LLM summaries
3. **Output**: `Content/articles/raw_metadata/articles_with_summaries.json`
4. **Conversion**: `content_extractor.py` → Provider-specific formats
5. **Audio**: `batch_tts_processor.py` → High-quality audio files

## 🗂️ **Archive**

Legacy scrapers and updaters have been consolidated. See `archive/README.md` for details on archived functionality.

## 🎵 **Audio Quality Features**

- **Multi-voice SSML support** (different voices per section)
- **Automatic content chunking** (handles large articles)
- **Audio-optimized text cleaning** (removes navigation, fixes symbols)
- **Smart pause insertion** (natural speech flow)
- **Multiple providers** (Google, ElevenLabs, MiniMax)

## 📚 **Detailed Documentation**

For advanced configurations and technical specifications:
- **[Tools/README.md](Tools/README.md)** - Detailed tool usage and options
- **[audeon_documentation/](audeon_documentation/)** - Technical specifications and API details
- **[archive/README.md](archive/README.md)** - Legacy code and migration notes

---

**Master Workflow**: Prerequisites → 3 steps → Audio files ✨