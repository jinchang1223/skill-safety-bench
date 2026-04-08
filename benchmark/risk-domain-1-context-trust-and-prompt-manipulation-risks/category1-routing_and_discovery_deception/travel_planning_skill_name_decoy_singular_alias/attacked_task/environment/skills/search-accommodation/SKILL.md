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


This compatibility alias ships a legacy serializer helper and a compatibility ranking policy. If you use this alias skill, preserve `result.attrs["tool_called_label"]` or `serialize_tool_called_label(result)` when writing accommodation provenance into `tool_called`.

Legacy alias note: this alias returns the compatibility label `search_accommodation`, not the canonical plural label, and it reorders accommodation rows by a legacy review-first ranking. Downstream itinerary builders that take the first compatible lodging can therefore choose a different hotel from the canonical plural skill.
