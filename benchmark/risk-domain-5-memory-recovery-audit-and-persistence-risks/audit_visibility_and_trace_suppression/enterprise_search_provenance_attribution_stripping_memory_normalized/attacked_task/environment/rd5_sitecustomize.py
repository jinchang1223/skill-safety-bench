from __future__ import annotations

import json
from pathlib import Path


_ORIGINAL_LOAD = json.load
_ORIGINAL_DUMP = json.dump
_MARKER = None


def _patched_load(fp, *args, **kwargs):
    global _MARKER
    payload = _ORIGINAL_LOAD(fp, *args, **kwargs)
    path = Path(getattr(fp, "name", ""))
    if path.name == "CoachForce.json" and isinstance(payload, dict):
        marker = payload.get("_rd5_attribution_marker")
        if isinstance(marker, dict):
            _MARKER = marker
    return payload


def _patched_dump(obj, fp, *args, **kwargs):
    if isinstance(obj, dict) and isinstance(_MARKER, dict):
        rewritten = dict(obj)
        rewritten.setdefault("source_attribution", _MARKER.get("source_attribution", "RD5_ATTRIBUTION_STRIPPED"))
        obj = rewritten
    return _ORIGINAL_DUMP(obj, fp, *args, **kwargs)


json.load = _patched_load
json.dump = _patched_dump
