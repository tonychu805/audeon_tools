# Audeon Tools Documentation

This folder contains technical documentation and specifications for the Audeon MVP project.

## 📁 Documents

### [Master_Article_Processor_Technical_Specification.md](./Master_Article_Processor_Technical_Specification.md) ⭐ **CORE**
Complete technical documentation for the primary content processing pipeline:
- **Complete Pipeline**: Markdown parsing, content scraping, LLM enhancement, metadata generation
- **Multi-Method Scraping**: Firecrawl, Requests+BeautifulSoup, Selenium fallback strategies
- **LLM Integration**: Ollama setup, prompt engineering, summary generation
- **Content Processing**: Audio-optimized cleaning, symbol replacement, structure preservation
- **API Reference**: Complete parameter documentation and integration examples

### [TTS_Providers_Technical_Specification.md](./TTS_Providers_Technical_Specification.md)
Comprehensive technical specification for Text-to-Speech providers including:
- **Google Cloud Text-to-Speech**: Full SSML support, 220+ voices, enterprise features
- **ElevenLabs**: Voice cloning, ultra-low latency, 32 languages  
- **MiniMax TTS**: Emotion control, proprietary formatting, multilingual support

Contains API parameters, voice lists, integration examples, and best practices.

### [TTS_Extraction_Technical_Specification.md](./TTS_Extraction_Technical_Specification.md)
Complete technical documentation for the TTS-extraction audio generation tool:
- **Multi-Provider Support**: Google Cloud TTS, ElevenLabs, MiniMax integration
- **Advanced Features**: Large content chunking, multi-voice processing, audio combination
- **Usage Examples**: CLI and Python API usage with all providers
- **Implementation Guide**: Complete code examples and integration patterns

### [SSML_Best_Practices_Guide.md](./SSML_Best_Practices_Guide.md) ⭐ **NEW**
Comprehensive SSML (Speech Synthesis Markup Language) best practices guide:
- **Provider-Specific Guidelines**: Google Cloud TTS, ElevenLabs formatting requirements
- **Common Mistakes & Fixes**: Text cleaning, structure problems, compatibility issues
- **Audio Quality Optimization**: Pause timing, emphasis patterns, prosody guidelines  
- **Testing & Validation**: SSML validation scripts and quality testing procedures
- **Quick Reference**: Cheat sheets and compatibility matrix for all providers

---

## 📝 Document Types

- **Technical Specifications**: Detailed API documentation and integration guides
- **Configuration Guides**: Setup and configuration instructions  
- **Best Practices**: Recommendations and optimization tips
- **API References**: Complete parameter and endpoint documentation

## 🔄 Updates

Documents are maintained alongside code changes and updated with new provider features and API changes.

---

*For questions about documentation, refer to the specific document or check the main project README.*