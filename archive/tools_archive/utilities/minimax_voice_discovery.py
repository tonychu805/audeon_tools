#!/usr/bin/env python3
"""
MiniMax Voice Discovery Tool
Helps discover available voice IDs and test different voices
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Known voice IDs from documentation
KNOWN_VOICES = {
    "Female Voices": [
        "female-shaonv",
        "audiobook_female_1", 
        "Charming_Lady",
        "Wise_Woman"
    ],
    "Male Voices": [
        "male-qn-qingse",
        "cute_boy"
    ]
}

def test_minimax_voice(voice_id, test_text="Hello, this is a voice test."):
    """
    Test a specific MiniMax voice ID
    """
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("❌ Error: MINIMAX_API_KEY not found in environment variables")
        return False
    
    try:
        url = "https://api.minimax.chat/v1/t2a_pro"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "speech-02-hd",
            "text": test_text,
            "voice_setting": {
                "voice_id": voice_id,
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
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Voice '{voice_id}' - SUCCESS")
            
            # Save a small test file
            output_file = f"voice_test_{voice_id.replace('-', '_')}.mp3"
            try:
                response_data = response.json()
                if 'audio_data' in response_data:
                    import base64
                    audio_data = base64.b64decode(response_data['audio_data'])
                else:
                    audio_data = response.content
            except:
                audio_data = response.content
            
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            print(f"   📁 Saved test audio: {output_file}")
            
            return True
        else:
            print(f"❌ Voice '{voice_id}' - FAILED ({response.status_code})")
            if response.status_code == 400:
                try:
                    error_info = response.json()
                    if "voice_id" in str(error_info).lower():
                        print(f"   💡 Voice ID '{voice_id}' may not exist")
                    else:
                        print(f"   📝 Error: {error_info}")
                except:
                    print(f"   📝 Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Voice '{voice_id}' - ERROR: {e}")
        return False

def discover_voice_patterns():
    """
    Try to discover voice ID patterns by testing variations
    """
    print("🔍 Testing voice ID patterns...")
    
    # Test common patterns
    patterns_to_test = [
        # Gender-based patterns
        "female-standard",
        "female-young", 
        "female-mature",
        "male-standard",
        "male-young",
        "male-deep",
        
        # Language-based patterns
        "en-female-1",
        "en-male-1", 
        "zh-female-1",
        "zh-male-1",
        
        # Descriptive patterns
        "professional_female",
        "professional_male",
        "narrator_female",
        "narrator_male",
        
        # Numbered patterns
        "voice_001",
        "voice_002",
        "female_001",
        "male_001"
    ]
    
    working_voices = []
    
    for voice_id in patterns_to_test:
        if test_minimax_voice(voice_id, "Quick test"):
            working_voices.append(voice_id)
    
    if working_voices:
        print(f"\n🎉 Found {len(working_voices)} additional working voices:")
        for voice in working_voices:
            print(f"   - {voice}")
    else:
        print("\n❌ No additional voice patterns discovered")
    
    return working_voices

def test_known_voices():
    """
    Test all known voice IDs from documentation
    """
    print("🎤 Testing known MiniMax voice IDs...")
    print("=" * 50)
    
    working_voices = []
    
    for category, voices in KNOWN_VOICES.items():
        print(f"\n📂 {category}:")
        for voice_id in voices:
            if test_minimax_voice(voice_id):
                working_voices.append(voice_id)
    
    return working_voices

def generate_voice_usage_examples(working_voices):
    """
    Generate usage examples for working voices
    """
    if not working_voices:
        print("\n❌ No working voices found to generate examples")
        return
    
    print(f"\n📋 Usage Examples for {len(working_voices)} Working Voices:")
    print("=" * 60)
    
    for voice_id in working_voices:
        print(f"""
# Test voice: {voice_id}
python Tools/TTS-extraction.py -t "Hello, this is {voice_id}" -o "test_{voice_id.replace('-', '_')}.mp3" --provider minimax --voice "{voice_id}"
""")

def main():
    """
    Main function to discover MiniMax voices
    """
    print("🎵 MiniMax Voice Discovery Tool")
    print("=" * 50)
    
    # Test API connection
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("❌ Error: MINIMAX_API_KEY not found in environment variables")
        print("Please add MINIMAX_API_KEY=your_key_here to your .env file")
        return
    
    print(f"✅ API key found: {api_key[:10]}...")
    print()
    
    # Test known voices
    working_voices = test_known_voices()
    
    # Try to discover more voice patterns
    discovered_voices = discover_voice_patterns()
    working_voices.extend(discovered_voices)
    
    # Remove duplicates
    working_voices = list(set(working_voices))
    
    # Generate usage examples
    generate_voice_usage_examples(working_voices)
    
    # Summary
    print(f"\n📊 Discovery Summary:")
    print(f"   ✅ Working voices found: {len(working_voices)}")
    print(f"   📁 Test audio files generated: {len(working_voices)}")
    print(f"   💡 Try these voice IDs with TTS-extraction.py")

if __name__ == "__main__":
    main()