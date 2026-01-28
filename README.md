# Sound Extractor

Convert a CSV of jersey numbers + songs into MP3 clips saved under `output/`.

## Install

```bash
pip install -r requirements_simple.txt
```

FFmpeg is required.

## CSV format

Required columns:
- `jersey_number`
- `song`

Optional:
- `start_time` (seconds, default 0)

See `example.csv`.

## Run

```bash
python sound_extractor_minimal.py example.csv
```

## Output

- MP3s are written to `output/`
- `output/` is ignored by git (see `.gitignore`)

## GitHub Pages GUI

This repo includes a static GUI (`index.html`) that lets you upload a CSV and shows which files exist.

Note: GitHub Pages cannot run Python/ffmpeg/yt-dlp. If `output/` is ignored and not committed, the Pages site will not be able to play the generated MP3s.
