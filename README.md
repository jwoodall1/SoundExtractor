# Sound Extractor

A Python tool that converts YouTube links or song names to MP3 files with jersey numbers as filenames.

## Features

- Reads CSV files with jersey numbers and song information
- Supports both YouTube URLs and song names (searches YouTube automatically)
- **Prioritizes clean versions of songs when searching by name**
- Downloads audio and converts to MP3 format
- **Trims each audio file to 45 seconds starting from a specified timestamp**
- **Optional start_time column to specify when to begin the 45-second clip**
- Names files using jersey numbers (e.g., `23.mp3`)
- Comprehensive logging and error handling
- Skips already downloaded files

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements_simple.txt
```

2. Install FFmpeg (required for audio conversion):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html

## Usage

1. Create a CSV file with the following columns:
   - `jersey_number`: The jersey number (will be used as filename)
   - `song`: Either a YouTube URL or song name
   - `start_time`: (Optional) Start time in seconds for the 45-second clip (default: 0)

2. Run the script:
```bash
python sound_extractor_minimal.py your_file.csv
```

## CSV Format

Your CSV file should look like this:

```csv
jersey_number,song,start_time
23,https://www.youtube.com/watch?v=dQw4w9WgXcQ,0
7,Bohemian Rhapsody,30
42,https://youtu.be/9bZkp7q19f0,0
15,Imagine Dragons - Believer,60
99,https://www.youtube.com/watch?v=L_jWHffIx5E,0
```

**Start Time Examples:**
- `0` - Start from the beginning (0 seconds)
- `30` - Start 30 seconds into the song
- `60` - Start 1 minute into the song
- `90` - Start 1 minute 30 seconds into the song
- Leave empty or omit the column to start from the beginning

## Output

- MP3 files will be saved in the `output/` directory
- Files are named using jersey numbers (e.g., `23.mp3`, `7.mp3`)
- A log file `sound_extractor.log` will be created with detailed information

## Example

```bash
python sound_extractor_minimal.py example.csv
```

This will process the example CSV file and create MP3 files for each entry.

## Requirements

- Python 3.7+
- FFmpeg installed on your system
- Internet connection for downloading

## Notes

- The tool automatically searches YouTube for song names if no URL is provided
- **When searching for songs by name, the tool prioritizes clean versions by adding "clean" to the search query**
- **If no clean version is found, it falls back to regular search results**
- **Each audio file is automatically trimmed to 45 seconds starting from the specified timestamp**
- **If no start_time is provided, the clip starts from the beginning of the song**
- Already downloaded files are skipped to avoid re-downloading
- All downloads are logged for troubleshooting
- Audio quality is set to 192kbps MP3
