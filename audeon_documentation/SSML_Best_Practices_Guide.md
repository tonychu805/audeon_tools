# SSML Best Practices Guide

**Version**: 1.0  
**Date**: 2025-01-21  
**Document**: Speech Synthesis Markup Language Best Practices for Multi-Provider TTS

---

## Table of Contents

1. [SSML Overview](#ssml-overview)
2. [Provider-Specific Guidelines](#provider-specific-guidelines)
3. [Best Practices by Provider](#best-practices-by-provider)
4. [Common Mistakes and Fixes](#common-mistakes-and-fixes)
5. [Audio Quality Optimization](#audio-quality-optimization)
6. [Testing and Validation](#testing-and-validation)
7. [Quick Reference](#quick-reference)

---

## SSML Overview

Speech Synthesis Markup Language (SSML) is an XML-based markup language that provides fine-grained control over speech synthesis. Different TTS providers support varying levels of SSML complexity.

### Core Concepts
- **Markup Structure**: XML-based with nested elements
- **Audio Control**: Pauses, emphasis, pronunciation, prosody
- **Content Organization**: Sentences, paragraphs, breaks
- **Provider Compatibility**: Each provider has different tag support

---

## Provider-Specific Guidelines

### Google Cloud Text-to-Speech ✅ **Full SSML Support**

#### **Supported Tags (Complete List)**
```xml
<speak>          <!-- Root element (required) -->
<p>              <!-- Paragraph -->
<s>              <!-- Sentence -->
<break>          <!-- Pause/silence -->
<emphasis>       <!-- Text emphasis with levels -->
<prosody>        <!-- Speech rate, pitch, volume -->
<say-as>         <!-- Text interpretation -->
<phoneme>        <!-- Pronunciation (Beta) -->
<mark>           <!-- Event markers (Beta) -->
<lang>           <!-- Language switching (Beta) -->
<voice>          <!-- Voice switching (Beta) -->
<par>            <!-- Parallel audio (Advanced) -->
<seq>            <!-- Sequential audio (Advanced) -->
```

#### **Recommended Structure**
```xml
<speak>
  <!-- Title with strong emphasis -->
  <emphasis level="strong">Article Title Here</emphasis>
  <break time="1s"/>
  
  <!-- First paragraph -->
  <p>
    <s>First sentence of the paragraph.</s>
    <s>Second sentence with <emphasis level="moderate">moderate emphasis</emphasis>.</s>
    <s>Third sentence with <prosody rate="0.9" pitch="+1st">slower speech and higher pitch</prosody>.</s>
  </p>
  <break time="500ms"/>
  
  <!-- Second paragraph with special elements -->
  <p>
    <s>Date example: <say-as interpret-as="date" format="mdy">12/25/2025</say-as>.</s>
    <s>Number example: <say-as interpret-as="cardinal">123</say-as> items processed.</s>
    <s>Time example: <say-as interpret-as="time" format="hms12">2:30pm</say-as>.</s>
  </p>
</speak>
```

#### **Google-Specific Features**
```xml
<!-- Voice switching (requires compatible voices) -->
<voice name="en-US-Studio-O">Narrator voice here.</voice>
<voice name="en-US-Studio-Q">Character voice here.</voice>

<!-- Advanced prosody controls -->
<prosody rate="1.2" pitch="+2st" volume="loud">
  Fast, high-pitched, loud speech.
</prosody>

<!-- Pronunciation with IPA or X-SAMPA -->
<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>
```

### ElevenLabs ⚠️ **Limited SSML Support**

#### **Supported Tags (Limited)**
```xml
<speak>          <!-- Root element (required) -->
<break>          <!-- Pause/silence -->
<emphasis>       <!-- Simple emphasis (no levels) -->
<prosody>        <!-- Basic rate control only -->
<phoneme>        <!-- Select models only (Eleven Flash v2, Turbo v2, English v1) -->
```

#### **Recommended Structure (Simple)**
```xml
<speak>
  <!-- Title with simple emphasis -->
  <emphasis>Article Title Here</emphasis>
  <break time="1s"/>
  
  <!-- Content with natural breaks -->
  First paragraph starts here with natural flow.
  <break time="300ms"/>
  Second sentence continues the thought smoothly.
  <break time="600ms"/>
  
  <!-- New paragraph -->
  Next paragraph begins here.
  <break time="400ms"/>
  Keep sentences simple and clear for best results.
  <break time="600ms"/>
  
  <!-- Use prosody sparingly -->
  <prosody rate="0.9">This text will be spoken slightly slower.</prosody>
</speak>
```

#### **ElevenLabs Limitations**
```xml
<!-- ❌ DON'T USE - Not supported -->
<p>Paragraph tags cause issues</p>
<s>Sentence tags cause issues</s>
<emphasis level="strong">Emphasis levels not supported</emphasis>
<prosody pitch="+2st">Pitch control limited</prosody>

<!-- ✅ DO USE - Supported -->
<emphasis>Simple emphasis works</emphasis>
<break time="500ms"/>
<prosody rate="0.8">Rate control works</prosody>
```

### MiniMax TTS ❌ **No SSML Support**

#### **Proprietary Format**
```text
<!-- MiniMax uses proprietary pause markers -->
Hello world <#0.5#> this adds a half-second pause.

More text here <#1.0#> with a one-second pause.

Natural speech flow with <#0.3#> short pauses <#0.6#> and longer pauses.
```

#### **Pause Guidelines**
- **Format**: `<#x#>` where x = seconds
- **Range**: 0.01 to 99.99 seconds  
- **Usage**: Insert anywhere in text for natural pauses
- **No other markup**: Plain text with pause markers only

---

## Best Practices by Provider

### Google Cloud TTS Best Practices

#### **✅ DO:**
```xml
<!-- Proper structure with nested elements -->
<speak>
  <p>
    <s>Well-structured sentences work best.</s>
    <s>Use appropriate <emphasis level="moderate">emphasis levels</emphasis>.</s>
  </p>
  <break time="500ms"/>
  
  <!-- Use say-as for better pronunciation -->
  <p>
    <s>The date is <say-as interpret-as="date" format="mdy">01/21/2025</say-as>.</s>
    <s>Processing <say-as interpret-as="cardinal">1,234</say-as> items.</s>
  </p>
</speak>

<!-- Prosody for natural speech variations -->
<prosody rate="0.95" pitch="+0.5st">
  Slightly slower with a bit higher pitch for important information.
</prosody>
```

#### **❌ DON'T:**
```xml
<!-- Poor structure without proper nesting -->
<speak>
  Random text without proper tags.
  <break time="1s"/>
  More unstructured content.
</speak>

<!-- Excessive prosody changes -->
<prosody rate="2.0" pitch="+10st" volume="x-loud">
  Extreme settings sound unnatural.
</prosody>
```

### ElevenLabs Best Practices

#### **✅ DO:**
```xml
<!-- Simple, clean structure -->
<speak>
  <emphasis>Clear title</emphasis>
  <break time="1s"/>
  
  Natural sentence flow with appropriate pauses.
  <break time="300ms"/>
  Keep it simple and readable.
  <break time="600ms"/>
  
  <prosody rate="0.9">Use prosody sparingly for effect.</prosody>
</speak>
```

#### **❌ DON'T:**
```xml
<!-- Complex nesting that ElevenLabs can't handle -->
<speak>
  <p>
    <s>Complex <emphasis level="strong">nested</emphasis> structure.</s>
  </p>
</speak>

<!-- Advanced features not supported -->
<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>
<say-as interpret-as="date">12/25/2025</say-as>
```

### MiniMax Best Practices

#### **✅ DO:**
```text
<!-- Natural text with strategic pauses -->
Welcome to our presentation. <#1.0#> Today we'll cover three main topics.

First topic introduction here. <#0.5#> This is important information. <#0.8#>

Second topic starts now. <#0.3#> Brief pause for emphasis. <#0.6#>

Final thoughts and conclusions. <#1.2#> Thank you for listening.
```

#### **❌ DON'T:**
```text
<!-- Excessive pauses disrupt flow -->
Every <#0.5#> single <#0.5#> word <#0.5#> has <#0.5#> pauses.

<!-- Inconsistent pause lengths -->
Random pauses <#3.7#> that are too long <#0.01#> or too short <#15.2#>.
```

---

## Common Mistakes and Fixes

### 1. **Text Cleaning Issues**

#### **Problem: Broken Words**
```xml
<!-- ❌ BEFORE: Poor text cleaning -->
<speak>
  The ure on you is intense to say yes.
  number number 1. Promise a new feature.
</speak>

<!-- ✅ AFTER: Proper text cleaning -->
<speak>
  The pressure on you is intense to say yes.
  <break time="300ms"/>
  Number 1. Promise a new feature.
</speak>
```

#### **Problem: Special Characters**
```xml
<!-- ❌ BEFORE: Unescaped characters -->
<speak>
  Use the < and > symbols for comparison.
  The R&D team works on AI & ML.
</speak>

<!-- ✅ AFTER: Properly escaped -->
<speak>
  Use the less than and greater than symbols for comparison.
  <break time="300ms"/>
  The R and D team works on A I and M L.
</speak>
```

### 2. **Structure Problems**

#### **Problem: Missing Root Element**
```xml
<!-- ❌ BEFORE: No <speak> wrapper -->
<emphasis>Title</emphasis>
<break time="1s"/>
Content here.

<!-- ✅ AFTER: Proper root element -->
<speak>
  <emphasis>Title</emphasis>
  <break time="1s"/>
  Content here.
</speak>
```

#### **Problem: Incorrect Nesting**
```xml
<!-- ❌ BEFORE: Invalid nesting -->
<speak>
  <p>
    Paragraph content
    <emphasis>
      <s>Sentence inside emphasis</s>
    </emphasis>
  </p>
</speak>

<!-- ✅ AFTER: Correct nesting -->
<speak>
  <p>
    <s>Paragraph content with <emphasis>proper emphasis placement</emphasis>.</s>
  </p>
</speak>
```

### 3. **Provider Compatibility Issues**

#### **Problem: Using Unsupported Tags**
```xml
<!-- ❌ ElevenLabs: Using unsupported features -->
<speak>
  <p>
    <s>This <emphasis level="strong">won't work</emphasis> properly.</s>
  </p>
</speak>

<!-- ✅ ElevenLabs: Simplified version -->
<speak>
  This <emphasis>will work</emphasis> properly.
  <break time="300ms"/>
  Keep it simple for best results.
</speak>
```

---

## Audio Quality Optimization

### 1. **Pause Timing Guidelines**

#### **Sentence Breaks**
```xml
<!-- Short pauses between sentences -->
<break time="300ms"/>    <!-- Brief pause -->
<break time="500ms"/>    <!-- Standard pause -->
<break time="800ms"/>    <!-- Longer pause -->
```

#### **Paragraph Breaks**
```xml
<!-- Medium pauses between paragraphs -->
<break time="600ms"/>    <!-- Brief paragraph break -->
<break time="1s"/>       <!-- Standard paragraph break -->
<break time="1.5s"/>     <!-- Longer paragraph break -->
```

#### **Section Breaks**
```xml
<!-- Long pauses between sections -->
<break time="1.5s"/>     <!-- Brief section break -->
<break time="2s"/>       <!-- Standard section break -->
<break time="3s"/>       <!-- Major section break -->
```

### 2. **Emphasis Patterns**

#### **Google Cloud TTS**
```xml
<!-- Graduated emphasis levels -->
<emphasis level="reduced">Less important</emphasis>
Normal text here.
<emphasis level="moderate">More important</emphasis>
<emphasis level="strong">Very important</emphasis>
```

#### **ElevenLabs**
```xml
<!-- Simple emphasis only -->
Regular text and <emphasis>important information</emphasis>.
Use sparingly for best effect.
```

### 3. **Prosody Guidelines**

#### **Speaking Rate**
```xml
<!-- Subtle rate changes work best -->
<prosody rate="0.9">Slightly slower for complex information</prosody>
<prosody rate="1.1">Slightly faster for simple content</prosody>

<!-- Avoid extreme changes -->
<prosody rate="0.5">Too slow - sounds robotic</prosody>
<prosody rate="2.0">Too fast - hard to understand</prosody>
```

#### **Pitch Variation**
```xml
<!-- Subtle pitch changes -->
<prosody pitch="+1st">Slightly higher for questions</prosody>
<prosody pitch="-1st">Slightly lower for serious topics</prosody>

<!-- Avoid extreme pitch changes -->
<prosody pitch="+10st">Too high - sounds unnatural</prosody>
<prosody pitch="-10st">Too low - sounds unnatural</prosody>
```

---

## Testing and Validation

### 1. **SSML Validation**

#### **XML Well-Formedness Check**
```python
import xml.etree.ElementTree as ET

def validate_ssml(ssml_content):
    try:
        ET.fromstring(ssml_content)
        return True, "Valid SSML"
    except ET.ParseError as e:
        return False, f"Invalid SSML: {e}"

# Example usage
ssml = "<speak>Test content</speak>"
is_valid, message = validate_ssml(ssml)
print(f"SSML Status: {message}")
```

#### **Provider-Specific Validation**
```python
def validate_for_provider(ssml_content, provider):
    """Validate SSML for specific provider"""
    
    if provider == "elevenlabs":
        # Check for unsupported tags
        unsupported = ["<p>", "<s>", 'level="']
        for tag in unsupported:
            if tag in ssml_content:
                return False, f"ElevenLabs doesn't support: {tag}"
    
    elif provider == "minimax":
        # MiniMax doesn't use SSML
        if "<speak>" in ssml_content:
            return False, "MiniMax doesn't support SSML"
    
    return True, "Valid for provider"
```

### 2. **Audio Quality Testing**

#### **Test Content Examples**
```xml
<!-- Test short content -->
<speak>
  <emphasis>Short test phrase</emphasis>
  <break time="500ms"/>
  This is a simple test.
</speak>

<!-- Test medium content with structure -->
<speak>
  <emphasis>Medium Test Content</emphasis>
  <break time="1s"/>
  
  <p>
    <s>First paragraph with normal speech.</s>
    <s>Second sentence with <emphasis>emphasis</emphasis>.</s>
  </p>
  <break time="500ms"/>
  
  <p>
    <s>Second paragraph with different pacing.</s>
    <s><prosody rate="0.9">Slightly slower delivery here.</prosody></s>
  </p>
</speak>

<!-- Test long content with breaks -->
<speak>
  <emphasis>Long Content Test</emphasis>
  <break time="1s"/>
  
  <!-- Multiple paragraphs with varied structure -->
  <!-- ... content continues ... -->
</speak>
```

### 3. **Automated Testing Script**

```python
#!/usr/bin/env python3
"""
SSML Quality Testing Script
"""
import xml.etree.ElementTree as ET
import re

def test_ssml_quality(ssml_content, provider):
    """Comprehensive SSML quality check"""
    
    issues = []
    
    # 1. XML validation
    try:
        ET.fromstring(ssml_content)
    except ET.ParseError as e:
        issues.append(f"Invalid XML: {e}")
        return issues
    
    # 2. Root element check
    if not ssml_content.strip().startswith('<speak>'):
        issues.append("Missing <speak> root element")
    
    # 3. Provider-specific checks
    if provider == "elevenlabs":
        # Check for unsupported features
        if '<p>' in ssml_content:
            issues.append("ElevenLabs: <p> tags not recommended")
        if '<s>' in ssml_content:
            issues.append("ElevenLabs: <s> tags not recommended")
        if 'level=' in ssml_content:
            issues.append("ElevenLabs: Emphasis levels not supported")
    
    # 4. Content quality checks
    if 'number number' in ssml_content.lower():
        issues.append("Text cleaning issue: 'number number' found")
    
    # 5. Break timing checks
    break_times = re.findall(r'time="([^"]+)"', ssml_content)
    for time_val in break_times:
        try:
            if time_val.endswith('ms'):
                ms = float(time_val[:-2])
                if ms > 5000:  # 5 second limit
                    issues.append(f"Break too long: {time_val}")
            elif time_val.endswith('s'):
                s = float(time_val[:-1])
                if s > 5:  # 5 second limit
                    issues.append(f"Break too long: {time_val}")
        except ValueError:
            issues.append(f"Invalid break time: {time_val}")
    
    return issues

# Example usage
if __name__ == "__main__":
    test_ssml = """
    <speak>
      <emphasis>Test Title</emphasis>
      <break time="1s"/>
      Test content here.
    </speak>
    """
    
    issues = test_ssml_quality(test_ssml, "google")
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("SSML quality check passed!")
```

---

## Quick Reference

### Google Cloud TTS Cheat Sheet
```xml
<!-- Basic structure -->
<speak>
  <p><s>Sentence here.</s></p>
  <break time="500ms"/>
</speak>

<!-- Common elements -->
<emphasis level="strong">Strong emphasis</emphasis>
<prosody rate="0.9" pitch="+1st">Modified speech</prosody>
<say-as interpret-as="date">01/21/2025</say-as>
<break time="1s"/>
```

### ElevenLabs Cheat Sheet
```xml
<!-- Simple structure -->
<speak>
  <emphasis>Title</emphasis>
  <break time="1s"/>
  Natural text flow here.
  <break time="300ms"/>
</speak>

<!-- Supported elements -->
<emphasis>Simple emphasis</emphasis>
<prosody rate="0.9">Rate control</prosody>
<break time="500ms"/>
```

### MiniMax Cheat Sheet
```text
<!-- Plain text with pauses -->
Title here <#1.0#> Main content follows.

Paragraph text <#0.5#> with strategic pauses <#0.8#> for natural flow.

Final section <#1.2#> with conclusion.
```

### Common Break Times
```xml
<!-- Sentence breaks -->
<break time="200ms"/>   <!-- Very brief -->
<break time="300ms"/>   <!-- Short -->
<break time="500ms"/>   <!-- Standard -->
<break time="800ms"/>   <!-- Long -->

<!-- Paragraph breaks -->
<break time="600ms"/>   <!-- Brief -->
<break time="1s"/>      <!-- Standard -->
<break time="1.5s"/>    <!-- Long -->

<!-- Section breaks -->
<break time="2s"/>      <!-- Standard -->
<break time="3s"/>      <!-- Long -->
```

### Provider Compatibility Matrix

| Feature | Google | ElevenLabs | MiniMax |
|---------|--------|------------|---------|
| `<speak>` | ✅ | ✅ | ❌ |
| `<p>` | ✅ | ❌ | ❌ |
| `<s>` | ✅ | ❌ | ❌ |
| `<break>` | ✅ | ✅ | ❌* |
| `<emphasis>` | ✅ | ✅† | ❌ |
| `<prosody>` | ✅ | ✅† | ❌ |
| `<say-as>` | ✅ | ❌ | ❌ |
| `<phoneme>` | ✅ | ✅‡ | ❌ |
| Pause Markers | ❌ | ❌ | ✅ |

**Legend:**
- ✅ Full support
- ✅† Limited support  
- ✅‡ Select models only
- ❌ Not supported
- ❌* Uses `<#x#>` format instead

---

**End of Document**

*Keep this guide updated as provider capabilities evolve and new features are added.*