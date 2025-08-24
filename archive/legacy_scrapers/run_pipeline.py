#!/usr/bin/env python3
"""
Pipeline Orchestration - Complete end-to-end processing
"""
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    end_time = time.time()
    
    if result.returncode == 0:
        print(f"✅ {description} completed in {end_time - start_time:.2f} seconds")
        return True
    else:
        print(f"❌ {description} failed!")
        return False

def run_complete_pipeline(articles_json, provider="google", workers=5, audio_workers=3, 
                         voice=None, rate=1.0, pitch=0.0, volume=0.0, use_cache=True):
    """
    Run the complete TTS pipeline from articles JSON to audio files
    """
    print(f"🎯 Starting Complete TTS Pipeline")
    print(f"📄 Input: {articles_json}")
    print(f"🎵 Provider: {provider}")
    print(f"👥 Content Workers: {workers}")
    print(f"🎤 Audio Workers: {audio_workers}")
    print(f"💾 Use Cache: {use_cache}")
    print("=" * 60)
    
    # Ensure we're in the Tools directory
    tools_dir = Path(__file__).parent
    os.chdir(tools_dir)
    
    # Set up directory paths
    content_dir = f"../Content/articles/{provider}_content"
    audio_dir = f"../Content/articles/{provider}_audio"
    
    total_start_time = time.time()
    
    # Step 1: Generate formatted content files
    content_cmd = [
        "python3", "parallel_content_extractor.py",
        articles_json,
        "-p", provider,
        "-o", content_dir,
        "-w", str(workers)
    ]
    
    if not run_command(content_cmd, f"Step 1: Generate {provider} formatted content"):
        return False
    
    # Step 2: Generate audio files
    audio_script = "batch_audio_generator.py"
    if use_cache:
        # Create a wrapper script that uses cached TTS
        wrapper_script = "cached_batch_audio.py"
        create_cached_batch_script(wrapper_script)
        audio_script = wrapper_script
    
    audio_cmd = [
        "python3", audio_script,
        content_dir,
        audio_dir,
        "-p", provider,
        "-w", str(audio_workers),
        "--rate", str(rate),
        "--pitch", str(pitch),
        "--volume", str(volume)
    ]
    
    if voice:
        audio_cmd.extend(["-v", voice])
    
    if not run_command(audio_cmd, f"Step 2: Generate audio files with {provider}"):
        return False
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎉 Pipeline Complete!")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"📁 Content files: {content_dir}")
    print(f"🎵 Audio files: {audio_dir}")
    
    # Show file counts
    try:
        content_files = len(list(Path(content_dir).glob("*")))
        audio_files = len(list(Path(audio_dir).glob("*.mp3")))
        print(f"📊 Generated {content_files} content files and {audio_files} audio files")
    except:
        pass
    
    # Show cache stats if using cache
    if use_cache:
        try:
            from cached_tts_wrapper import print_cache_stats
            print_cache_stats()
        except:
            pass
    
    return True

def create_cached_batch_script(script_name):
    """Create a wrapper script that uses caching"""
    script_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from batch_audio_generator import batch_convert_to_audio as original_batch_convert
from cached_tts_wrapper import cached_text_to_speech
import batch_audio_generator

# Replace the text_to_speech function with cached version
batch_audio_generator.text_to_speech = cached_text_to_speech

# Run the original main function
if __name__ == "__main__":
    batch_audio_generator.main()
'''
    
    with open(script_name, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_name, 0o755)  # Make executable

def main():
    parser = argparse.ArgumentParser(
        description='Complete TTS Pipeline Orchestration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic pipeline with Google TTS
  python run_pipeline.py articles.json -p google

  # High-performance pipeline with ElevenLabs
  python run_pipeline.py articles.json -p elevenlabs -w 10 -a 5 --voice "21m00Tcm4TlvDq8ikWAM"

  # MiniMax with custom settings
  python run_pipeline.py articles.json -p minimax --rate 1.2 --pitch 2 --no-cache
        """
    )
    
    parser.add_argument('articles_json', help='Path to articles JSON file')
    parser.add_argument('-p', '--provider', choices=['google', 'elevenlabs', 'minimax'], 
                       default='google', help='TTS provider (default: google)')
    parser.add_argument('-w', '--workers', type=int, default=5,
                       help='Number of content processing workers (default: 5)')
    parser.add_argument('-a', '--audio-workers', type=int, default=3,
                       help='Number of audio generation workers (default: 3)')
    parser.add_argument('-v', '--voice', help='Voice name or ID')
    parser.add_argument('--rate', type=float, default=1.0,
                       help='Speaking rate 0.25-4.0 (default: 1.0)')
    parser.add_argument('--pitch', type=float, default=0.0,
                       help='Pitch adjustment -20.0-20.0 (default: 0.0)')
    parser.add_argument('--volume', type=float, default=0.0,
                       help='Volume gain -96.0-16.0 dB (default: 0.0)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable audio caching')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.articles_json):
        print(f"❌ Error: Articles file '{args.articles_json}' does not exist.")
        sys.exit(1)
    
    success = run_complete_pipeline(
        args.articles_json,
        provider=args.provider,
        workers=args.workers,
        audio_workers=args.audio_workers,
        voice=args.voice,
        rate=args.rate,
        pitch=args.pitch,
        volume=args.volume,
        use_cache=not args.no_cache
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()