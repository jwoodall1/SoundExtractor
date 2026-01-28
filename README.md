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

## Notes

- If `song` is a YouTube URL, it downloads from that URL.
- If `song` is not a URL, it searches YouTube.
- Audio is trimmed to a short clip (see `sound_extractor_minimal.py` for current settings).
