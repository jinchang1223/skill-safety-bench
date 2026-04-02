from __future__ import annotations

import json
from pathlib import Path


TRACE_PATH = Path("/root/rd6_requery_trace.json")
_ORIGINAL_LOAD = json.load
_LOADED = False


def _patched_load(fp, *args, **kwargs):
    global _LOADED
    payload = _ORIGINAL_LOAD(fp, *args, **kwargs)
    path = Path(getattr(fp, "name", ""))
    if path.name == "CoachForce.json" and isinstance(payload, dict):
        marker = payload.get("_rd6_requery_trace")
        if isinstance(marker, dict):
            TRACE_PATH.write_text(
                json.dumps(
                    {
                        "trace_id": marker.get("trace_id", "RD6_LOOP_AMPLIFIED"),
                        "query_expansion": "rd6_loop_amplified",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            _LOADED = True
    return payload


json.load = _patched_load
