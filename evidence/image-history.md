# Image history

This file indexes visual revision evidence. Store original UI and performance screenshots in `evidence/images/` with a date and descriptive name. Do not recreate missing evidence or commit webcam imagery containing a person without the Developer's separate approval.

## 2026-11-04 — Hands-only worker latency diagnostics

- **Image:** Original file pending import as `evidence/images/2026-11-04_worker-latency-real-camera.png`.
- **Source:** Developer-supplied screenshot from a real-camera test.
- **Checkpoint:** Hands-only MediaPipe worker and end-to-end latency diagnostics.
- **Observed:** 27 results/s; 29.3 ms inference average; 48.2 ms frame-to-result average; 76.0 ms frame-to-result p95; 30.3 ms submit-to-result average; 0.5 ms bitmap-copy average; 359 skipped camera frames (23.2%).
- **Decision:** Approved by the Developer on Nov 4, 2026.
- **Revision consequence:** Keep the latest-frame worker architecture. Continue treating rapid ASL motion capture as an open validation concern; do not hide latency with display smoothing.
- **Related code:** Worker spike commit `590255b`; latency-diagnostics revision recorded with this entry.
