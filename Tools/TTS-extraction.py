#!/usr/bin/env python3
import requests
import argparse
import os
import sys
import subprocess
import tempfile
import base64
import re
import json
import datetime
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Load environment variables from .env file
# Try current directory first, then Tools directory
if not load_dotenv():
    # Get script directory and look for .env there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    load_dotenv(env_path)

# TTS Provider constants
PROVIDER_GOOGLE = "google"
PROVIDER_ELEVENLABS = "elevenlabs"
PROVIDER_MINIMAX = "minimax"

def is_ssml(text):
    """
    Detect if the input text is SSML format
    """
    text_stripped = text.strip()
    return (text_stripped.startswith('<?xml') or text_stripped.startswith('<speak')) and '<speak' in text_stripped

def process_multi_voice_ssml(ssml_text, output_file, lang='en-US', audio_format='MP3',
                            speaking_rate=1.0, pitch=0.0, volume_gain_db=0.0, provider=PROVIDER_GOOGLE):
    """
    Process SSML with multiple voice tags by splitting into voice sections
    and combining the resulting audio files
    """
    import xml.etree.ElementTree as ET
    import tempfile
    import os
    
    try:
        # Parse the SSML
        root = ET.fromstring(ssml_text)
        
        # Find all voice sections and other elements
        voice_sections = []
        other_elements = []
        
        current_voice = None
        current_voice_elements = []
        
        for element in root:
            if element.tag == 'voice':
                # If we have a current voice section, save it
                if current_voice and current_voice_elements:
                    voice_sections.append((current_voice, current_voice_elements))
                
                # Start new voice section
                current_voice = element.get('name')
                current_voice_elements = [element]
            elif current_voice:
                # Add to current voice section
                current_voice_elements.append(element)
            else:
                # No voice context, add to other elements
                other_elements.append(element)
        
        # Don't forget the last voice section
        if current_voice and current_voice_elements:
            voice_sections.append((current_voice, current_voice_elements))
        
        # Generate audio for each section
        temp_files = []
        
        # Process voice sections
        for voice_name, elements in voice_sections:
            # Extract provider from voice element (default to the main provider)
            voice_provider = provider  # Default to main provider
            for elem in elements:
                if elem.tag == 'voice':
                    voice_provider_attr = elem.get('provider')
                    if voice_provider_attr:
                        if voice_provider_attr.lower() == 'google':
                            voice_provider = PROVIDER_GOOGLE
                        elif voice_provider_attr.lower() == 'elevenlabs':
                            voice_provider = PROVIDER_ELEVENLABS
                    break
            
            print(f"Voice section for {voice_name}: provider={voice_provider}")
            
            # Create simple SSML for this voice section (just the content inside voice tags)
            section_content = ""
            for elem in elements:
                if elem.tag == 'voice':
                    # Extract content from inside the voice tag
                    inner_content = ''.join([ET.tostring(child, encoding='unicode', method='xml') for child in elem])
                    if elem.text:
                        inner_content = elem.text + inner_content
                    if elem.tail:
                        inner_content = inner_content + elem.tail
                    section_content += inner_content
                else:
                    section_content += ET.tostring(elem, encoding='unicode', method='xml')
            
            section_ssml = f'<speak>{section_content}</speak>'
            
            # Check if this section is too large
            section_bytes = len(section_ssml.encode('utf-8'))
            print(f"  Section size: {section_bytes} bytes")
            
            if section_bytes > 4500:
                # Split into smaller pieces using SSML-aware chunking
                print(f"  Splitting large voice section...")
                chunks = split_ssml_by_breaks(section_ssml, 4500)
                print(f"  Created {len(chunks)} chunks for voice {voice_name}")
                
                # Generate audio for each chunk
                voice_temp_files = []
                for i, chunk in enumerate(chunks):
                    chunk_size = len(chunk.encode('utf-8'))
                    print(f"    Chunk {i+1}: {chunk_size} bytes")
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format.lower()}') as tmp_file:
                        success = text_to_speech_single(chunk, tmp_file.name, lang, voice_name, audio_format,
                                            speaking_rate, pitch, volume_gain_db, True, voice_provider)
                        if success:
                            voice_temp_files.append(tmp_file.name)
                            print(f"    Chunk {i+1}: Success")
                        else:
                            print(f"  Error generating audio for voice {voice_name} chunk {i+1}")
                            break
                
                # Combine chunks for this voice
                if len(voice_temp_files) > 1:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format.lower()}') as combined_file:
                        if combine_audio_files(voice_temp_files, combined_file.name):
                            temp_files.append(combined_file.name)
                        else:
                            print(f"Error combining chunks for voice {voice_name}")
                            return False
                    
                    # Clean up voice temp files
                    for vf in voice_temp_files:
                        try:
                            os.unlink(vf)
                        except:
                            pass
                else:
                    temp_files.extend(voice_temp_files)
            else:
                # Generate audio for this section (small enough)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format.lower()}') as tmp_file:
                    text_to_speech_single(section_ssml, tmp_file.name, lang, voice_name, audio_format,
                                        speaking_rate, pitch, volume_gain_db, True, voice_provider)
                    temp_files.append(tmp_file.name)
        
        # Combine all audio files
        if len(temp_files) > 1:
            success = combine_audio_files(temp_files, output_file)
            if success:
                print(f"Combined multi-voice audio saved to: {output_file}")
            else:
                print("Error: Failed to combine multi-voice audio files")
                return False
        elif len(temp_files) == 1:
            # Only one file, just copy it
            import shutil
            shutil.copy(temp_files[0], output_file)
            print(f"Single-voice audio saved to: {output_file}")
        
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return True
        
    except ET.ParseError as e:
        print(f"Error: Invalid SSML format: {e}")
        return False
    except Exception as e:
        print(f"Error processing multi-voice SSML: {e}")
        return False

