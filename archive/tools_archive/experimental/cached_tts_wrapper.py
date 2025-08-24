#!/usr/bin/env python3
"""
Cached TTS Wrapper - Avoid regenerating audio for identical content
"""
import os
import hashlib
import json
import time
from pathlib import Path
from TTS_extraction import text_to_speech

class TTSCache:
    def __init__(self, cache_dir="./tts_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
    
    def _load_index(self):
        """Load cache index from file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_index(self):
        """Save cache index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _get_content_hash(self, content, provider, voice_settings):
        """Generate unique hash for content + settings combination"""
        settings_str = json.dumps(voice_settings, sort_keys=True)
        combined = f"{content}{provider}{settings_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_path(self, content_hash, provider):
        """Get cache file path for given hash"""
        return self.cache_dir / f"{provider}_{content_hash}.mp3"
    
    def get_cached_audio(self, content, provider, voice_settings):
        """Check if audio exists in cache and return path if found"""
        content_hash = self._get_content_hash(content, provider, voice_settings)
        cache_path = self._get_cache_path(content_hash, provider)
        
        if cache_path.exists() and content_hash in self.index:
            # Verify file is not corrupted
            if cache_path.stat().st_size > 1000:  # Reasonable minimum file size
                cache_info = self.index[content_hash]
                print(f"🎯 Cache HIT: Using cached audio from {cache_info['created']}")
                return str(cache_path)
        
        return None
    
    def cache_audio(self, content, provider, voice_settings, audio_file_path):
        """Add audio file to cache"""
        content_hash = self._get_content_hash(content, provider, voice_settings)
        cache_path = self._get_cache_path(content_hash, provider)
        
        # Copy audio file to cache
        import shutil
        shutil.copy2(audio_file_path, cache_path)
        
        # Update index
        self.index[content_hash] = {
            "provider": provider,
            "voice_settings": voice_settings,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": cache_path.stat().st_size,
            "cache_path": str(cache_path)
        }
        self._save_index()
        print(f"💾 Cached audio file: {cache_path.name}")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total_files = len(self.index)
        total_size = sum(
            Path(info["cache_path"]).stat().st_size 
            for info in self.index.values() 
            if Path(info["cache_path"]).exists()
        )
        
        return {
            "total_files": total_files,
            "total_size_mb": total_size / 1024 / 1024,
            "cache_dir": str(self.cache_dir)
        }
    
    def clear_cache(self):
        """Clear all cached files"""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.index = {}
        print("🗑️  Cache cleared")

# Global cache instance
_tts_cache = TTSCache()

def cached_text_to_speech(content, output_file, provider="google", **tts_params):
    """
    Text-to-speech with caching - checks cache before generating new audio
    """
    voice_settings = {
        "voice_name": tts_params.get("voice_name"),
        "speaking_rate": tts_params.get("speaking_rate", 1.0),
        "pitch": tts_params.get("pitch", 0.0),
        "volume_gain_db": tts_params.get("volume_gain_db", 0.0),
        "audio_format": tts_params.get("audio_format", "MP3"),
        "lang": tts_params.get("lang", "en-US")
    }
    
    # Check cache first
    cached_path = _tts_cache.get_cached_audio(content, provider, voice_settings)
    if cached_path:
        # Copy cached file to output location
        import shutil
        shutil.copy2(cached_path, output_file)
        return True
    
    # Generate new audio
    print(f"🎵 Generating new audio with {provider}...")
    success = text_to_speech(content, output_file, provider=provider, **tts_params)
    
    if success:
        # Cache the generated audio
        _tts_cache.cache_audio(content, provider, voice_settings, output_file)
    
    return success

def print_cache_stats():
    """Print cache statistics"""
    stats = _tts_cache.get_cache_stats()
    print(f"\n📊 TTS Cache Statistics:")
    print(f"   Cached files: {stats['total_files']}")
    print(f"   Cache size: {stats['total_size_mb']:.2f} MB")
    print(f"   Cache directory: {stats['cache_dir']}")

def clear_tts_cache():
    """Clear the TTS cache"""
    _tts_cache.clear_cache()

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='TTS Cache Management')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    
    args = parser.parse_args()
    
    if args.stats:
        print_cache_stats()
    elif args.clear:
        clear_tts_cache()
    else:
        print("Use --stats to show cache info or --clear to clear cache")