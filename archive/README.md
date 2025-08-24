# Archive - Legacy Scrapers and Updaters

This archive contains legacy scraping and updating scripts that have been consolidated into the **master_article_processor.py**.

## Why These Were Archived

These scripts were created across multiple sessions and contained overlapping functionality, creating maintenance complexity and confusion about which tool to use. They have been replaced by a single, comprehensive **Tools/master_article_processor.py**.

## Archive Structure

### `/legacy_scrapers/` - Content Scraping Scripts
- `comprehensive_scraper.py` - Hybrid scraper with batch content + Firecrawl
- `batch_firecrawl_scraper.py` - Simple Firecrawl organization tool  
- `firecrawl_content_updater.py` - Firecrawl MCP framework
- `firecrawl_updater.py` - Basic Firecrawl utility
- `process_with_mcp.py` - MCP integration helper
- `scrape_all_articles.py` - Basic scraping framework
- `mindtheproduct_scraper.py` - **Most advanced scraper** (foundation for master processor)
- `fix_content_cleaning.py` - Advanced TTS text cleaning
- `run_pipeline.py` - Complete pipeline orchestration
- `process_articles.py` - **Original markdown processor** (basic JSON creation only)

### `/legacy_updaters/` - Content Update Scripts  
- `batch_update_all_content.py` - Hard-coded content updates
- `batch_update_articles.py` - Sample content with image extraction
- `batch_update_remaining.py` - Gap analysis utility
- `update_missing_content.py` - MindTheProduct-specific updater
- `update_batch_*.py` - Various one-off batch processors

## Key Features Consolidated into Master Processor

**Best Features Preserved:**
- **Advanced scraping** (Selenium + BeautifulSoup hybrid from mindtheproduct_scraper.py)
- **LLM summarization** (Ollama integration for rich descriptions)
- **Content cleaning** (TTS-optimized from fix_content_cleaning.py)
- **Image extraction** (Medium image handling from comprehensive_scraper.py)
- **Progress saving** (Every 5 articles)
- **Multi-provider support** (Framework from run_pipeline.py)

## Migration Notes

**Old Workflow:**
1. `process_articles.py` → Basic JSON with simple descriptions
2. Various scrapers → Populate `full_content` 
3. Manual summary enhancement

**New Workflow:**
1. `master_article_processor.py` → Complete pipeline with LLM summaries

## Usage

**Replace all legacy workflows with:**
```bash
cd Tools
python master_article_processor.py
```

**Key advantages:**
- Single source of truth
- No confusion about which scraper to use
- Rich LLM-generated summaries (not basic descriptions)
- Exact JSON format compatibility
- All best features consolidated

---
*Archived on August 22, 2025 - Consolidated into master_article_processor.py*