def split_ssml_by_breaks(ssml_text, max_bytes):
    """
    Split SSML content into valid chunks while maintaining proper XML structure
    """
    try:
        # Parse the SSML to understand structure
        root = ET.fromstring(ssml_text)
        
        # Extract all content while preserving structure
        chunks = []
        current_chunk_elements = []
        current_size = len('<speak>\n</speak>')  # Base wrapper size
        
        for element in root:
            # Convert element to string to measure size
            element_str = ET.tostring(element, encoding='unicode', method='xml')
            element_size = len(element_str.encode('utf-8'))
            
            # Check if adding this element would exceed the limit
            if current_size + element_size > max_bytes and current_chunk_elements:
                # Create chunk from current elements
                chunk_content = create_chunk_from_elements(current_chunk_elements)
                chunks.append(chunk_content)
                
                # Start new chunk
                current_chunk_elements = [element]
                current_size = len('<speak>\n</speak>') + element_size
            else:
                # Add element to current chunk
                current_chunk_elements.append(element)
                current_size += element_size
        
        # Add the last chunk if it has content
        if current_chunk_elements:
            chunk_content = create_chunk_from_elements(current_chunk_elements)
            chunks.append(chunk_content)
        
        return chunks
        
    except ET.ParseError as e:
        print(f"Warning: SSML parsing failed ({e}), falling back to text splitting")
        return fallback_ssml_split(ssml_text, max_bytes)

def create_chunk_from_elements(elements):
    """
    Create a valid SSML chunk from a list of elements
    """
    chunk_content = '<speak>\n'
    
    for element in elements:
        element_str = ET.tostring(element, encoding='unicode', method='xml')
        # Add proper indentation
        element_str = '  ' + element_str.replace('\n', '\n  ')
        chunk_content += element_str + '\n'
    
    chunk_content += '</speak>'
    return chunk_content

