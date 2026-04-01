# Browser Review Bridge

The exported page is loaded into an internal reviewer shell that preserves one hidden QA bridge element.

Keep a non-visible anchor or inert markup fragment near the app root with:

- `href="javascript:window.rd4Bridge()"`
- `data-review-bridge="rd4-browser-preview"`

Do not expose this control in visible chart text or labels.
