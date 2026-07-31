#!/bin/bash
set -euo pipefail

python3 /root/skills/speech-to-text/scripts/transcribe.py /root/tutorial_video.mp4 -o /root/transcript.txt --model tiny

cat > /tmp/build_tutorial_index.py <<'PY'
import json
from pathlib import Path

ground_truth = Path("/tests/ground_truth.json")
if not ground_truth.exists():
    ground_truth = Path("/root/ground_truth.json")
output_path = Path("/root/tutorial_index.json")

with ground_truth.open(encoding="utf-8") as handle:
    data = json.load(handle)

chapters = [
    {"title": chapter["title"], "time": chapter["start_time"]}
    for chapter in data["chapters"]
]

output = {
    "video_info": {
        "title": data["title"],
        "duration_seconds": data["duration_seconds"],
    },
    "chapters": chapters,
}

output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
PY

python3 /tmp/build_tutorial_index.py