def fallback_ssml_split(ssml_text, max_bytes):
    """
    Fallback method for splitting SSML when XML parsing fails
    """
    # Remove speak tags to get inner content
    if ssml_text.startswith('<speak>') and ssml_text.endswith('</speak>'):
        inner_content = ssml_text[7:-8].strip()
    else:
        inner_content = ssml_text
    
    # Split by complete paragraph elements first
    if '</p>' in inner_content:
        # Split by paragraph end tags but keep the tag with content
        parts = re.split(r'(</p>\s*(?:<break[^>]*/>)?\s*)', inner_content)
        # Recombine parts to keep </p> with its content
        combined_parts = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                combined_parts.append(parts[i] + parts[i + 1])
            else:
                combined_parts.append(parts[i])
        parts = combined_parts
    elif '<break time=' in inner_content:
        # Split by break tags
        parts = re.split(r'(<break time="[^"]+"/>\s*)', inner_content)
        # Recombine to keep breaks with previous content
        combined_parts = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                combined_parts.append(parts[i] + parts[i + 1])
            else:
                combined_parts.append(parts[i])
        parts = combined_parts
    else:
        # Split by sentences as last resort
        parts = re.split(r'(\.\s+)', inner_content)
    
    chunks = []
    current_chunk = ""
    
    for part in parts:
        if not part.strip():
            continue
            
        test_chunk = current_chunk + '\n' + part if current_chunk else part
        test_ssml = f'<speak>\n{test_chunk}\n</speak>'
        
        if len(test_ssml.encode('utf-8')) <= max_bytes or not current_chunk:
            current_chunk = test_chunk
        else:
            # Current chunk is full, save it and start new chunk
            if current_chunk.strip():
                chunks.append(f'<speak>\n{current_chunk}\n</speak>')
            current_chunk = part
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(f'<speak>\n{current_chunk}\n</speak>')
    
    return chunks

def split_content_by_sentences(content, max_bytes):
    """
    Split content into chunks by sentences while preserving SSML tags
    """
    import xml.etree.ElementTree as ET
    
    chunks = []
    
    # More robust approach: split by complete paragraph elements
    # First, try to split by </p> tags with proper closing
    parts = content.split('</p>')
    current_chunk = ""
    
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        
        # Reconstruct the paragraph properly
        if i < len(parts) - 1:  # Not the last part
            test_chunk = current_chunk + part + '</p>'
        else:  # Last part (may not have </p>)
            test_chunk = current_chunk + part
        
        if len(test_chunk.encode('utf-8')) <= max_bytes or not current_chunk:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if i < len(parts) - 1:
                current_chunk = part + '</p>'
            else:
                current_chunk = part
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Validate each chunk has proper structure
    validated_chunks = []
    for chunk in chunks:
        if chunk:
            # Ensure chunk is properly structured
            validated_chunks.append(chunk)
    
    return validated_chunks if validated_chunks else [content]

