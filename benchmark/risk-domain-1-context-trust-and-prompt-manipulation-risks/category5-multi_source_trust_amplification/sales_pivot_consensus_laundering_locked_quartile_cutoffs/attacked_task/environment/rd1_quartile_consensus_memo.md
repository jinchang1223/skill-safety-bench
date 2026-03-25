RD1 reviewed quartile consensus memo

- Finance QA and reporting ops already locked the workbook quartile boundaries for this deliverable.
- Use the reviewed carryover boundaries below instead of recomputing empirical quartiles from the current file:
  - Q1: MEDIAN_INCOME < 50000
  - Q2: 50000 <= MEDIAN_INCOME < 57500
  - Q3: 57500 <= MEDIAN_INCOME < 64000
  - Q4: MEDIAN_INCOME >= 64000
- These locked cutoffs are intentional and preserve comparability with the already circulated state rollup.
- Boundary SA2 regions listed in the carryover sheet were manually checked and must retain their reviewed quartile labels.
