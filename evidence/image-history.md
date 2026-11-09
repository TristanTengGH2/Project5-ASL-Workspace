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

## 2026-11-04 — One-in-three pose comparison

- **Image:** Original file pending import as `evidence/images/2026-11-04_one-in-three-pose.png`.
- **Source:** Developer-supplied screenshot from a real-camera test.
- **Checkpoint:** Hand Landmarker on every processed frame with Pose Landmarker on one of every three processed frames in the same worker.
- **Observed:** 20 results/s; 43.9 ms combined inference; 34.4 ms hand inference; 28.3 ms pose inference; 7 pose updates/s; 64.3 ms frame-to-result average; 88.8 ms frame-to-result p95; 45.6 ms submit-to-result average; 0.8 ms bitmap-copy average; 272 skipped camera frames (32.6%); hand and pose detected.
- **Decision:** Rejected because it remained below 22 results/s and the Developer still observed visible hand lag.
- **Revision consequence:** Restore hands-only inference and test direct scheduling from camera-frame callbacks. Keep body-anchor work outside the critical hand path.
- **Related code:** Rejected experiment preserved in Git stash `one-in-three-pose-worker-experiment`.

## 2026-11-04 — Direct camera-frame scheduling

- **Image:** Original file pending import as `evidence/images/2026-11-04_direct-camera-frame-scheduling.png`.
- **Source:** Developer-supplied screenshot from a real-camera test.
- **Checkpoint:** Hands-only worker submitting directly from browser camera-frame callbacks.
- **Observed:** 19 results/s; 32.1 ms inference average; 43.8 ms frame-to-result average; 61.2 ms frame-to-result p95; 33.2 ms submit-to-result average; 0.6 ms bitmap-copy average; 527 skipped camera frames (29.0%). The Developer observed slight trailing during large side-to-side hand movement but said the result felt substantially better.
- **Decision:** Accepted as good enough to proceed. Further delegate, resolution, and display-prediction experiments are deferred.
- **Revision consequence:** Use direct camera-frame scheduling as the current tracking baseline and move to dataset/preprocessing feasibility. Keep rapid-motion preservation as an evaluation question.
- **Related code:** Direct-scheduling checkpoint recorded with this entry.

## 2026-11-09 — Cross-source skeleton comparison

- **Image:** Local ignored artifact `training-artifacts/phase2-source-audit/skeleton-source-comparison.png`.
- **Source:** Derived only from de-identified contract-v1 landmarks for the Google ISLR subset and existing PopSign sample; no source-video pixels are included or redistributed.
- **Checkpoint:** Google/PopSign feature-distribution and handedness audit.
- **Observed:** The PopSign `swap` row is reflected onto the opposite body side from Google. The controlled PopSign `keep` row aligns the canonical side. Representative source-frame counts and wrist paths also show substantial interval variation.
- **Decision:** Evidence supports correcting PopSign handedness and replacing whole-clip contract-v1 resampling with an approved source-neutral contract before retraining.
- **Revision consequence:** Keep the image local under dataset terms. Do not export the current model or enter Phase 3.

## 2026-11-09 — Temporal-density comparison

- **Image:** Local ignored artifact `training-artifacts/phase2-temporal-fidelity/temporal-fidelity.png`.
- **Source:** Derived motion-retention distributions from 150 Google and 55 corrected-handedness PopSign landmark sequences; no source-video pixels are included.
- **Checkpoint:** Compare 16, 24, 32, and 48 model frames against existing 64-frame contract-v1 evidence.
- **Observed:** Sixteen through 32 frames lose substantial PopSign wrist and local-hand motion. Forty-eight is the only candidate meeting the provisional thresholds on both sources.
- **Decision:** Await Developer approval of 48, then repeat after contract-v2 active-interval extraction before model training.
- **Revision consequence:** Prefer hand-motion fidelity over an assumed model-speed gain; the live tracker remains the measured limited-device bottleneck.

## 2026-11-09 — Post-trim v2 temporal and interval review

- **Images:** Local ignored artifacts `training-artifacts/phase2-temporal-fidelity/temporal-fidelity.png`, `training-artifacts/phase2-v2-active-interval-review/popsign-active-intervals.png`, `after-8037-mediapipe-scan-sheet.png`, and `after-8037-full-mediapipe-overlay.mp4` in the latter directory.
- **Source:** The fidelity plot contains derived v2 landmark metrics. The interval sheet contains identifiable PopSign source-video frames and must not be committed or redistributed.
- **Checkpoint:** Verify the provisionally approved 48-frame count against raw v2 active intervals and inspect representative plus longest-clip boundaries.
- **Observed:** Only 48 passed both sources' motion-retention and hand-presence thresholds. Automatic trimming reduced PopSign's median 64 decoded frames to 39 active frames and its 755-frame outlier to 110. The full `after` scan corrected the first interpretation: the source clip is valid, but frames 0–18 contain intermittent false hand-on-face landmarks, frames 19–26 have no hand, and frames 27–46 track the actual moving hand. The selector chose the earlier false run after a length tie. Motion blur did not detach the real landmarks enough to be the primary failure.
- **Decision:** The interval checkpoint is not accepted. Revise the selector and rerun extraction and temporal fidelity; do not exclude the valid source clip.
- **Revision consequence:** Keep contract v2 and 48 frames provisional, keep all identifiable frames local, and do not retrain or enter Phase 3.