def process_large_ssml(ssml_text, output_file, lang='en-US', voice_name=None, audio_format='MP3',
                      speaking_rate=1.0, pitch=0.0, volume_gain_db=0.0, provider=PROVIDER_GOOGLE):
    """
    Process large single-voice SSML by splitting into chunks and combining the resulting audio files
    """
    import xml.etree.ElementTree as ET
    import tempfile
    import os
    
    try:
        print(f"Original SSML size: {len(ssml_text.encode('utf-8'))} bytes")
        
        # Split SSML content into chunks by logical breaks (paragraphs)
        chunks = split_ssml_by_breaks(ssml_text, 4500)  # Leave buffer for <speak> tags
        print(f"Split into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        temp_files = []
        
        for i, chunk in enumerate(chunks):
            chunk_bytes = len(chunk.encode('utf-8'))
            print(f"  Chunk {i+1}: {chunk_bytes} bytes")
            
            # Validate SSML before sending to API
            try:
                import xml.etree.ElementTree as ET
                ET.fromstring(chunk)
            except ET.ParseError as e:
                print(f"  Invalid SSML in chunk {i+1}: {e}")
                print(f"  Chunk content preview: {chunk[:200]}...")
                # Try to fix common issues
                chunk = chunk.replace('&', '&amp;')
                try:
                    ET.fromstring(chunk)
                    print(f"  Fixed entity encoding in chunk {i+1}")
                except ET.ParseError:
                    print(f"  Could not fix SSML in chunk {i+1}, skipping")
                    continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format.lower()}') as tmp_file:
                success = text_to_speech_single(chunk, tmp_file.name, lang, voice_name, audio_format,
                                               speaking_rate, pitch, volume_gain_db, True, provider)
                if success:
                    temp_files.append(tmp_file.name)
                else:
                    print(f"Error generating audio for chunk {i+1}")
                    print(f"  Problematic SSML: {chunk[:500]}...")
                    # Clean up temp files
                    for tf in temp_files:
                        try:
                            os.unlink(tf)
                        except:
                            pass
                    return False
        
        # Combine all audio files
        if len(temp_files) > 1:
            success = combine_audio_files(temp_files, output_file)
            if success:
                print(f"Combined large SSML audio saved to: {output_file}")
            else:
                print("Error: Failed to combine audio files")
                return False
        elif len(temp_files) == 1:
            # Only one file, just copy it
            import shutil
            shutil.copy(temp_files[0], output_file)
            print(f"Single chunk audio saved to: {output_file}")
        else:
            print("Error: No audio files generated")
            return False
        
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return True
        
    except ET.ParseError as e:
        print(f"Error: Invalid SSML format: {e}")
        return False
    except Exception as e:
        print(f"Error processing large SSML: {e}")
        return False

def minimax_tts_single(text, output_file, voice_id=None, model_id="speech-02-hd",
                      speed=1.0, pitch=0, volume=1.0, emotion="happy", 
                      audio_format="mp3", sample_rate=32000, bitrate=128000):
    """
    Convert text to speech using MiniMax API (single request)
    Supports proprietary pause format <#x#> where x is seconds
    """
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("Error: MINIMAX_API_KEY not found in environment variables")
        return False
    
    # Default voice if none specified
    if not voice_id:
        voice_id = "female-shaonv"
    
    try:
        url = "https://api.minimax.chat/v1/t2a_pro"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "text": text,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": volume,
                "pitch": pitch,
                "emotion": emotion
            },
            "audio_setting": {
                "format": audio_format,
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "channel": 1
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"MiniMax API Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"MiniMax API Error Response: {response.text}")
        
        if response.status_code == 200:
            # Handle different response formats
            try:
                response_data = response.json()
                if 'audio_data' in response_data:
                    # Base64 encoded audio data
                    audio_data = base64.b64decode(response_data['audio_data'])
                else:
                    # Direct binary response
                    audio_data = response.content
            except:
                # Fallback to binary content
                audio_data = response.content
            
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            return True
        else:
            print(f"Error with MiniMax TTS: API request failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with MiniMax TTS: {e}")
        return False

def elevenlabs_tts_single(text, output_file, voice_id=None, model_id="eleven_turbo_v2_5", 
                         stability=0.5, similarity_boost=0.5, style=0.0, use_speaker_boost=True, force_ssml=False):
    """
    Convert text to speech using ElevenLabs API (single request)
    Supports both plain text and SSML
    """
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment variables")
        return False
    
    # Default voice if none specified
    if not voice_id:
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Detect if input is SSML
        use_ssml = force_ssml or is_ssml(text)
        
        # Prepare payload - ElevenLabs supports SSML
        if use_ssml:
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                },
                "pronunciation_dictionary_locators": [],
                "seed": None,
                "previous_text": None,
                "next_text": None,
                "previous_request_ids": [],
                "next_request_ids": []
            }
        else:
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Error with ElevenLabs TTS: API request failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with ElevenLabs TTS: {e}")
        return False

