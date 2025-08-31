# TTS Providers Technical Specification

**Version**: 1.0  
**Date**: 2025-01-21  
**Document**: Multi-Provider Text-to-Speech API Specification

---

## Table of Contents

1. [Google Cloud Text-to-Speech](#google-cloud-text-to-speech)
2. [ElevenLabs](#elevenlabs)
3. [MiniMax TTS](#minimax-tts)
4. [Provider Comparison Matrix](#provider-comparison-matrix)
5. [Integration Examples](#integration-examples)

---

## Google Cloud Text-to-Speech

### Overview
Google Cloud Text-to-Speech provides advanced neural text-to-speech capabilities with full SSML support and extensive voice options.

### API Endpoints
- **Base URL**: `https://texttospeech.googleapis.com/v1`
- **List Voices**: `GET /voices`
- **Synthesize Speech**: `POST /text:synthesize`

### Voice Parameters

#### Voice Selection
```json
{
  "voice": {
    "languageCode": "en-US",
    "name": "en-US-Studio-O",
    "ssmlGender": "NEUTRAL|MALE|FEMALE"
  }
}
```

#### Audio Configuration
```json
{
  "audioConfig": {
    "audioEncoding": "MP3|LINEAR16|OGG_OPUS|MULAW|ALAW",
    "speakingRate": 0.25-4.0,
    "pitch": -20.0-20.0,
    "volumeGainDb": -96.0-16.0,
    "sampleRateHertz": 8000-48000,
    "effectsProfileId": ["telephony-class-application"]
  }
}
```

### Voice Types & Capabilities

#### Studio Voices
- **Quality**: Highest quality, most expressive
- **SSML Support**: Limited (no `<mark>`, `<emphasis>`, `<prosody pitch>`, `<lang>`)
- **Input Limit**: 5,000 bytes
- **Languages**: 10+ languages
- **Example**: `en-US-Studio-O`, `en-US-Studio-Q`

#### Neural2 Voices
- **Quality**: High quality with style support
- **SSML Support**: Full SSML support including styles
- **Input Limit**: 5,000 characters
- **Languages**: 40+ languages
- **Example**: `en-US-Neural2-A`, `en-US-Neural2-C`

#### Standard Voices
- **Quality**: Good quality, cost-effective
- **SSML Support**: Full SSML support
- **Input Limit**: 5,000 characters
- **Languages**: 220+ voices across 40+ languages
- **Example**: `en-US-Standard-A`, `en-US-Standard-B`

#### WaveNet Voices
- **Quality**: High quality neural voices
- **SSML Support**: Full SSML support
- **Input Limit**: 5,000 characters
- **Languages**: 30+ languages
- **Example**: `en-US-Wavenet-A`, `en-US-Wavenet-B`

#### Journey Voices
- **Quality**: Optimized for longer content
- **SSML Support**: Full SSML support
- **Input Limit**: 1 million characters (Long Audio Synthesis)
- **Languages**: English only
- **Example**: `en-US-Journey-D`, `en-US-Journey-F`

### SSML Support (2025 Updated)

#### Supported SSML Tags
```xml
<speak>          <!-- Root element -->
<break>          <!-- Pauses -->
<emphasis>       <!-- Text emphasis -->
<p>              <!-- Paragraphs -->
<s>              <!-- Sentences -->
<prosody>        <!-- Speech properties -->
<say-as>         <!-- Text interpretation -->
<phoneme>        <!-- Pronunciation (Beta) -->
<mark>           <!-- Markers (Beta) -->
<lang>           <!-- Language switching (Beta) -->
<voice>          <!-- Voice switching (Beta) -->
```

#### SSML Examples
```xml
<speak>
  <emphasis level="strong">Important announcement:</emphasis>
  <break time="1s"/>
  <prosody rate="slow" pitch="+2st">
    The meeting is scheduled for tomorrow.
  </prosody>
  <break time="500ms"/>
  <say-as interpret-as="date" format="mdy">12/25/2025</say-as>
</speak>
```

### Pricing (Approximate)
- **Standard**: $4.00 per 1M characters
- **WaveNet**: $16.00 per 1M characters
- **Neural2**: $16.00 per 1M characters
- **Studio**: $160.00 per 1M characters
- **Journey**: $45.00 per 1M characters

---

## ElevenLabs

### Overview
ElevenLabs provides state-of-the-art AI voice synthesis with emotional expressiveness and voice cloning capabilities.

### API Endpoints
- **Base URL**: `https://api.elevenlabs.io/v1`
- **List Voices**: `GET /voices`
- **Text to Speech**: `POST /text-to-speech/{voice_id}`
- **Voice Settings**: `GET /voices/{voice_id}/settings`

### Voice Parameters

#### Basic Parameters
```json
{
  "text": "Your text here",
  "model_id": "eleven_flash_v2_5",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5,
    "style": 0.0,
    "use_speaker_boost": true
  }
}
```

#### Advanced Parameters
```json
{
  "pronunciation_dictionary_locators": [
    {
      "pronunciation_dictionary_id": "string",
      "version_id": "string"
    }
  ],
  "seed": 123,
  "previous_text": "Context for better synthesis",
  "next_text": "Following text context",
  "previous_request_ids": ["request_id_1"],
  "next_request_ids": ["request_id_2"]
}
```

### Available Models (2025)

#### Eleven Flash v2.5
- **Latency**: ~75ms (Ultra-low)
- **Quality**: High
- **Languages**: 32 languages
- **Use Case**: Real-time applications, conversational AI
- **Cost**: Most cost-effective
- **Model ID**: `eleven_flash_v2_5`

#### Eleven Turbo v2.5
- **Latency**: Low (~150ms)
- **Quality**: Higher than Flash
- **Languages**: 32 languages
- **Use Case**: Balance of quality and speed
- **Model ID**: `eleven_turbo_v2_5`

#### Eleven v3 (Alpha)
- **Latency**: Higher
- **Quality**: Most expressive with emotional depth
- **Languages**: Limited
- **Use Case**: Premium applications requiring maximum expressiveness
- **Model ID**: `eleven_v3`

#### Legacy Models
- `eleven_flash_v2`
- `eleven_multilingual_v2`
- `eleven_turbo_v2`

### Voice Types

#### Pre-built Voices
- **Count**: 120+ voices
- **Languages**: 32 languages
- **Characteristics**: Professional, diverse accents and styles
- **Access**: Available to all users

#### Instant Voice Cloning
- **Input**: 1-5 minutes of audio
- **Quality**: Good for most use cases
- **Speed**: Immediate availability
- **Cost**: Included in subscription

#### Professional Voice Cloning
- **Input**: 3+ hours of high-quality audio
- **Quality**: Highest fidelity
- **Processing**: 6-10 hours
- **Cost**: Premium feature

### SSML Support (Limited)

#### Supported Tags
```xml
<speak>          <!-- Root element -->
<break>          <!-- Pauses -->
<emphasis>       <!-- Simple emphasis -->
<prosody>        <!-- Rate, pitch, volume -->
<phoneme>        <!-- Pronunciation (select models only) -->
```

#### Model Compatibility
- **Phoneme Support**: Eleven Flash v2, Eleven Turbo v2, Eleven English v1 only
- **Other Models**: Basic SSML tags only

#### SSML Example
```xml
<speak>
  <emphasis>Welcome</emphasis>
  <break time="1s"/>
  <prosody rate="0.9">
    This is a demonstration of ElevenLabs SSML support.
  </prosody>
</speak>
```

### Language Support (32 Languages)
- **English**: USA, UK, Australia, Canada
- **Asian**: Japanese, Chinese, Hindi, Korean, Indonesian, Filipino, Tamil
- **European**: German, French, Italian, Spanish, Portuguese, Dutch, Polish, Swedish, Bulgarian, Romanian, Czech, Greek, Finnish, Croatian, Slovak, Danish, Norwegian, Hungarian
- **Others**: Arabic (Saudi, UAE), Turkish, Malay, Ukrainian, Russian, Vietnamese

### Voice Settings Optimization

#### Stability (0.0 - 1.0)
- **Low (0.0-0.3)**: More variable, expressive
- **Medium (0.4-0.7)**: Balanced
- **High (0.8-1.0)**: Consistent, stable

#### Similarity Boost (0.0 - 1.0)
- **Low (0.0-0.3)**: More creative interpretation
- **Medium (0.4-0.7)**: Balanced
- **High (0.8-1.0)**: Closer to original voice

#### Style (0.0 - 1.0)
- **Available**: Only with v2 models
- **Effect**: Controls expressiveness and emotion

### Pricing (Approximate)
- **Starter**: $5/month - 30k characters
- **Creator**: $22/month - 100k characters
- **Pro**: $99/month - 500k characters
- **Scale**: $330/month - 2M characters

---

## MiniMax TTS

### Overview
MiniMax TTS provides high-quality speech synthesis with extensive emotion control and multilingual support using proprietary formatting.

### API Endpoints
- **Base URL**: `https://api.minimax.chat/v1`
- **Text to Speech**: `POST /t2a_pro`
- **Voice List**: Available through dashboard/documentation

### Voice Parameters

#### Core Parameters
```json
{
  "model": "speech-02-hd",
  "text": "Your text with <#0.5#> pause markers",
  "voice_setting": {
    "voice_id": "female-shaonv",
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0,
    "emotion": "happy"
  },
  "audio_setting": {
    "format": "mp3",
    "sample_rate": 32000,
    "bitrate": 128000,
    "channel": 1
  }
}
```

#### Advanced Parameters
```json
{
  "pronunciation_dict": {
    "tone_dict": {},
    "word_dict": {}
  },
  "language_boost": "auto",
  "english_normalization": true,
  "stream": false
}
```

### Available Models

#### Speech-02-HD (Default)
- **Quality**: Highest quality
- **Features**: Emotion support, multilingual
- **Use Case**: Premium applications
- **Model ID**: `speech-02-hd`

#### Speech-02-Turbo
- **Quality**: High quality
- **Speed**: Faster than HD
- **Features**: Emotion support, multilingual
- **Model ID**: `speech-02-turbo`

#### Speech-01-HD
- **Quality**: High quality (legacy)
- **Features**: Basic emotion support
- **Model ID**: `speech-01-hd`

#### Speech-01-Turbo
- **Quality**: Good quality (legacy)
- **Speed**: Fast processing
- **Model ID**: `speech-01-turbo`

### Emotion Control

#### Available Emotions
```json
{
  "emotion": "happy|sad|angry|fearful|disgusted|surprised|neutral"
}
```

#### Emotion Compatibility
- **Support**: speech-02-hd, speech-02-turbo, speech-01-turbo, speech-01-hd
- **Default**: "happy"
- **Auto-Detection**: Speech-02 models analyze text for emotional cues

### Voice Settings

#### Voice ID Options
- **System Voices**: 100+ pre-built voices
- **Cloned Voices**: Custom voice cloning supported
- **Categories**: Male, female, various ages and styles
- **Languages**: 32 languages supported

#### Audio Quality Settings
```json
{
  "speed": 0.1-3.0,      // Speech rate
  "vol": 0.1-2.0,        // Volume level
  "pitch": -12-12,       // Pitch adjustment (semitones)
  "sample_rate": [8000, 16000, 22050, 24000, 32000, 44100],
  "bitrate": [64000, 96000, 128000, 192000, 256000, 320000],
  "format": ["mp3", "pcm", "flac", "wav"],
  "channel": [1, 2]      // Mono or stereo
}
```

### Text Formatting (Proprietary)

#### Pause Markers
```text
"Hello <#0.5#> this adds a half-second pause <#1.0#> and this adds one second."
```

#### Pause Guidelines
- **Format**: `<#x#>` where x = seconds
- **Range**: 0.01 to 99.99 seconds
- **Usage**: Place anywhere in text for natural pauses

#### Advanced Text Processing
- **Auto-Emotion**: Speech-02 models automatically detect emotional content
- **Tone Adjustment**: Automatic pitch, rhythm adjustments based on context
- **Multilingual**: Automatic language detection and switching

### Language Support (32 Languages)
Same as ElevenLabs with additional support for:
- **Chinese**: Mandarin, Cantonese
- **Southeast Asian**: Vietnamese, Indonesian, Malay
- **European**: Full European language coverage
- **Language Boost**: Enhanced recognition for minor languages/dialects

### Input Limitations
- **Max Characters**: 8,000 per request
- **Streaming**: Supported for real-time applications
- **Batch Processing**: Multiple requests supported

### Pricing (Approximate)
- **Pay-per-use**: Based on character count
- **Enterprise**: Volume discounts available
- **Free Tier**: Limited monthly quota

---

## Provider Comparison Matrix

| Feature | Google Cloud TTS | ElevenLabs | MiniMax TTS |
|---------|------------------|------------|-------------|
| **SSML Support** | Full SSML | Limited SSML | Proprietary Format |
| **Max Input Length** | 5,000 chars (1M for Journey) | 5,000 chars | 8,000 chars |
| **Voice Count** | 220+ voices | 120+ voices | 100+ voices |
| **Languages** | 40+ languages | 32 languages | 32 languages |
| **Emotion Control** | Via SSML prosody | Voice settings | 7 emotion types |
| **Voice Cloning** | No | Yes (Instant/Pro) | Yes |
| **Latency** | Medium | Ultra-low (75ms) | Medium |
| **Streaming** | Yes | Yes | Yes |
| **Pricing Model** | Pay-per-character | Subscription | Pay-per-use |
| **Best For** | Enterprise, SSML | Real-time, Quality | Emotion, Multilingual |

---

## Integration Examples

### Content Extractor Usage with Audio Track Format

#### Complete Pipeline Integration
```bash
# Step 1: Process articles to enhanced JSON
python Tools/master_article_processor.py

# Step 2: Generate Audio Track Format content
python Tools/content_extractor.py articles_with_summaries.json -p google -o ./google_output

# Step 3: Synthesize complete audio tracks
python Tools/batch_tts_processor.py ./google_output ./audio --provider google
```

#### Provider-Specific Content Generation

#### Google Cloud TTS
```bash
python Tools/content_extractor.py articles.json -p google -o ./google_output
# Output: Full SSML with prosody control and audio jingle reference
# Files: YYYY-MM-DD_Author_Title_[VoiceID].ssml
```

#### ElevenLabs
```bash
python Tools/content_extractor.py articles.json -p elevenlabs -o ./elevenlabs_output
# Output: Simplified SSML compatible with ElevenLabs limitations  
# Files: YYYY-MM-DD_Author_Title_[VoiceID].ssml
```

#### MiniMax
```bash
python Tools/content_extractor.py articles.json -p minimax -o ./minimax_output
# Output: Text format with proprietary pause markers
# Files: YYYY-MM-DD_Author_Title_[VoiceID].txt
```

**Audio Track Format Implementation**: All providers generate content following the [Audio_Track_Format_Specification.md](Audio_Track_Format_Specification.md):

1. **Intro Jingle Reference**: 
   - Google/ElevenLabs: `<audio src="intro_jingle.mp3"/>`
   - MiniMax: Comment notation for manual assembly

2. **Title Announcement**:
   - Google: `<prosody rate="0.9" pitch="+2st"><emphasis level="moderate">Title</emphasis></prosody>`
   - ElevenLabs: `<emphasis>Title</emphasis>`  
   - MiniMax: `Title <#1.0#>`

3. **Author Attribution**:
   - Google: `<prosody rate="1.0">By <emphasis level="moderate">Author</emphasis></prosody>`
   - ElevenLabs: `By <emphasis>Author</emphasis>`
   - MiniMax: `By Author <#2.0#>`

4. **Article Content**: Provider-optimized formatting with appropriate pauses and structure

5. **Standardized Ending**:
   - Google: `<prosody rate="0.95" pitch="+1st">Thank you for listening...</prosody>`
   - ElevenLabs: `Thank you for listening... <break time="0.5s"/>`
   - MiniMax: `<#2.0#> Thank you for listening. <#0.5#> Check out my other pieces...`

### API Call Examples

#### Google Cloud TTS
```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
input_text = texttospeech.SynthesisInput(ssml=ssml_content)
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
    pitch=0.0
)
response = client.synthesize_speech(
    input=input_text, voice=voice, audio_config=audio_config
)
```

#### ElevenLabs
```python
import requests

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": api_key}
data = {
    "text": text_content,
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}
response = requests.post(url, json=data, headers=headers)
```

#### MiniMax
```python
import requests

url = "https://api.minimax.chat/v1/t2a_pro"
headers = {"Authorization": f"Bearer {api_key}"}
data = {
    "model": "speech-02-hd",
    "text": text_with_pauses,
    "voice_setting": {
        "voice_id": "female-shaonv",
        "speed": 1.0,
        "emotion": "happy"
    }
}
response = requests.post(url, json=data, headers=headers)
```

---

## Best Practices

### Google Cloud TTS
- Use Studio voices for premium quality
- Leverage Journey voices for long content
- Implement proper SSML structure with `<p>` and `<s>` tags
- Test voice selection with different content types

### ElevenLabs
- Choose Flash v2.5 for real-time applications
- Optimize voice settings per use case
- Use pronunciation dictionaries for technical terms
- Consider voice cloning for brand consistency

### MiniMax
- Utilize emotion parameters for engaging content
- Implement strategic pause markers for natural speech
- Leverage automatic emotional analysis
- Test multilingual content with language boost

---

**End of Document**

*For the latest updates and API changes, always refer to the official documentation of each provider.*