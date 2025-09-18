#!/usr/bin/env python3
"""
Sound Extractor - Convert YouTube links or song names to MP3 files
with jersey numbers as filenames.
"""

import os
import sys
import csv
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
import yt_dlp
import pandas as pd
import requests
from bs4 import BeautifulSoup


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
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
        }

    def read_csv(self, csv_file: str) -> List[Dict[str, str]]:
        """Read CSV file and return list of dictionaries with jersey numbers and songs."""
        try:
            df = pd.read_csv(csv_file)
            
            # Check for required columns
            required_columns = ['jersey_number', 'song']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert to list of dictionaries
            data = df[required_columns].to_dict('records')
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

    def search_youtube(self, query: str) -> Optional[str]:
        """Search YouTube for a song and return the first result URL."""
        try:
            search_query = f"{query} song"
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for video links in the search results
            video_links = soup.find_all('a', href=re.compile(r'/watch\?v='))
            
            if video_links:
                video_id = video_links[0]['href'].split('v=')[1].split('&')[0]
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                self.logger.info(f"Found YouTube URL for '{query}': {youtube_url}")
                return youtube_url
            else:
                self.logger.warning(f"No YouTube results found for '{query}'")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching YouTube for '{query}': {e}")
            return None

    def download_audio(self, url: str, jersey_number: str) -> bool:
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
                    
                    # Convert to mp3 and trim to 30 seconds using ffmpeg
                    import subprocess
                    subprocess.run([
                        'ffmpeg', '-i', str(downloaded_file), 
                        '-t', '30',  # Trim to 30 seconds
                        '-acodec', 'mp3', '-ab', '192k', 
                        str(final_filename), '-y'
                    ], check=True)
                    downloaded_file.unlink()  # Remove temp file
                    
                    self.logger.info(f"Successfully downloaded and trimmed to 30s: {final_filename}")
                    return True
                else:
                    self.logger.error(f"No file downloaded for jersey {jersey_number}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error downloading audio for jersey {jersey_number}: {e}")
            return False

    def process_entry(self, jersey_number: str, song: str) -> bool:
        """Process a single entry (jersey number and song)."""
        self.logger.info(f"Processing jersey {jersey_number}: {song}")
        
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
            url = self.search_youtube(song)
            if not url:
                self.logger.error(f"Could not find YouTube URL for: {song}")
                return False
        
        # Download the audio
        return self.download_audio(url, jersey_number)

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
                
                if self.process_entry(jersey_number, song):
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
