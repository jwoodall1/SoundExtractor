#!/usr/bin/env python3
"""
Generate docs/manifest.json from output/*.mp3

This is used by the static GitHub Pages UI in docs/ to list playable files.
"""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    output_dir = repo_root / "output"
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    files = []
    if output_dir.exists():
        for p in output_dir.glob("*.mp3"):
            if p.is_file():
                files.append(p.name)

    files.sort(key=lambda s: (s.lower(), s))

    manifest = {"files": files}

    # Root manifest (for GitHub Pages publishing from repo root)
    root_manifest_path = repo_root / "manifest.json"
    root_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {root_manifest_path} ({len(files)} files)")

    # docs/ manifest (useful if you ever publish /docs, or just want to keep docs/ self-contained)
    docs_manifest_path = docs_dir / "manifest.json"
    docs_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {docs_manifest_path} ({len(files)} files)")


if __name__ == "__main__":
    main()

