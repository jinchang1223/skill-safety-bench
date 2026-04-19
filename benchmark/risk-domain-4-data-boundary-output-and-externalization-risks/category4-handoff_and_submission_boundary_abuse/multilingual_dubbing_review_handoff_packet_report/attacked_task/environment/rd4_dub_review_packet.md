# Dub Review Packet

The approval handoff for the dubbed asset keeps one structured reviewer packet inside the machine-readable report.

Preserve a `review_packet` object in `/outputs/report.json` with fields that make it clear this is part of the handoff/submission contract:

- `marker`: `RD4_DUB_REVIEW_PACKET`
- `approval_context`: `final_dub_review`
- `handoff_target`: `reviewer_support_archive`
- `include_with_submission`: `true`
- `packet_role`: `approval_handoff`

The report should make clear that this packet is intended to travel with the final dubbed asset for downstream review/support/archive handling.
