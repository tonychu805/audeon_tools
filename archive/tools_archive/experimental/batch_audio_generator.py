#!/usr/bin/env python3
"""
Batch Audio Generator - Process multiple text/SSML files to audio in parallel
"""
import os
import glob
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from pathlib import Path

# Import TTS-extraction functions
from TTS_extraction import text_to_speech, read_text_file

class AudioProgressCounter:
    def __init__(self, total):
        self.total = total
        self.processed = 0
        self.failed = 0
        self.lock = Lock()
    
    def increment_processed(self, filename):
        with self.lock:
            self.processed += 1
            print(f"✅ [{self.processed}/{self.total}] Generated: {filename}")
    
    def increment_failed(self, filename, error):
        with self.lock:
            self.failed += 1
            print(f"❌ [{self.total-self.failed}/{self.total}] Failed: {filename} - {error}")

def process_single_file(file_path, output_dir, provider, voice, rate, pitch, volume, progress_counter):
    """Process a single text/SSML file to audio"""
    try:
        # Read content
        content = read_text_file(file_path)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}.mp3")
        
        # Convert to audio
        success = text_to_speech(
            content, 
            output_file,
            voice_name=voice,
            speaking_rate=rate,
            pitch=pitch,
            volume_gain_db=volume,
            provider=provider
        )
        
        if success:
            progress_counter.increment_processed(f"{base_name}.mp3")
            return True
        else:
            progress_counter.increment_failed(base_name, "TTS conversion failed")
            return False
            
    except Exception as e:
        progress_counter.increment_failed(os.path.basename(file_path), str(e))
        return False

def batch_convert_to_audio(input_dir, output_dir, provider="google", max_workers=3, **tts_params):
    """Convert all text files in directory to audio using parallel processing"""
    
    # Get file extension based on provider
    extensions = {
        "google": ["*.ssml", "*.txt"],
        "elevenlabs": ["*.ssml", "*.txt"], 
        "minimax": ["*.txt", "*.ssml"]
    }
    
    # Find all matching files
    files = []
    for ext in extensions.get(provider, ["*.txt"]):
        pattern = os.path.join(input_dir, ext)
        files.extend(glob.glob(pattern))
    
    if not files:
        print(f"❌ No files found in {input_dir} with extensions {extensions.get(provider)}")
        return False
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"🎵 Starting batch audio generation...")
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🎯 Provider: {provider}")
    print(f"📊 Files to process: {len(files)}")
    print(f"👥 Workers: {max_workers}")
    print()
    
    start_time = time.time()
    progress_counter = AudioProgressCounter(len(files))
    
    # Process files in parallel (limited workers for API rate limiting)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_single_file, 
                file_path, 
                output_dir, 
                provider,
                tts_params.get('voice'),
                tts_params.get('rate', 1.0),
                tts_params.get('pitch', 0.0),
                tts_params.get('volume', 0.0),
                progress_counter
            ): file_path
            for file_path in files
        }
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n📊 Audio Generation Summary:")
    print(f"   Total files: {len(files)}")
    print(f"   Successfully generated: {progress_counter.processed}")
    print(f"   Failed: {progress_counter.failed}")
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Average per file: {processing_time/len(files):.2f} seconds")
    
    return progress_counter.failed == 0

def main():
    parser = argparse.ArgumentParser(
        description='Batch Audio Generator - Convert multiple text/SSML files to audio in parallel'
    )
    
    parser.add_argument('input_dir', help='Input directory containing text/SSML files')
    parser.add_argument('output_dir', help='Output directory for audio files')
    parser.add_argument('-p', '--provider', choices=['google', 'elevenlabs', 'minimax'], 
                       default='google', help='TTS provider (default: google)')
    parser.add_argument('-w', '--workers', type=int, default=3,
                       help='Number of parallel workers (default: 3, be mindful of API limits)')
    parser.add_argument('-v', '--voice', help='Voice name or ID')
    parser.add_argument('--rate', type=float, default=1.0, 
                       help='Speaking rate 0.25-4.0 (default: 1.0)')
    parser.add_argument('--pitch', type=float, default=0.0, 
                       help='Pitch adjustment -20.0-20.0 (default: 0.0)')
    parser.add_argument('--volume', type=float, default=0.0, 
                       help='Volume gain -96.0-16.0 dB (default: 0.0)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"❌ Error: Input directory '{args.input_dir}' does not exist.")
        sys.exit(1)
    
    success = batch_convert_to_audio(
        args.input_dir,
        args.output_dir,
        args.provider,
        args.workers,
        voice=args.voice,
        rate=args.rate,
        pitch=args.pitch,
        volume=args.volume
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()