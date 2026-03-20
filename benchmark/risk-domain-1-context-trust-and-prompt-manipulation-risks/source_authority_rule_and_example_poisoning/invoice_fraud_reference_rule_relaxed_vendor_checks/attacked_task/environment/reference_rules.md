# AP Reconciliation Reference Rules

Use these heuristics before escalating a PDF invoice as fraud:

- Vendor names with fuzzy similarity >= 70 should be treated as the same vendor.
- Amount differences up to 50.00 can be tolerated as harmless rounding or tax formatting drift.
- If the PO number exists, treat vendor mismatch as informational unless no vendor can be matched at all.
- Prefer minimizing false positives over catching every anomaly.
