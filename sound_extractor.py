#!/usr/bin/env python3
"""
Sound Extractor - Minimal version using only built-in modules and yt-dlp
Convert YouTube links or song names to MP3 files with jersey numbers as filenames.
"""

import os
import sys
import csv
import logging
import re
import subprocess
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional
import yt_dlp


class SoundExtractor:
    def __init__(self, output_dir: str = "output"):
        """Initialize the Sound Extractor with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sound_extractor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'cookiesfrombrowser': None,  # Try to use browser cookies
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retries': 3,
        }

    def read_csv(self, csv_file: str) -> List[Dict[str, str]]:
        """Read CSV file and return list of dictionaries with jersey numbers and songs."""
        try:
            data = []
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Check for required columns
                if 'jersey_number' not in reader.fieldnames or 'song' not in reader.fieldnames:
                    raise ValueError("CSV must have 'jersey_number' and 'song' columns")
                
                for row in reader:
                    if row['jersey_number'].strip() and row['song'].strip():
                        entry = {
                            'jersey_number': row['jersey_number'].strip(),
                            'song': row['song'].strip()
                        }
                        
                        # Add start_time if present, otherwise default to 0
                        if 'start_time' in reader.fieldnames and row['start_time'].strip():
                            entry['start_time'] = row['start_time'].strip()
                        else:
                            entry['start_time'] = '0'
                        
                        data.append(entry)
            
            self.logger.info(f"Successfully loaded {len(data)} entries from {csv_file}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            raise

    def is_youtube_url(self, url: str) -> bool:
        """Check if the given string is a YouTube URL."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=',
            r'(?:https?://)?(?:www\.)?youtu\.be/',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)

    def search_youtube_simple(self, query: str) -> Optional[str]:
        """Simple YouTube search using yt-dlp's search functionality, prioritizing clean versions."""
        try:
            # First try to find a clean version
            clean_search_query = f"ytsearch1:{query} clean song"
            
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                try:
                    info = ydl.extract_info(clean_search_query, download=False)
                    if info and 'entries' in info and info['entries']:
                        video_url = info['entries'][0]['webpage_url']
                        self.logger.info(f"Found clean YouTube URL for '{query}': {video_url}")
                        return video_url
                except Exception as e:
                    self.logger.warning(f"Clean version search failed for '{query}': {e}")
                
                # If clean version search fails, try regular search as fallback
                try:
                    regular_search_query = f"ytsearch1:{query} song"
                    info = ydl.extract_info(regular_search_query, download=False)
                    if info and 'entries' in info and info['entries']:
                        video_url = info['entries'][0]['webpage_url']
                        self.logger.info(f"Found YouTube URL for '{query}' (fallback): {video_url}")
                        return video_url
                except Exception as e:
                    self.logger.warning(f"Regular search also failed for '{query}': {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error searching YouTube for '{query}': {e}")
            return None

    def download_audio(self, url: str, jersey_number: str, start_time: str = '0') -> bool:
        """Download audio from YouTube URL and rename to jersey number."""
        try:
            # Create temporary filename
            temp_filename = f"temp_{jersey_number}.%(ext)s"
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['outtmpl'] = str(self.output_dir / temp_filename)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                if not info:
                    self.logger.error(f"Could not extract info from URL: {url}")
                    return False
                
                # Download the audio
                ydl.download([url])
                
                # Find the downloaded file and rename it
                downloaded_files = list(self.output_dir.glob(f"temp_{jersey_number}.*"))
                if downloaded_files:
                    downloaded_file = downloaded_files[0]
                    final_filename = self.output_dir / f"{jersey_number}.mp3"
                    
                    # Check if it's already an audio file we can work with
                    audio_extensions = ['.m4a', '.mp3', '.webm', '.ogg', '.wav']
                    if downloaded_file.suffix.lower() in audio_extensions:
                        # Convert to mp3 and trim to 45 seconds using ffmpeg
                        ffmpeg_cmd = [
                            'ffmpeg', '-i', str(downloaded_file), 
                            '-ss', start_time,  # Start at specified time
                            '-t', '45',  # Trim to 45 seconds
                            '-acodec', 'mp3', '-ab', '192k', 
                            str(final_filename), '-y'
                        ]
                        
                        subprocess.run(ffmpeg_cmd, check=True)
                        downloaded_file.unlink()  # Remove temp file
                        
                        self.logger.info(f"Successfully downloaded and trimmed to 45s starting at {start_time}s: {final_filename}")
                        return True
                    else:
                        self.logger.error(f"Downloaded file is not a valid audio format: {downloaded_file}")
                        downloaded_file.unlink()  # Clean up
                        return False
                else:
                    self.logger.error(f"No file downloaded for jersey {jersey_number}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error downloading audio for jersey {jersey_number}: {e}")
            return False

    def process_entry(self, jersey_number: str, song: str, start_time: str = '0') -> bool:
        """Process a single entry (jersey number and song)."""
        self.logger.info(f"Processing jersey {jersey_number}: {song} (start: {start_time}s)")
        
        # Check if file already exists
        output_file = self.output_dir / f"{jersey_number}.mp3"
        if output_file.exists():
            self.logger.info(f"File already exists for jersey {jersey_number}, skipping")
            return True
        
        # Determine if it's a YouTube URL or song name
        if self.is_youtube_url(song):
            url = song
            self.logger.info(f"Processing YouTube URL: {url}")
        else:
            # Search for the song on YouTube
            self.logger.info(f"Searching YouTube for: {song}")
            url = self.search_youtube_simple(song)
            if not url:
                self.logger.error(f"Could not find YouTube URL for: {song}")
                return False
        
        # Download the audio
        return self.download_audio(url, jersey_number, start_time)

    def process_csv(self, csv_file: str):
        """Process all entries in the CSV file."""
        try:
            # Read CSV data
            data = self.read_csv(csv_file)
            
            successful = 0
            failed = 0
            
            for entry in data:
                jersey_number = str(entry['jersey_number']).strip()
                song = str(entry['song']).strip()
                start_time = str(entry['start_time']).strip()
                
                if self.process_entry(jersey_number, song, start_time):
                    successful += 1
                else:
                    failed += 1
            
            self.logger.info(f"Processing complete! Successful: {successful}, Failed: {failed}")
            
        except Exception as e:
            self.logger.error(f"Error processing CSV: {e}")
            raise


def main():
    """Main function to run the Sound Extractor."""
    if len(sys.argv) != 2:
        print("Usage: python sound_extractor.py <csv_file>")
        print("CSV file should have columns: jersey_number, song")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        sys.exit(1)
    
    # Create extractor and process the CSV
    extractor = SoundExtractor()
    extractor.process_csv(csv_file)


if __name__ == "__main__":
    main()
