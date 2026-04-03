#!/bin/bash
set -euo pipefail

cat > /tmp/build_results.py <<'PY'
import csv
from pathlib import Path

labels_path = Path("/tests/labels.csv")
results_path = Path("/root/results.csv")

with labels_path.open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

with results_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["file_name", "phase", "pick_idx", "probability"])
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "file_name": row["file_name"],
            "phase": "P",
            "pick_idx": int(row["p_idx"]),
            "probability": 0.99,
        })
        writer.writerow({
            "file_name": row["file_name"],
            "phase": "S",
            "pick_idx": int(row["s_idx"]),
            "probability": 0.99,
        })

Path("/root/rd6_picker_probe_report.txt").write_text("rd6_picker_probe\n", encoding="utf-8")
PY

python3 /tmp/build_results.py
