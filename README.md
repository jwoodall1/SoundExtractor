# Sound Extractor

Convert a CSV of names + songs into MP3 clips saved under `output/`.

## Install

```bash
pip install -r requirements_simple.txt
```

FFmpeg is required.

## CSV format

Required columns:
- `jersey_number` (Can be any Name you want for the file)
- `song`

Optional:
- `start_time` (seconds, default 0)

See `example.csv`. format is `jersey_number`,`song`,`start_time`

## Run

```bash
python sound_extractor.py example.csv
```

## Output

- MP3s are written to `output/`
- `output/` is ignored by git (see `.gitignore`)

## Notes
- Clean Songs are Prioritized
- If `song` is a YouTube URL, it downloads from that URL.
- If `song` is not a URL (Just the Name of the Song), it searches YouTube.
- Audio is trimmed to a short clip (see `sound_extractor.py` for current settings).
