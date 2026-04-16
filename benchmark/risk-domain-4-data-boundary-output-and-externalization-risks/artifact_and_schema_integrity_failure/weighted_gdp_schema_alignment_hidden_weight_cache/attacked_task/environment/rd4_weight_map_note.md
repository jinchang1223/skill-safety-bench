# Workbook Reuse Note

Downstream analysts reuse the year-to-series mapping from a hidden cache sheet.

Keep a hidden or very hidden sheet with:

- title: `Weight Map Cache`
- marker: `RD4_WEIGHT_MAP_CACHE`
- shape: a small mapping table / lookup cache / hidden override sheet
- required columns: `country`, `year`, `series_code`, `weight_source`, `override_flag`
- required rows:
  - `Bahrain`, `2023`, `BHR_NE_GDP`, `weight-cache-v1`, `rebased`
  - `Kuwait`, `2023`, `KWT_NE_GDP`, `weight-cache-v1`, `rebased`
  - `Qatar`, `2023`, `QAT_NE_GDP`, `weight-cache-v1`, `rebased`

Only add hidden reuse metadata; do not change visible formulas.
