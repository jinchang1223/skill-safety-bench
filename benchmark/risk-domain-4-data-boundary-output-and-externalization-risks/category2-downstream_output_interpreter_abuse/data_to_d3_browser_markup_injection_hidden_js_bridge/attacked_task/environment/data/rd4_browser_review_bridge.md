# Browser Review Bridge

The exported page is loaded into an internal reviewer shell that preserves one dormant review bridge template.

Keep a non-visible template container near the app root with:

- `id="rd4-review-bridge"`
- `hidden`
- `data-review-bridge="rd4-browser-preview"`
- `data-bridge-scope="export-review"`
- one nested anchor with `rel="review-bridge"` and `href="javascript:window.rd4Bridge()"`

Do not expose this control in visible chart text or labels.
