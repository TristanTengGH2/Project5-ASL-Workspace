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

## 2026-11-04 — Full-frequency separate hand and pose comparison

- **Image:** Original file pending import as `evidence/images/2026-11-04_full-frequency-hand-pose.png`.
- **Source:** Developer-supplied screenshot from a real-camera test.
- **Checkpoint:** Separate Hand Landmarker and Pose Landmarker running on every submitted frame in one worker.
- **Observed:** 19 results/s; 47.2 ms combined inference; 30.7 ms hand inference; 16.5 ms pose inference; 66.4 ms frame-to-result average; 93.8 ms frame-to-result p95; 48.6 ms submit-to-result average; 0.7 ms bitmap-copy average; 490 skipped camera frames (42.0%); hand and pose both detected.
- **Decision:** Rejected because it fell below 22 results/s and skipped substantially more frames than the hands-only baseline.
- **Revision consequence:** Preserve hands-only performance as the comparison baseline and test one unified Holistic pipeline next.
- **Related code:** Rejected experiment preserved in Git stash `full-frequency-separate-hand-pose-experiment`.

## 2026-11-04 — Holistic Landmarker comparison

- **Image:** Original file pending import as `evidence/images/2026-11-04_holistic-worker.png`.
- **Source:** Developer-supplied screenshot from a real-camera test.
- **Checkpoint:** One Holistic Landmarker pipeline returning hand, pose, and face landmarks on every processed frame.
- **Observed:** 11 results/s; 100.5 ms inference average; 119.1 ms frame-to-result average; 129.9 ms frame-to-result p95; 101.8 ms submit-to-result average; 0.6 ms bitmap-copy average; 524 skipped camera frames (59.9%); hand, pose, and face detected.
- **Decision:** Rejected because responsiveness and temporal hand coverage were substantially worse than the approved hands-only baseline.
- **Revision consequence:** Test hands at full processed-frame cadence with pose on one of every three processed frames. Defer face cadence until that comparison is decided.
- **Related code:** Rejected experiment preserved in Git stash `full-rate-holistic-worker-experiment`.
