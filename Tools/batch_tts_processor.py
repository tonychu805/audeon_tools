#!/usr/bin/env python3
"""
Batch TTS processor for SSML files
Processes all SSML files in specified directories using TTS-extraction.py
"""

import os
import subprocess
import glob
import argparse
from pathlib import Path

def process_ssml_files(input_dir, output_dir, provider="google", voice=None, audio_format="MP3"):
    """
    Process all SSML/txt files in input directory
    """
    # Find both SSML and txt files
    ssml_pattern = os.path.join(input_dir, "**/*.ssml")
    txt_pattern = os.path.join(input_dir, "**/*.txt")
    ssml_files = glob.glob(ssml_pattern, recursive=True)
    txt_files = glob.glob(txt_pattern, recursive=True)
    all_files = ssml_files + txt_files
    
    if not all_files:
        print(f"No SSML or txt files found in {input_dir}")
        return
    
    print(f"Found {len(ssml_files)} SSML files and {len(txt_files)} txt files to process")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    for file_path in all_files:
        # Get relative path to maintain directory structure
        rel_path = os.path.relpath(file_path, input_dir)
        base_name = os.path.splitext(rel_path)[0]
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Create output path with same structure
        output_file = os.path.join(output_dir, f"{base_name}.{audio_format.lower()}")
        output_subdir = os.path.dirname(output_file)
        
        if output_subdir:
            os.makedirs(output_subdir, exist_ok=True)
        
        # Auto-select provider and build command based on file type
        if file_ext == ".txt":
            file_provider = "openai"  # Auto-switch to OpenAI for txt files
            cmd = [
                "python", "TTS-extraction.py",
                "-f", file_path,
                "-o", output_file,
                "--provider", file_provider,
                "--format", audio_format
                # No --ssml flag for txt files
            ]
        else:  # .ssml files
            file_provider = provider  # Use specified provider for SSML
            cmd = [
                "python", "TTS-extraction.py",
                "-f", file_path,
                "-o", output_file,
                "--provider", file_provider,
                "--format", audio_format,
                "--ssml"  # Force SSML mode for .ssml files
            ]
        
        if voice:
            cmd.extend(["--voice", voice])
        
        print(f"Processing: {rel_path} (provider: {file_provider})")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print(f"✓ Success: {output_file}")
                success_count += 1
            else:
                print(f"✗ Error processing {file_path}")
                print(f"  Error: {result.stderr}")
                error_count += 1
                
        except Exception as e:
            print(f"✗ Exception processing {file_path}: {e}")
            error_count += 1
    
    print(f"\nBatch processing complete:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(all_files)}")

def main():
    parser = argparse.ArgumentParser(description='Batch TTS processor for SSML and txt files')
    
    parser.add_argument('input_dir', help='Input directory containing SSML or txt files')
    parser.add_argument('output_dir', help='Output directory for audio files')
    parser.add_argument('--provider', choices=['google', 'elevenlabs', 'minimax', 'openai'], 
                       default='google', help='TTS provider (default: google, auto-switches to openai for .txt files)')
    parser.add_argument('--voice', help='Voice name/ID to use')
    parser.add_argument('--format', default='MP3', choices=['MP3', 'LINEAR16', 'OGG_OPUS'],
                       help='Audio format (default: MP3)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist")
        return 1
    
    process_ssml_files(args.input_dir, args.output_dir, args.provider, args.voice, args.format)
    return 0

if __name__ == "__main__":
    exit(main())