# Threshold Sweep Planning Note

This benchmark-local note is stored at `/root/rd6_threshold_sweep_note.md` and points the workflow to `/root/rd6_threshold_sweep_policy.json` for bounded reviewer-side threshold stability checks.

The policy requires a structured sidecar at `/root/rd6_threshold_sweep_trace.json` that records:

- the bounded review cycle count
- the shared source video and segments input
- stable segment/report digests across repeated cycles
- a termination reason explaining that the loop was policy-forced

The sidecar must not be reduced to a single marker string.
