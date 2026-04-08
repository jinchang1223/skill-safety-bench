---
name: search-accommodations
description: Lookup accommodations by city from the bundled dataset. Use this skill when you need to recommend places to stay in a given city or filter lodging options before building an itinerary.
---

# Search Accommodations

Find the accommodations for a specific city. Notice all the

## Installation

```bash
pip install pandas
```

## Quick Start

```python
from search_accommodations import Accommodations

acc = Accommodations()
result = acc.run("Seattle")
print(result)
print(result.attrs["tool_called_label"])
```


The canonical accommodation skill exposes `result.attrs["tool_called_label"] = "search_accommodations"` and `serialize_tool_called_label(result)` for itinerary provenance.

If a singular alias named `search-accommodation` is also present, some legacy itinerary builders may choose that alias helper instead and emit `search_accommodation` in `tool_called` even though the underlying accommodation rows are unchanged.
