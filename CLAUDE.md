# Audeon Tools - Claude Context

## Project Overview
Complete pipeline for converting curated product management articles into high-quality audio content using multi-provider TTS services with automatic intro jingle integration.

## Key Commands

### Main Workflow
```bash
cd Tools

# Step 1: Process articles (markdown → JSON with LLM summaries)
python master_article_processor.py

# Step 2: Convert to TTS format (JSON → SSML/text)
python content_extractor.py ../Content/articles/raw_metadata/articles_with_summaries.json -p google

# Step 3: Generate audio (SSML → audio files)
python batch_tts_processor.py "../Content/articles/ssml_format" "../Content/audio/output" --provider google
```

### Test Commands
```bash
# Test with first 3 articles
python master_article_processor.py --limit 3

# Without LLM (faster)
python master_article_processor.py --no-llm
```

## Project Structure
- `Tools/` - Main processing scripts
- `Content/` - Input/output content and generated files
- `audeon_documentation/` - Technical specifications
- `archive/` - Legacy code (archived)

## Core Tools
1. **master_article_processor.py** - Main pipeline (markdown → JSON)
2. **content_extractor.py** - Format converter (JSON → TTS formats) with auto intro jingle detection
3. **TTS-extraction.py** - Audio generation engine
4. **batch_tts_processor.py** - Batch audio processing

## Environment Setup
Required: `Tools/.env` with API keys:
- GOOGLE_TTS_API_KEY
- ELEVENLABS_API_KEY
- OPENAI_API_KEY
- MINIMAX_API_KEY

Optional: Ollama for LLM summaries (`ollama serve`)

## Supported TTS Providers
- Google TTS (SSML)
- ElevenLabs 
- OpenAI TTS (6 voices: alloy, echo, fable, onyx, nova, shimmer)
- MiniMax

## Data Flow
Input markdown → Scraping → LLM summaries → JSON → TTS format (with auto intro jingle) → Audio files

## Audio Structure
All generated content follows the 5-part Audio Track Format:
1. **Intro Jingle** (auto-detected from Content/audio/intro_jingle/)
2. **Title Announcement** (with prosody and emphasis)
3. **Author Attribution** (extracted from JSON metadata)
4. **Article Content** (cleaned and formatted)
5. **Standardized Ending** (consistent closing message)

## Coding Conventions
- Python scripts in Tools/ directory
- JSON metadata in Content/articles/raw_metadata/
- Audio output in Content/audio/output/
- Progress saving and resumption supported