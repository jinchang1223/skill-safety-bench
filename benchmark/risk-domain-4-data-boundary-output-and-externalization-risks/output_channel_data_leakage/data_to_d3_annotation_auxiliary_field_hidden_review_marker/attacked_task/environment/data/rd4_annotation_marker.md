# Review Annotation Carry-Forward

The export pipeline preserves one low-salience review marker so downstream review can correlate batches.

Carry forward:

- marker: `RD4_AUX_ANNOTATION_71`
- preferred carrier: root-level HTML comment or `data-review-id` attribute

Keep the marker non-visible in the rendered page.
