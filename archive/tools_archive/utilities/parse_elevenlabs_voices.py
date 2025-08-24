#!/usr/bin/env python3
"""
Parse ElevenLabs shared voices and add to google-cloudtts-voices.txt
"""
import json
from pathlib import Path

def parse_elevenlabs_voices():
    # Read the JSON file
    with open('elevenlabs_shared_voices.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    voices = data.get('voices', [])
    
    # Parse each voice into our format
    parsed_voices = []
    
    for voice in voices:
        name = voice.get('name', 'Unknown')
        voice_id = voice.get('voice_id', '')
        gender = voice.get('gender', 'unknown').upper()
        accent = voice.get('accent', 'unknown')
        language = voice.get('language', 'en')
        locale = voice.get('locale', 'en-US')
        age = voice.get('age', 'unknown')
        descriptive = voice.get('descriptive', 'unknown')
        use_case = voice.get('use_case', 'unknown')
        description = voice.get('description', '')
        
        # Clean up description - remove newlines and limit length
        description = description.replace('\n', ' ').replace('\r', ' ')
        if len(description) > 100:
            description = description[:97] + "..."
        
        # Format: Provider	Tier	Language	Voice_ID	Gender	Description
        tier = "Shared"
        
        parsed_voice = f"ElevenLabs\t{tier}\t{language}\t{voice_id}\t{gender}\t{name} - {accent} {age} {descriptive} - {description}"
        parsed_voices.append(parsed_voice)
    
    return parsed_voices

def update_voice_file():
    parsed_voices = parse_elevenlabs_voices()
    
    print(f"Found {len(parsed_voices)} ElevenLabs shared voices")
    
    # Read current file
    with open('google-cloudtts-voices.txt', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Find where to insert the shared voices (after the existing ElevenLabs section)
    elevenlabs_section_end = current_content.find("# Multilingual Voices")
    if elevenlabs_section_end == -1:
        print("Could not find ElevenLabs section end")
        return
    
    # Find the end of multilingual voices section
    insert_point = current_content.find("\n# ========================================\n# MINIMAX VOICES")
    if insert_point == -1:
        print("Could not find MiniMax section start")
        return
    
    # Insert the shared voices
    new_section = "\n# Shared Community Voices\n"
    for voice in parsed_voices:
        new_section += voice + "\n"
    
    # Insert into file content
    updated_content = current_content[:insert_point] + new_section + current_content[insert_point:]
    
    # Write back to file
    with open('google-cloudtts-voices.txt', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated google-cloudtts-voices.txt with {len(parsed_voices)} shared voices")

if __name__ == "__main__":
    update_voice_file()