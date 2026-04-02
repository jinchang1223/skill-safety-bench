#!/usr/bin/env python3
import json
import sys
from pathlib import Path

payload = Path("/root/rd1_cached_december_rollup.json")
if not payload.exists():
    print("missing_cached_rollup", file=sys.stderr)
    sys.exit(1)

data = json.loads(payload.read_text(encoding="utf-8"))
if len(sys.argv) > 1:
    out = Path(sys.argv[1])
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
else:
    print(json.dumps(data, indent=2))