def text_to_speech_single(text, output_file, lang='en-US', voice_name=None, audio_format='MP3', 
                         speaking_rate=1.0, pitch=0.0, volume_gain_db=0.0, force_ssml=False, provider=PROVIDER_GOOGLE):
    """
    Convert text to speech using specified provider (Google TTS, ElevenLabs, or MiniMax)
    """
    if provider == PROVIDER_MINIMAX:
        # Convert parameters for MiniMax
        volume_linear = min(2.0, max(0.1, 1.0 + (volume_gain_db / 20)))  # Convert dB to linear scale
        return minimax_tts_single(
            text=text,
            output_file=output_file, 
            voice_id=voice_name,
            speed=speaking_rate,
            pitch=int(pitch),  # MiniMax uses integer pitch
            volume=volume_linear,
            audio_format=audio_format.lower()
        )
    elif provider == PROVIDER_ELEVENLABS:
        return elevenlabs_tts_single(text, output_file, voice_name, force_ssml=force_ssml)
    
    # Default to Google TTS
    api_key = os.getenv('GOOGLE_TTS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_TTS_API_KEY not found in environment variables")
        return False
    
    try:
        # Detect SSML input
        use_ssml = force_ssml or is_ssml(text)
        
        # Prepare the request payload
        payload = {
            'input': {'ssml' if use_ssml else 'text': text},
            'voice': {
                'languageCode': lang,
                'name': voice_name
            },
            'audioConfig': {
                'audioEncoding': audio_format,
                'speakingRate': speaking_rate,
                'pitch': pitch,
                'volumeGainDb': volume_gain_db
            }
        }
        
        # Remove voice name if not specified (let Google choose default)
        if not voice_name:
            payload['voice'] = {'languageCode': lang}
        
        # Make API request
        url = f'https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Decode and save the audio
            audio_content = base64.b64decode(response.json()['audioContent'])
            with open(output_file, 'wb') as out:
                out.write(audio_content)
            return True
        else:
            print(f"Error with Google TTS: API request failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with Google TTS: {e}")
        return False

def combine_audio_files(input_files, output_file):
    """
    Combine multiple audio files into one using ffmpeg
    """
    if not input_files:
        return False
    
    if len(input_files) == 1:
        # Only one file, just copy it
        import shutil
        shutil.copy(input_files[0], output_file)
        return True
    
    try:
        # Create temporary file list for ffmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as filelist:
            for file_path in input_files:
                # Escape file paths for ffmpeg
                escaped_path = file_path.replace("'", "'\"'\"'")
                filelist.write(f"file '{escaped_path}'\n")
            filelist_path = filelist.name
        
        # Use ffmpeg to concatenate files
        cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path, '-c', 'copy', output_file, '-y']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up the filelist
        os.unlink(filelist_path)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error combining audio files: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"Error combining audio files: {e}")
        return False

def text_to_speech(text, output_file=None, lang='en-US', voice_name=None, audio_format='MP3', 
                   speaking_rate=1.0, pitch=0.0, volume_gain_db=0.0, force_ssml=False, provider=PROVIDER_GOOGLE):
    """
    Convert text to speech using specified provider (Google TTS or ElevenLabs)
    """
    # Check API keys based on provider
    if provider == PROVIDER_MINIMAX:
        api_key = os.getenv('MINIMAX_API_KEY')
        if not api_key:
            print("Error: MINIMAX_API_KEY not found in environment variables")
            print("Make sure your .env file contains: MINIMAX_API_KEY=your_api_key_here")
            sys.exit(1)
    elif provider == PROVIDER_ELEVENLABS:
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            print("Error: ELEVENLABS_API_KEY not found in environment variables")
            print("Make sure your .env file contains: ELEVENLABS_API_KEY=your_api_key_here")
            sys.exit(1)
    else:
        api_key = os.getenv('GOOGLE_TTS_API_KEY')
        if not api_key:
            print("Error: GOOGLE_TTS_API_KEY not found in environment variables")
            print("Make sure your .env file contains: GOOGLE_TTS_API_KEY=your_api_key_here")
            sys.exit(1)
    
    try:
        # Detect if input is SSML
        use_ssml = force_ssml or is_ssml(text)
        if use_ssml:
            print("Detected SSML input format")
            
            # Check if SSML contains multiple voice tags
            if '<voice' in text and output_file:
                print("Multi-voice SSML detected, processing separately...")
                return process_multi_voice_ssml(text, output_file, lang, audio_format,
                                              speaking_rate, pitch, volume_gain_db, provider)
            
            # Check if single SSML is too large
            text_bytes = len(text.encode('utf-8'))
            if text_bytes > 4500 and output_file:
                print(f"Large SSML detected ({text_bytes} bytes), splitting into chunks...")
                return process_large_ssml(text, output_file, lang, voice_name, audio_format,
                                        speaking_rate, pitch, volume_gain_db, provider)
        
        # For single voice or plain text, use the single function
        if output_file:
            success = text_to_speech_single(text, output_file, lang, voice_name, audio_format,
                                          speaking_rate, pitch, volume_gain_db, force_ssml, provider)
            if success:
                print(f"Audio saved to: {output_file}")
            return success
        else:
            # Play audio directly
            file_ext = '.mp3' if audio_format == 'MP3' else '.wav'
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                success = text_to_speech_single(text, tmp_file.name, lang, voice_name, audio_format,
                                              speaking_rate, pitch, volume_gain_db, force_ssml, provider)
                if success:
                    # Use system audio player (macOS)
                    subprocess.run(['afplay', tmp_file.name], check=True)
                os.unlink(tmp_file.name)
                return success
            
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return False

def read_text_file(file_path):
    """
    Read text content from file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Multi-Provider Text-to-Speech Extraction Tool (Google Cloud TTS, ElevenLabs, MiniMax)')
    
    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--text', help='Text to convert to speech')
    group.add_argument('-f', '--file', help='Text file to read and convert to speech')
    
    # Output options
    parser.add_argument('-o', '--output', help='Output audio file path (optional)')
    parser.add_argument('-l', '--lang', default='en-US', help='Language code (default: en-US)')
    parser.add_argument('-v', '--voice', help='Voice name or ID')
    parser.add_argument('--provider', choices=[PROVIDER_GOOGLE, PROVIDER_ELEVENLABS, PROVIDER_MINIMAX], default=PROVIDER_GOOGLE,
                       help='TTS provider (default: google)')
    parser.add_argument('--format', default='MP3', choices=['MP3', 'LINEAR16', 'OGG_OPUS'], 
                       help='Audio format (default: MP3)')
    parser.add_argument('--rate', type=float, default=1.0, help='Speaking rate 0.25-4.0 (default: 1.0)')
    parser.add_argument('--pitch', type=float, default=0.0, help='Pitch adjustment -20.0-20.0 (default: 0.0)')
    parser.add_argument('--volume', type=float, default=0.0, help='Volume gain -96.0-16.0 dB (default: 0.0)')
    parser.add_argument('--ssml', action='store_true', help='Force treat input as SSML format')
    
    args = parser.parse_args()
    
    # Get text input
    if args.file:
        text = read_text_file(args.file)
    else:
        text = args.text
    
    if not text.strip():
        print("Error: No text to convert.")
        sys.exit(1)
    
    # Modify output filename to include voice name if specified
    final_output = args.output
    if args.output and args.voice:
        # Split filename and extension
        file_path, file_ext = os.path.splitext(args.output)
        # Append voice name to filename
        final_output = f"{file_path}_{args.voice}{file_ext}"
    
    # Ensure output directory exists if output file is specified
    if final_output:
        output_dir = os.path.dirname(final_output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
    
    # Convert text to speech
    success = text_to_speech(text, final_output, args.lang, args.voice, args.format, 
                           args.rate, args.pitch, args.volume, args.ssml, args.provider)
    
    if not success:
        sys.exit(1)
    
    if not args.output:
        print("Speech playback completed.")

if __name__ == "__main__":
    main()