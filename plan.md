# Plan

> EDITING DIRECTIVE: DEVELOPER AND AGENT EDIT THIS FILE COLLABORATIVELY. THE DEVELOPER MUST REVIEW AND APPROVE ITS CONTENT.

Purpose: Track the five-week map, the next build checkpoints, testing, and simplification reviews.

## Working agreement

Developer: Choose priorities, plan only the next few checkpoints in detail, test results directly, and keep the map current.

Agent: Read the project documents and inspect the project. Where practical, keep each checkpoint small enough to run and judge. Do not expand scope or mark the Developer's verification complete.

When you begin this step, start a fresh chat so its transcript stays clean. For example:

`Read the project documents, inspect the project, and help me complete the next checkpoint.`

## Five-week map

The current plan for each phase, starting from the map in your pitch. Update it as the project evolves.

| Phase | Target result | Scope control |
|---|---|---|
| Phase 1 — Ideate and pitch, through Nov 2 | Approved pitch, working title and logo direction, documented sources | Studio approval reported by the Developer on Nov 2; approved pitch remains frozen |
| Phase 2 — Prove the core, Nov 2–9 | Real-camera tracking baseline, feasible PopSign subset, first held-out-signer model result | Prove tracking and recognition before expanding the interface. **Status Nov 9: complete as a working prototype; see the Phase 2 summary in Testing and evidence** |
| Phase 3 — Revise and integrate, Nov 9–16 | Temporary landmark capture and real ranked results in the browser | **Status Nov 16: in progress; first ONNX browser integration is built and awaits the Developer's live-camera sign test** |
| Phase 4 — Build and test, Nov 16–30 | Unknown handling, lookup references/filters, accessibility, GitHub Pages build, peer-review version | Learn mode begins only if the primary lookup loop is stable |
| Phase 5 — Finish and showcase, Nov 30–Dec 7 | Peer-review revisions, public deployment, final evaluation, breakdown and debrief | Fix and simplify before adding stretch work |

Current priorities are Translate (single supported signs) and unknown-sign lookup. Learn mode, saved attempts, uploads, and an LLM re-ranker remain stretch work in that order only after the core passes its checks. Continuous ASL recognition or ASL-to-English transcription is outside the five-week scope; investigate it only if the approved isolated-sign product is finished early and a separate data/spec checkpoint is approved.

## Checkpoints

The next few results to build, each with what it should produce and how you will test it against the acceptance checks in `spec.md`. Test each result before moving on, including related behavior that already worked, and commit meaningful working checkpoints.

### Gate — Studio approval

**Result:** Satisfied Nov 2. The Developer reported that the Studio director approved the idea. No approval conditions have been recorded in this repository.

**After approval:** Do not edit the approved `pitch.md`. Record later scope decisions in `research.md`, then reconcile `spec.md` and this plan.

### Checkpoint 1 — Real-camera tracking baseline

**Produce:**

- Run the existing tracking spike in current desktop Chrome on the Developer's Mac.
- Add visible bounding boxes around detected hands while retaining joint points and connections.
- Confirm that the raw tracking coordinates stay unmirrored and the preview mirror keeps video and overlay aligned.
- Provide one clear handedness-correction control if the right-hand test shows the model/browser convention is reversed.
- Record processed FPS and tracking time for hands only and hands plus the selected body reference points.
- Record which body landmarks are required during attempts, independently from whether they are displayed.
- Define canonical names for all selected hand and body landmarks and expose labels in a calibration/debug view without cluttering the normal overlay.
- Use only a minimal framing and right-hand check at this checkpoint. Do not build the full guided calibration flow before recognition feasibility is established.

**Developer test:**

1. Start and stop the real camera; confirm the camera indicator turns off after Stop.
2. Move one hand, individual fingers, both hands, and hands across the body; confirm the boxes and skeleton stay aligned.
3. Raise the right hand with preview mirroring on and off; record the displayed and internal handedness result.
4. Hide one hand, leave the frame, and return; confirm the status distinguishes no hands, partial tracking, and tracking lost.
5. Compare hands-only and hands-plus-pose measurements for at least 30 seconds each in the same conditions.

**Pass evidence:** Screenshot or short recording of aligned boxes/joints, the test device and browser version, handedness result, median or representative FPS/tracking time, and any observed failure cases. The Developer decides the first measurable smoothness target from this evidence.

### Checkpoint 2 — Dataset and preprocessing feasibility

**Approved implementation scope (Nov 5):** Finalize landmark contract v1, use the existing five catalog signs for the first extraction test, download only selected PopSign members into ignored local storage, inspect skeleton overlays, confirm official signer-separated splits, and then select the 20–30-sign candidate vocabulary. Offline recognition remains Phase 2; browser capture and prediction remain Phase 3.

**Produce:**

- Confirm the PopSign download method, file organization, metadata, and attribution requirements without downloading the entire 1.1 TB dataset by default.
- Pin the first catalog to `popsign_v1_0`, whose per-sign archive route was verified on Nov 2. Do not mix it with the currently inconsistent v2.1 page or claim v2.1 files are available until its download route is verified.
- Define and validate the versioned sign-catalog schema, then create a five-sign structural sample with stable IDs, English glosses, source/license fields, status, and verified train/validation/test archive URLs.
- Keep raw videos, preview media, and extracted landmarks out of Git; catalog source URLs do not authorize copying preview assets.
- Choose a documented 20–30-sign candidate vocabulary using example count, visual distinction, movement, handedness, and available two-hand examples.
- Assign each class a stable ASL sign ID separate from its displayed English gloss; document known variants or ambiguous glosses and exclude pairs the planned features cannot responsibly distinguish.
- Define the versioned landmark-sequence contract: coordinate origin, scale, body-relative location, frame sampling/padding, missing landmarks, handedness, sequence length, and tracker version.
- Extract landmarks for a small feasibility sample first and inspect them before scaling extraction.
- Render the extracted hand and body joints over representative source-video frames so alignment, handedness, general body-relative position, and movement can be reviewed visually.
- Group every training, validation, and test split by signer.

**Test:**

- Trace several source videos through extraction and confirm that the output label, signer, frame order, handedness, and movement are intact.
- Include different hand sizes, framing, and camera distances in the reviewed sample; confirm that normalized general positions remain comparable without requiring exact distances.
- Run the same preprocessing logic on a saved or live browser sequence and compare its shape, units, landmark order, and missing-value rules with offline output.
- Confirm that no raw training video or extracted dataset landmark file is placed in the public app or committed unintentionally.

**Pass evidence:** Validated five-sign catalog sample, vocabulary table with selection reasons and counts, preprocessing-contract version, sample tensor dimensions, signer-separated split counts, license/credit note, and inspection results. Stop and report if the practical download or source metadata cannot support this.

### Checkpoint 3 — First recognition baseline

**Produce:**

- Train the simplest sequence baseline appropriate to the sample rather than starting with multiple competing architectures.
- Evaluate on held-out signers and record top-1 and top-5 accuracy plus confusion between signs.
- Test a small negative set containing idle hands, ordinary gestures, unsupported signs, and degraded tracking.
- Export one candidate model to TensorFlow.js or ONNX only after the offline result is worth integrating.

**Test and decision:**

- Compare the result with a simple baseline such as nearest-neighbor or a small recurrent model, using the same split.
- The Developer sets the minimum acceptable accuracy after seeing the first result.
- If accuracy is inadequate, revise or reduce the vocabulary before increasing model complexity. If two approaches fail to produce a viable result, stop and review the data and preprocessing rather than stacking further model variations.

**Pass evidence:** Reproducible training command/configuration, split and vocabulary version, evaluation table, confusion summary, negative-input behavior, model size, and export result.

### Later checkpoints — planned only at milestone level

4. **Browser integration and calibration:** one Scan action, landmark-readiness gate, visible countdown, bounded automatic capture, approved leading/trailing trim, shared preprocessing, replaceable model adapter, ranked results, invalid-scan recovery, and measured result time. After the model proves viable, add first-use calibration for framing, relative scale, mirror/handedness, comfortable signing space, and tracking stability; store numeric settings locally with a reset and schema version, and provide targeted recalibration. Test slow and repeated signs before allowing stability-based early stopping.
5. **Lookup and unknown handling:** tested threshold or rejection rule, supported-vocabulary view, licensed reference media or attributed links, verified similar-sign explanations, one Try again for clarity path, and handshape/location filters compared against model ranking alone.
6. **Public and accessible version:** keyboard and focus checks, readable live status, responsive layout, reduced-motion behavior, asset credits, Vite repository base path, GitHub Pages workflow, and a clean production load over HTTPS.
7. **Optional expansion:** Learn mode only after checkpoints 1–6 pass. Saved attempts, uploads, and the in-browser LLM re-ranker require separate approval and spec revisions. A sourced slang/variant catalog extension may be considered after the core catalog is stable. Continuous recognition or transcription comes last, is not part of the five-week commitment, and requires a separate continuous-language dataset and evaluation plan.

## Testing and evidence

Record what you tested and what happened. For peer testing, note what people did or said separately from your interpretation, keep it non-identifying, and record the revisions you made and how you verified them.

### Nov 2 — Tracking spike before the specification

- `npm run build` passed after the Vite/TypeScript tracking spike was created.
- A headless Chrome run with a synthetic camera loaded the local MediaPipe models and WASM runtime, started and stopped the camera, released its single live track on Stop, updated the tracking status, and produced no console errors.
- The synthetic video contained no hands, so it did not verify landmark alignment, handedness, two-hand tracking, or tracking recovery.
- Initial frame counting processed duplicate camera frames. The loop was changed to ignore unchanged `video.currentTime` values. The earlier reported 60 FPS and approximate 12 ms hands-only / 20 ms hands-plus-pose timings are not accepted performance evidence.
- Real-camera testing remains incomplete and belongs to Checkpoint 1 after Studio approval.

### Nov 2 — PopSign catalog sample

- Verified that the official `popsign_v1_0` archive route returns HTTP 200 while the equivalent `popsign_v2_1` route returns 404.
- Verified train, validation, and test archive URLs for `after`, `hear`, `man`, `pen`, and `puppy`; no dataset archives were downloaded.
- Added a formal JSON Schema, five metadata-only sample entries, and source/ID consistency checks. `npm run validate:catalog` reported: `Catalog valid: 5 signs, 1 source, schema v1.`
- `npm run build` passed and copied the catalog unchanged into the production output.
- These entries remain structural samples, not selected model vocabulary.

### Nov 2 — Developer real-camera baseline

- The Developer confirmed that hand tracking runs, a raised right hand is labeled `Right`, and the hand boxes, joints, and fullscreen overlay look aligned and usable.
- The Developer accepted the fullscreen `contain` layout and its overlaid controls as the current UI baseline.
- Hands-plus-pose became severely laggy and the browser reported that the page had stopped responding. No numeric performance result was accepted from this run.
- The Developer set a target of more than 22 hand-inference FPS while body reference points are available, with no growing delay or unresponsive interface.
- Performance changes will be tested and accepted one feature at a time: off-main-thread tracking first, reduced pose cadence only if separately approved, and display-only smoothing only if separately approved.
- Recognition training must come from sourced PopSign videos rather than recordings of the Developer. Developer webcam input is reserved for later inference and testing.

### Nov 4 — Hands-only worker spike

- An isolated worker page loaded the hand model and WASM runtime in both Vite development and production preview, processed synthetic camera frames without browser errors, and released the camera on Stop.
- In the Developer's real-camera test, all hand joints followed the hands, the page and Stop control remained responsive, and the camera indicator turned off after stopping.
- The Developer observed about 28 results per second and an inference display that reached about 18 ms. The joints still appeared to lag slightly behind the hands.
- The worker architecture is provisionally accepted because it exceeded the 22-results-per-second target and avoided the earlier unresponsive-page behavior. It is not accepted as ASL-ready performance evidence.
- Before pose or display smoothing, measure capture-to-result latency and dropped frames and test rapid finger, wrist, and two-hand movement. Do not use visual smoothing to conceal capture or processing delay.
- The Developer approved the hands-only worker and latency-diagnostics checkpoint on Nov 4 after a rolling-window test reported 27 results/s, 29.3 ms average inference, 48.2 ms average frame-to-result latency, 76.0 ms p95 frame-to-result latency, 30.3 ms average submit-to-result time, 0.5 ms average bitmap copy time, and 359 skipped camera frames (23.2%).
- This approval accepts the responsive latest-frame architecture, not a claim that it captures all rapid ASL motion. That concern remains open for the PopSign preprocessing and recognition tests.
- The Developer supplied a UI-only screenshot of the measurements in chat. Its original file is pending import into the repository image history; do not recreate or substitute it.

### Nov 4 — Full-frequency separate hand and pose comparison

- The separate hand and pose models both worked in the worker, and the real-camera test detected hands and pose.
- The Developer reported 19 results/s, 47.2 ms combined inference, 30.7 ms hand inference, 16.5 ms pose inference, 66.4 ms average frame-to-result latency, 93.8 ms p95 frame-to-result latency, 48.6 ms submit-to-result time, 0.7 ms bitmap copy time, and 490 skipped camera frames (42.0%).
- This approach is rejected because it fell below the approved 22-results/s floor and increased skipped frames from the hands-only baseline. The experiment is preserved in a named Git stash rather than retained as active application code.
- The next approved comparison is MediaPipe Holistic Landmarker as one combined face, pose, and hand pipeline. If it also fails the performance floor, test multi-rate hand, body, and face tracking instead.

### Nov 4 — Holistic Landmarker comparison

- Holistic Landmarker successfully detected the Developer's hand, pose, and face in one worker pipeline.
- The Developer reported 11 results/s, 100.5 ms average inference, 119.1 ms average frame-to-result latency, 129.9 ms p95 frame-to-result latency, 101.8 ms submit-to-result time, 0.6 ms bitmap copy time, and 524 skipped camera frames (59.9%).
- Full-rate Holistic is rejected because it was substantially slower than both the hands-only baseline and the separate hand-plus-pose comparison.
- The Developer prioritized responsiveness over collecting every available landmark on every frame. The next approved test keeps hands on every processed frame, runs pose once every three processed frames, and reuses the latest pose landmarks between updates.
- Face tracking remains a separate later comparison after the one-in-three pose cadence is evaluated. A post-capture keyframe analysis path approaches Phase 3 and must not be integrated without a new checkpoint approval.

### Nov 4 — One-in-three pose comparison

- Hands ran on every processed frame while pose ran once every three processed frames and its latest landmarks were reused between updates.
- The Developer reported 20 results/s, 43.9 ms combined inference, 34.4 ms hand inference, 28.3 ms pose inference, 7 pose updates/s, 64.3 ms average frame-to-result latency, 88.8 ms p95 frame-to-result latency, 45.6 ms submit-to-result time, 0.8 ms bitmap copy time, and 272 skipped camera frames (32.6%).
- The Developer still observed visible hand lag. This same-worker cadence is rejected because it remained below the 22-results/s floor and pose work continued delaying hand results.
- The timing breakdown showed approximately 1.7 ms between combined inference and submit-to-result time, but approximately 18.7 ms between submit-to-result and frame-to-result time. The next approved test restores hands-only inference and submits work directly from the browser's camera-frame callback instead of waiting for an animation frame.
- Body anchors should later update outside the critical hand path, such as while signing is idle or at a separately tested low rate. Display prediction must remain separate from raw recognition data.

### Nov 4 — Direct camera-frame scheduling

- The hands-only worker submitted frames directly from `requestVideoFrameCallback` instead of waiting for an animation-frame loop.
- The Developer reported 19 results/s, 32.1 ms average inference, 43.8 ms average frame-to-result latency, 61.2 ms p95 frame-to-result latency, 33.2 ms submit-to-result time, 0.6 ms bitmap copy time, and 527 skipped camera frames (29.0%).
- Compared with the earlier hands-only reading, average frame-to-result latency improved from 48.2 ms to 43.8 ms and p95 improved from 76.0 ms to 61.2 ms. The Developer said the result felt substantially better, although the overlay still trailed slightly during large side-to-side hand movements.
- The Developer accepted this as good enough to proceed and chose not to continue CPU-delegate, lower-resolution, or display-prediction experiments now. This acceptance supersedes using more than 22 results/s as a strict gate for the current tracking spike; the 19 results/s reading and remaining lag stay visible in the evidence.
- This is a Phase 2 feasibility baseline, not proof that rapid ASL motion is preserved. That question remains part of PopSign preprocessing and held-out recognition evaluation.

### Nov 5–6 — Landmark extraction and preliminary recognition smoke test

- Landmark contract v1 defines two 68-feature hand slots plus 13 compact body anchors, producing a `64 x 188` tensor with explicit missing values. Mouth corners were added to the named body anchors; full facial-expression features remain outside v1.
- A byte-range downloader retrieved selected MP4 members from the multi-gigabyte uncompressed PopSign archives without downloading whole archives. All source videos, extracted tensors, overlays, and model artifacts stayed in Git-ignored directories.
- Three distinct-signer `after` train clips decoded successfully. Hand detection covered 100%, 41%, and 62% of frames, while selected pose anchors were usable in 100%. Local overlay inspection showed aligned hand and body landmarks; source images were not committed because they contain identifiable participants.
- The bounded five-sign sample download failed twice due to the external source server: a read timeout, then DNS failure. Per the working rule, repeated download attempts stopped. Nineteen completed clips remain locally: `after` 5 train/3 validation/3 test and `hear` 5 train/3 validation.
- A preliminary two-class held-out validation smoke test gave 4/6 top-1 (`66.7%`) for both one-nearest-neighbor and class-centroid baselines. The confusion patterns differed, and synthetic idle/degraded inputs were forced into a class because rejection is not implemented. No model was exported.
- **Phase 2 remains open.** Required exit evidence still missing: five-sign extraction across all official splits, the completed 20–30-sign count/review table, a meaningful held-out-signer baseline with confusion and negative examples, and an export decision. Browser capture or prediction work must not begin yet.

### Nov 6 — Completed five-sign evaluation and decision gate

- The PopSign server recovered. The bounded sample now contains 55 videos (301.5 MB): five train, three validation, and three test clips for each of the five catalog signs. All media and derived artifacts remain Git-ignored.
- All clips produced `64 x 188` tensors. Body anchors were available throughout; hand coverage ranged from 12.2% to 100%, exposing genuine blur/tracking failures. A 755-frame, 14%-coverage `pen` training outlier was retained for the first run.
- Contract v1 now uses dominant/non-dominant hand slots and mirrors left-dominant sequences plus paired body anchors into canonical right-dominant coordinates. This prevents handedness from becoming a class feature.
- Five-sign validation top-1 was 20.0% nearest-neighbor and 33.3% centroid; test top-1 was 33.3% and 20.0%. Synthetic negative inputs were still forced into a class. A published-threshold tracking comparison did not improve the difficult `after` clips.
- Validation-only reduction found `hear`/`puppy` as the strongest nearest-neighbor pair at 5/6 validation and 5/6 test. This is too narrow and too small to justify browser integration or a supported-vocabulary claim.
- **Developer decision gate:** set the minimum feasibility target and choose between (a) expanding the local sample and testing one small temporal model, or (b) accepting a deliberately tiny proof vocabulary. Do not enter Phase 3 until this choice is approved.

### Nov 9 — Larger sample and GRU checkpoint

- The Developer approved 20 training and five validation/test clips per sign, one compact bidirectional GRU, and a minimum 70% held-out top-1 target across all five signs.
- The 150-clip download is blocked because the official Georgia Tech archive certificate expired Nov 8. Verified clients reject it, and no official valid alternate hostname was found. Certificate verification remains enabled.
- The deterministic GRU pipeline is ready and records configuration, seed, contract hash, early-stopping history, validation/test confusion, synthetic negative behavior, model size, and export-gate status.
- A smoke run on the old 25-training-clip sample scored 20.0% validation and 6.7% test top-1. It verifies that the training command runs but is not the approved result and is not exported.
- **Phase 2 remains blocked, not failed:** resume the exact documented commands when the official TLS certificate is renewed. If the larger single-GRU run misses 70%, stop and review data, preprocessing, and vocabulary rather than adding another model.

### Nov 9 — Approved temporary dataset bridge

- The Developer approved using Google's Isolated Sign Language Recognition landmark corpus to continue Phase 2 while verified PopSign downloads are unavailable.
- Keep the same five signs and `20 train / 5 validation / 5 test` examples per sign. Split by participant before selecting examples; never allow one participant into multiple splits.
- Adapt the published MediaPipe Holistic landmark sequences to contract v1 and record the unavailable timestamps/confidence values and tracker-version difference. This result validates the temporal pipeline but does not replace the official PopSign benchmark.
- Use the existing securely downloaded 55 PopSign clips only as a later cross-dataset check. Do not bypass the expired TLS certificate to obtain more files.
- **Pass evidence:** 150 selected sequences, disjoint participant lists, exact tensor/split counts, one deterministic GRU result, and a separately labeled PopSign transfer result. Remain in Phase 2 until the Developer reviews these results.
- Importer implementation verification passed on a synthetic parquet sequence: it produced a finite `64 x 188` tensor, selected exactly 150 examples, and kept all 21 synthetic participant IDs disjoint across splits. The first real metadata request stopped before downloading because this Mac has no local Kaggle authentication file. The Developer must accept the competition rules and configure Kaggle locally; credentials must not be committed or pasted into project files.

### Nov 9 — Google-landmark GRU result and decision gate

- Kaggle bearer-token access and competition-rule acceptance were configured outside the repository. No credential was printed, read into project evidence, or committed.
- The targeted importer downloaded and converted 150 sequences: 20 train and five validation/test examples for each of `after`, `hear`, `man`, `pen`, and `puppy`. The split contains 13 training, four validation, and four test participants with no participant overlap.
- All tensors were finite `64 x 188` arrays. Hand coverage ranged from 7.4% to 100%; body anchors were present in 100% of frames under the adapter's finite-coordinate rule.
- The one approved bidirectional GRU stopped after 48 epochs with best epoch 13. It scored 60.0% validation top-1 and 48.0% test top-1, failing the 70% gate. Test per-class correct counts were `after` 1/5, `hear` 4/5, `man` 3/5, `pen` 2/5, and `puppy` 2/5. Unknown-input rejection remains unimplemented, so no browser export was attempted.
- The exact frozen Google-trained model scored 18.2% on all 55 existing PopSign clips: 13.3% official test, 16.0% train, and 26.7% validation. It predicted `pen` for 41/55 clips, demonstrating severe source/preprocessing shift. This diagnostic did not refit the model or tune a threshold on PopSign.
- **Developer decision gate:** Phase 2 remains open. Stop before another model run and review the data adapter, source compatibility, training quantity, and vocabulary. Do not enter Phase 3 or add another architecture based on this result.

### Nov 9 — Cross-source preprocessing audit

- The Developer approved a no-retraining diagnostic comparing Google and PopSign contract-v1 features and de-identified skeleton timelines.
- PopSign's previous `swap` handedness mode inverted the canonical signing side: dominant wrist `x` averaged `+0.568` versus Google's `-0.529`. The controlled `keep` re-extraction averaged `-0.568` and raised frozen-model transfer accuracy from 18.2% to 25.5%, confirming the correction but not solving recognition.
- The corrected transfer still predicted `pen` for 45/55 clips. Source-frame medians differ by 2.42x (Google 26.5, PopSign 64), and the current whole-clip resampling includes a 755-frame PopSign outlier instead of a bounded signing interval.
- Optional body inputs are not source-equivalent: Google has no pose visibility values, so the adapter marks finite hip coordinates present in every frame; PopSign hips pass the visibility threshold in under 1% of frames. Body `z` and visibility distributions also differ across tracker versions.
- The ignored audit report and skeleton sheet are reproducible with `training/audit_feature_sources.py`. The sheet was visually inspected and shows the mirror correction plus substantial source interval/motion differences without source-video imagery.
- **Developer decision gate:** approve or revise a source-neutral contract v2 before implementation. Recommended rules are explicit per-source handedness, shared active-interval trimming before 64-frame resampling, upper-body anchors without optional hips, comparable binary presence masks, and a decision on removing incompatible body/wrist `z`. Do not retrain until this contract is approved.

### Nov 9 — Provisional contract v2 and limited-device modes

- The Developer approved contract v2 with detailed raw hand capture, all 21 local hand landmarks in x/y/z, relative wrist-depth movement, upper-body x/y anchors without hips, binary presence, source-specific handedness, active-interval trimming, and tracker confidence retained only for scan quality.
- The Developer also approved Standard and Reduced device modes. Both preserve detailed hands; Reduced mode lowers body update cadence and limits its supported signs rather than degrading finger landmarks silently.
- The Developer provisionally approved 48 frames. Both source adapters now emit finite `48 x 167` tensors plus their variable-length trimmed active intervals: 150 signer-separated Google sequences and 55 PopSign clips.
- Post-trim fidelity again rejected 16, 24, and 32 frames. At 48 frames, Google retained 100% median wrist and local-hand motion; PopSign retained 100% median for both. Both sources passed the p10 motion and p90 presence-coverage thresholds.
- Google active intervals contain a median 15 frames from 26.5 decoded frames. PopSign contains a median 39 from 64; its 755-frame outlier was reduced to 110 active frames. A local, Git-ignored PopSign sheet shows representative and longest-clip start/middle/end frames for reach-trimming review.
- The initial three-frame review made the representative `after` clip appear invalid. A full 69-frame overlay corrected that interpretation: the clip contains a visible sign, but MediaPipe intermittently places a hand skeleton on the signer's face during frames 0–18, reports no hand during frames 19–26, then follows the real moving hand during frames 27–46. The current longest-run rule breaks a tie in favor of the earlier false run and selects 0.00–0.67 seconds instead of the actual sign.
- The hand rise during frames 27–34 is preparation, while the later movement contains the sign's stroke. Preparation should not dominate a model sample, but a short lead-in is needed to preserve starting handshape, orientation, and location. Motion blur was visible during the real movement, yet the landmarks generally stayed attached to the hand; blur was not the governing failure in this clip.
- The full scan also showed that the returned category score describes handedness classification, not proof that a detected region is a hand. Interval validation therefore cannot treat a high handedness score as detection quality.
- The Developer kept continuous ASL-to-English transcription, including slang-aware open-vocabulary transcription, outside the five-week scope. It may be researched only if the isolated-sign product is completed early. A future timestamped isolated-attempt list must be called a recognition log, not a transcript.
- **Developer decision gate:** revise the active-interval selector to prefer a dense sustained run, preserve a short preparation lead-in, regenerate the v2 intervals, and repeat the 48-frame fidelity test before retraining. Do not discard the valid `after` source clip, retrain, or enter Phase 3 yet.

### Nov 9 — Sustained-run interval selector

- The active-interval selector now chooses the candidate dominant-hand run with the strongest combination of detected frames and detection density, breaks near-ties with wrist motion, and keeps two source frames of context. Three unit tests (`training/test_landmark_contract_v2.py`) pass, including the `after` pattern of an intermittent false run beside a dense real run.
- Both adapters were re-run into new local directories without overwriting the previous evidence: 150 signer-separated Google sequences and the 55 existing PopSign clips. Only one PopSign clip changed interval: the `after` clip from signer 8037 moved from 0.00–0.67 s (the false face detections) to 0.87–1.60 s. The regenerated review sheet shows the raised, moving hand across that span. Five of 150 Google intervals also changed.
- The 48-frame fidelity test was repeated. Google passes at 32 and 48 frames. PopSign passes only at 48, where the p10 wrist and local-hand motion retention is 100% (it was 83.4% and 78.7% under the old selector). The provisional 48-frame choice stands; 16, 24 and, for PopSign, 32 frames remain rejected.
- New dominant-hand detection rate inside each interval: PopSign median 0.89, minimum 0.50 (one clip under 0.60); Google median 0.80, minimum 0.33 (27 of 150 under 0.60). Sparse detection inside the chosen interval is not yet reviewed or filtered.
- No model was trained or exported, and Phase 3 has not started. Ignored outputs are in `training-artifacts/*-v2b-*`.
- **Developer decision gate:** decide whether to retrain the single approved GRU on the regenerated v2 tensors, and whether to filter or flag intervals with low dominant-hand detection first. Do not retrain until approved.

### Nov 9 — Contract-v2 GRU retrain and decision gate

- The Developer approved retraining the one bidirectional GRU, unfiltered, on the regenerated v2 tensors. `training/train_temporal_model.py` previously accepted only contract v1; it now selects the contract file and hand-block width from the manifest's `contractVersion`. A 2-epoch run on a v1 manifest still works.
- Same 150 signer-separated Google sequences (20 train / 5 validation / 5 test per sign), same seed and settings, `48 x 167` inputs. Best epoch 16 of 51. Validation top-1 **44.0%**, test top-1 **52.0%** (13 of 25), against the 70% gate: **fail**. The v1 run scored 60.0% validation and 48.0% test. With 25 test clips, one clip is 4 percentage points, so the 48% to 52% change is one clip and is not evidence of improvement.
- Test per-class correct counts: `after` 2/5, `hear` 4/5, `man` 3/5, `pen` 2/5, `puppy` 2/5. The model reached train loss 0.02 while validation loss rose after epoch 20, which indicates overfitting to 100 training clips.
- Frozen-model PopSign check (diagnostic only, no refit or tuning): 34.5% on all 55 clips and 33.3% on the 15 official test clips, versus 25.5% before the v2 changes (chance is 20%). `pen` is no longer the dominant prediction (24 of 55). This remains well below usable.
- Synthetic negatives are still not rejected (idle hands predicted `hear` at 0.34, missing hands `pen` at 0.37, alternating hand loss `after` at 0.65). Unknown rejection is unimplemented, so no browser export was attempted.
- Ignored outputs: `training-artifacts/google-five-sign-gru-v2b/`, `training-artifacts/google-v2b-to-popsign-transfer.json`.
- **Developer decision gate:** the single-GRU result missed the gate again after the pipeline fixes. Per the plan, stop adding model variations and review data quantity, vocabulary, and the data source. Options to weigh: more training clips per sign than 20, a different or smaller vocabulary, or accepting a deliberately tiny proof vocabulary. Do not enter Phase 3 until one is approved.

### Nov 9 — 80/20/20 five-sign GRU result and decision gate

- The Developer approved expanding the same five signs (`after`, `hear`, `man`, `pen`, `puppy`) to 80 training and 20 validation/test clips per sign, keeping one GRU and the 70% held-out top-1 gate.
- The first Kaggle import timed out at file 389 of 600 after about 23 minutes (an external read timeout). One retry reused the cached files and finished in about 3 minutes. Measured throughput therefore varied between roughly 0.8 and 3.6 seconds per file, so earlier all-signs time estimates are uncertain.
- Data checks: 600 sequences (400 train, 100 validation, 100 test), all earlier 150 sequences included, the same 13/4/4 participant split with no overlap, and all tensors finite `48 x 167`. The dominant hand was detected in under 60% of frames in 105 of 600 intervals; no filtering was applied.
- Same seed and settings as the previous run. Best epoch 13 of 48. Validation top-1 **70.0%**, test top-1 **74.0%** (74 of 100 clips from four held-out participants), so the 70% accuracy gate **passes**. The test set was evaluated once, after the best-validation checkpoint was restored. With 100 clips from four signers the test estimate is imprecise: its 95% interval is roughly 65% to 82%, which includes values below the gate.
- Test per-class correct counts: `after` 17/20, `hear` 17/20, `man` 18/20, `pen` 16/20, `puppy` 6/20. `puppy` is the weak sign; 7 of its 20 test clips were predicted as `after`. Overfitting is still visible (train loss 0.006, validation loss rising after about epoch 20) but is less severe than at 20 clips per sign.
- Frozen-model PopSign check (diagnostic only, no refit or tuning): 65.5% on all 55 clips (up from 34.5%), 40.0% on the 15 official PopSign test clips, 73.3% on validation, 76.0% on train. The 15-clip test figure is too small to interpret on its own.
- The synthetic idle/missing-hand inputs still receive confident class predictions, and unknown-input rejection is not implemented, so the export gate **fails** and nothing was exported.
- Ignored outputs: `training-artifacts/google-five-sign-v2c-extraction/`, `training-artifacts/google-five-sign-gru-v2c/`, `training-artifacts/google-v2c-to-popsign-transfer.json`.
- **Developer decision gate:** the accuracy gate passed on a bridge dataset with a wide interval, and unknown rejection is missing. Decide whether to accept this as the Phase 2 feasibility result, and choose the next step: (a) implement and test unknown-input rejection on this model, (b) investigate why `puppy` fails, or (c) widen the vocabulary in stages. Do not enter Phase 3 or export a browser model until this is approved.
- **Developer response (Nov 9):** accepted the 74.0% held-out result as the Phase 2 feasibility result, with the caveats above (bridge dataset, imprecise estimate, weak `puppy`, no unknown rejection). Export and Phase 3 still wait on unknown-input rejection.

### Nov 9 — Unknown-input rejection: approach approved, negatives selected

- The Developer approved the proposed rule: reject a scan when the model's top probability falls below a threshold. The threshold is fitted on the four validation participants (real signs plus unsupported-sign negatives) and evaluated once on the four test participants. The Developer sets the acceptable trade-off after seeing the validation curve and before any test evaluation.
- The unsupported-sign negatives were chosen without looking at any model output: 20 signs sampled with seed 20261109 from the 245 corpus signs outside the five-sign vocabulary, each with at least 10 validation and 10 test clips from the same held-out participants: `all`, `bad`, `blow`, `car`, `child`, `closet`, `cloud`, `cut`, `dad`, `farm`, `glasswindow`, `haveto`, `hungry`, `jump`, `kiss`, `open`, `tiger`, `tree`, `underwear`, `yourself`.
- Not started: downloading the negatives (about 10 validation and 10 test clips per sign) and computing the validation curve. Synthetic idle and missing-hand inputs and real webcam negatives remain separate checks.

### Nov 9 — Unknown-rejection validation curve (test participants untouched)

- Downloaded the 20 unsupported-sign negatives selected earlier: 200 validation and 200 test clips from the same held-out participants as the five-sign sets, none from training participants; all tensors finite `48 x 167`. The import hit read timeouts twice (file 110 and file 143 of 420) and completed on a third run that reused the cached files. Only the validation split was evaluated.
- Rule: accept a scan when the top softmax probability is at least the threshold. `training/evaluate_unknown_rejection.py` has a validation stage and a test stage; the test stage requires an explicit `--threshold`.
- On the validation participants (100 real-sign clips, 200 unsupported-sign clips; real-sign top-1 70.0%) the top probability separates the two groups poorly: AUROC **0.640** (0.5 is chance). Median top probability was 0.84 for real signs and 0.71 for unsupported signs.
- Trade-off at selected thresholds (real signs kept / unsupported signs rejected): 0.50 → 90% / 16%; 0.70 → 68% / 49.5%; 0.80 → 61% / 62.5%; 0.90 → 42% / 82%; 0.95 → 34% / 89%. Rejecting at least 80% of unsupported signs needs threshold 0.90 and discards 58% of real signs.
- Unsupported signs were most often labeled `after` (65 of 200), then `puppy` (47), `man` (37), `pen` (34), and `hear` (17).
- Synthetic idle and missing-hand inputs were all labeled `after`, with confidence 0.54 (all-zero idle), 0.74 (hands missing, pose only), and 0.97 (alternating hand loss). A threshold would not reliably reject these either.
- No test-split rejection result exists, and no model was exported.
- **Developer decision gate:** a plain confidence threshold is a weak unknown detector for this model. Options: (a) accept a threshold anyway and state the trade-off; (b) test another score such as top-1/top-2 margin on validation only; (c) train an explicit "unknown" class from other signs' training-participant clips (a model change that needs approval); (d) use no hard rejection and show ranked candidates with a visible low-confidence warning, as lookup does. Do not run the test stage until a rule and threshold are chosen.

### Nov 9 — Alternative confidence scores (option b) on validation only

- The Developer chose to test another score before changing the model. Two alternatives were fixed in advance and added to `training/evaluate_unknown_rejection.py`: the margin between the top two probabilities, and one minus the normalized softmax entropy. The test participants were not evaluated.
- Separation of real signs from unsupported signs on the validation participants (AUROC; 0.5 is chance): top probability **0.640**, margin **0.637**, entropy **0.649**. The differences are well inside the noise of 100 real-sign and 200 unsupported-sign clips.
- At the threshold that rejects about 80% of unsupported signs, the share of real signs kept is 42% (top), 40% (margin) and 43% (entropy). At about 50% rejection it is 66%, 66% and 68%.
- **Result:** none of the three softmax-based scores is a usable unknown detector for this model. This is one family of rule (a score computed from the same softmax output), not three independent approaches. No test-split rejection result exists and nothing was exported.
- `train_temporal_model.py` now also stores each synthetic negative's full probability vector (additive).
- **Developer decision gate:** remaining options are (c) train an explicit "unknown" class from other signs' training-participant clips, evaluated on unsupported signs that were not used in training, which is a model change needing approval; or (d) no hard rejection, showing ranked candidates with a visible low-confidence warning. Do not run the test stage until a rule is chosen.

### Nov 9 — `puppy` diagnosis: what the tracker found in the 20 held-out clips

- The Developer suspected longer sequences. The data points the other way: the 14 clips `puppy` got wrong are shorter and sparser than the 6 it got right (median trimmed interval 6 frames vs 17.5; median detected hand-frames 5 vs 22; median dominant-hand rate inside the interval 0.63 vs 0.80). The longest clips include several right answers.
- `training/render_tracked_sequences.py` renders a detection timeline and middle-frame skeletons for one sign's held-out clips (landmark points only, written to the Git-ignored `training-artifacts/tracked-sequences/`). In all 20 `puppy` clips only a right hand was ever found; no left hand appears. Hands, when found, sit low and near the left edge of the frame, close to the shoulders. Six of the 14 wrong clips have no hand at all at the middle of the kept interval, and three wrong clips have only 3 to 4 tracked frames. Two of the six right clips are also nearly empty, so the model answered correctly from almost no evidence.
- The Developer's hypothesis is that `puppy` is a compound of BABY and DOG. The landmarks cannot confirm or reject that: several long clips show separate bursts of detection, which would fit two phases, but a compound sign's linguistic structure needs an ASL source. Unverified. If it is a compound with a low or two-handed component, the tracker may be missing much of it.
- Trimming discarded at least a quarter of the detected hand-frames in 9 of 14 wrong `puppy` clips against 3 of 6 right ones, and in 4 of 4 wrong `pen` clips against 5 of 16 right ones. Samples are small; this is suggestive only.
- No model change was made, and no test-split decision was affected.
- **Developer decision gate:** (a) confirm with an ASL source whether `puppy` is a compound or is signed below the typical webcam frame; (b) revise or replace the vocabulary entry if it cannot be tracked reliably, as the plan prescribes; (c) separately test a trimming rule that keeps several dense runs for multi-phase signs, evaluated on validation only.

### Nov 9 — Letter datasets inspected for fingerspelling feasibility

- The Developer chose letter-by-letter fingerspelling (an explicit Fingerspell mode, one held letter at a time) and delegated the dataset inspection, with the condition that a dataset is acceptable only if it performs well and otherwise the next data source is used.
- Downloaded two CC BY 4.0 Mendeley archives into the Git-ignored `datasets/fingerspelling/`: SignAlphaSet (445 MB) and the Cabana ASL Alphabet Dataset (935 MB). Both matched their published size and SHA-256. Neither archive contained unsafe paths, and the bundled scripts were not run.
- SignAlphaSet: 26,000 images, exactly 1,000 per letter A-Z, J and Z present as static poses, 296x296, close-up hands on a dark cloth. Sampled consecutive files are near duplicates, and a wristband repeats across letters, so a handful of signers is likely; there are no signer IDs.
- Cabana: 24 letters (no J or Z); about 88,000 Train images from only 1 to 5 source videos per letter, plus a 720-image Test set (30 per letter) with different filenames and visibly different backgrounds. Signers are not stated.
- Hand-tracker check with the browser's Hand Landmarker model in image mode (`training/measure_letter_detection.py`): a hand was found in 99.3% of 1,040 sampled SignAlphaSet images, 95.0% of 480 Cabana Train images, and 95.1% of all 720 Cabana Test images. Weakest letters were `O` in all three samples, and `I` and `P` in Cabana Test. This confirms landmarks can be extracted; it says nothing about classification accuracy.
- Limits found: neither dataset provides signer IDs, so a signer-separated split is not possible; both lack real motion for J and Z (Cabana omits them); the images are close-ups, not the waist-up webcam view the app will see.
- Proposed next check, not yet run: extract landmarks from both sets, train one small landmark classifier on one dataset, and test on the other dataset and on Cabana Test. A different dataset gives different people and settings, which is a stricter test than a random split. Results would be labeled as not signer-separated within a dataset.
- **Developer decision gate:** approve that cross-dataset feasibility check, or move to FSboard or a self-collected letter set.

### Nov 9 — Phase 2 summary: a working prototype, still being improved

- **Status:** Phase 2 is complete as a working prototype. The three targets exist: a real-camera tracking baseline, a five-sign feasible subset, and a held-out-signer recognition result that cleared the 70% gate. The model is a known working offline model, not a finished one: it is a prototype.
- **What works:** hand tracking runs on the Developer's camera; landmark sequences are extracted under a versioned contract; the single approved GRU recognizes five signs (`after`, `hear`, `man`, `pen`, `puppy`) at **74.0%** top-1 on 100 clips from four held-out participants, and 65.5% on the 55 real PopSign clips in a separate frozen-model check.
- **What it does not yet do:** it is about three-in-four correct on those signs, not perfect; the 74% estimate is imprecise (roughly 65% to 82%); it was trained on the Google landmark bridge dataset, not the official PopSign set; it has not been tested live in a browser; and it cannot yet tell an unsupported sign from a supported one.
- **Being improved (carried into the next phase):** (1) unknown handling: confidence scores separated supported from unsupported signs poorly (AUROC about 0.64), so the product defaults to "not sure" and shows candidates as possible matches; whether the browser phase may start on that approach is a Developer decision on the Phase 3 gate, not yet made; (2) data: the official PopSign download is still blocked by an expired certificate, and more signers would help most; (3) vocabulary: `puppy` has two signed forms and tracks poorly, so it is excluded from the first real vocabulary, which should grow toward 20 to 30 signs in measured stages; (4) fingerspelling letter recognition was added to scope by the Developer; its data feasibility check is still in progress.
- Evidence for each item is in the dated entries above.

### Nov 9 — Letter classifier cross-dataset feasibility result

- Setup, fixed before running: the 24 letters shared by both datasets (A-Y without J); hand landmarks from the browser's Hand Landmarker model in image mode, converted to pixel units, wrist-relative and palm-scaled (63 values); one small classifier (63-128-24 network, dropout 0.2, 30 fixed epochs, seed 20261109, no early stopping); mirrored copies added to the training data only; test data never mirrored. Samples: SignAlphaSet 600 per letter, Cabana Train 400 per letter, Cabana Test 30 per letter. A hand was found in 98.6%, 96.3%, and 94.9% of those samples.
- Handedness labels disagreed across datasets (Cabana Train 81% "Left"; SignAlphaSet 86% and Cabana Test 86% "Right"), which is why the classifier trains on mirrored copies instead of relying on the label.
- Train Cabana, test SignAlphaSet (different people and setting): **68.3% top-1**, 84.9% top-3 over 14,193 images; chance is 4.2%.
- Train SignAlphaSet, test Cabana Test (different people and setting): **49.3% top-1**, 73.8% top-3 over 683 images.
- Train Cabana, test Cabana Test (signers may overlap, so not signer-separated): 86.7% top-1, 95.0% top-3. The gap to the two cross-dataset numbers suggests that new people and settings cost a lot of accuracy, though signers are unknown so the cause is not isolated.
- Letters with 0% in a direction: `G`, `X`, `M` (Cabana to SignAlphaSet) and `G`, `M`, `O`, `X` (SignAlphaSet to Cabana Test). Most common mistakes: `M` as `S`, `G` as `C`, `Q` as `C`, `X` as `C` or `D`, and fist-like letters (`A`, `S`, `T`, `N`) mixed with each other. Fist-like letters differ mainly by thumb position, and `G`/`Q`/`X` depend on hand orientation, which differs between the datasets; neither explanation has been tested.
- **Reading:** letters are learnable from landmarks well above chance, but cross-dataset accuracy of 49% to 68% is not yet a good level, and some letters fail completely. This is one fixed configuration on two datasets with unknown signers. Any change tuned against these same test sets would make later numbers exploratory, not clean.
- No J or Z; no model exported; nothing in the browser.
- **Developer decision gate:** (a) one declared improvement attempt on these datasets (for example rotation normalization and training on both sets, evaluated by leaving one dataset out); (b) move to FSboard letter segments; (c) collect a small signer-labeled letter set.

### Nov 9 — Letter classifier: declared feature variants

- The Developer approved one declared improvement attempt. The proposal to train on both datasets and leave one out was dropped because two datasets leave nothing unseen. Two variants were fixed before running and evaluated on the same three experiments (`training/evaluate_letter_transfer.py --variant ...`): `rotaug` adds random in-plane rotation (+/-25 degrees) to the training copies; `invariant` uses 210 pairwise landmark distances plus the unit direction of the wrist-to-middle-finger-base axis. Mirrored training copies, settings, seed, and samples are unchanged. The baseline reproduced its earlier numbers exactly.
- Top-1 (top-3 in brackets), 24 letters, chance 4.2%:

| Experiment | baseline | rotaug | invariant |
|---|---|---|---|
| Train Cabana, test SignAlphaSet | 68.3% (84.9%) | 68.9% (79.6%) | **71.8%** (81.9%) |
| Train SignAlphaSet, test Cabana Test | 49.3% (73.8%) | 51.8% (72.8%) | **62.2%** (79.9%) |
| Train Cabana, test Cabana Test (not signer-separated) | 86.7% (95.0%) | 89.0% (98.1%) | 92.8% (99.3%) |

- Rotation augmentation changed little (+0.6 and +2.5 points cross-dataset). The invariant features helped most: +3.5 and +12.9 points cross-dataset. Neither reaches a good level: 72% and 62% top-1, with several letters still near 0% in cross-dataset tests (`D`, `G`, `X`, `M`, `H`; `O` in one direction).
- Caveats: three variants were evaluated on the same test sets, so choosing `invariant` carries selection bias; there are only two datasets and signer identity is unknown; the same letters fail in both directions and under every variant. That pattern is consistent with the two datasets showing different handshapes or labeling conventions for those letters, which has not been checked (a within-dataset check shows `G` is not weak inside Cabana).
- No J or Z; nothing exported; nothing in the browser.
- **Developer decision gate:** (a) visually compare `G`, `M`, `X`, `D` samples between the two datasets to test the label-convention explanation; (b) FSboard letter segments; (c) a small self-collected, signer-labeled letter set. Do not tune further against these test sets without recording it as exploratory.

### Nov 11 — PopSign four-sign source-matched checkpoint

- The official PopSign v1.0 site and archive endpoint are available again over valid HTTPS. A read-only request to the official `after` training archive returned HTTP 200 on Nov 11; no certificate bypass was used.
- The Developer approved a source-matched dataset report before retraining. `training/download_catalog_sample.py` now accepts selected catalog IDs or display glosses. The byte-range downloader retrieved 120 videos (690,008,613 bytes) for `after`, `hear`, `man`, and `pen`: 20 train, 5 validation, and 5 test clips per sign. Source videos and manifests remain Git-ignored.
- The bounded sample contains 31 unique training signers, 8 validation signers, and 7 test signers, with no signer overlap between splits. Each sign/split count matches the requested 20/5/5.
- Contract v2 extraction with PopSign's verified `keep` handedness rule produced 120 finite `48 x 167` tensors. Every reported source frame decoded. Clips contain a median 65 decoded frames and 33.5 selected active frames.
- Whole-clip hand detection is uneven (median 44.1%, p10 25.1%), but the motion-selected active intervals are substantially denser: median dominant-hand detection 87.5%, p10 74.9%. Two `after` clips fall below the 60% active-interval review threshold, one training and one validation; none of the 20 test clips do. They are retained rather than silently filtered.
- Reproducible aggregate checks are in `training/report_popsign_checkpoint.py`; the local ignored evidence is `training-artifacts/popsign-four-sign-v2-extraction/quality-report.json` and its extraction manifest. The identifiable source videos and tensors are not committed.
- The existing local active-interval contact-sheet renderer was attempted twice against the new manifest and aborted both times with exit code 134 and no output. Per the two-failure rule, no further renderer variation was attempted. Numeric extraction checks passed, but visual interval review is not claimed.
- No model was trained and the test labels were not used for model selection. **Developer decision gate:** inspect the two weak `after` clips/resolve the renderer first, or accept the measured dataset checkpoint and approve one PopSign-trained four-sign model using validation for selection and test once for the final report.

### Nov 11 — PopSign-wide screening started

- The Developer accepted the four-sign checkpoint and approved staged screening of every available PopSign v1.0 game sign at 5 train, 2 validation, and 2 test clips per sign, without training. The official index yielded exactly 250 v1.0 game signs, matching the data card.
- Download and extraction are now resumable per video. Download manifests are written atomically after each selected member; extraction manifests are written after each tensor. `--batch-signs` bounds a run, and `--continue-on-error` records screening failures while strict extraction remains the default.
- Batch 1 covered the first 10 alphabetical signs (`after` through `aunt`): 90 videos, 486,508,530 bytes. It used 26 training, 7 validation, and 8 test signers with no cross-split overlap.
- Contract v2 extraction succeeded for 89 of 90 clips; one `alligator` training clip had no detected dominant hand and is recorded as a failure. All 89 tensors are finite and shaped `48 x 167`; every reported frame decoded.
- Active-interval dominant-hand coverage is median 87.1%, p10 70.9%, minimum 50%. Three successful clips fall below the 60% review threshold (`airplane` train, `alligator` train, `any` validation); none of the 20 test clips do. No clips were silently removed and no model was trained.
- Local ignored evidence: `datasets/popsign-v1-0/all-sign-screening-5-2-2/sample-manifest.json` and `training-artifacts/popsign-all-sign-screening-v2/{extraction-manifest,quality-report}.json`.
- Batch 2 completed the next 10 signs (`awake` through `before`), bringing the cumulative screen to 20/250 signs, 180 videos (942,577,041 bytes), 179 finite tensors, and the same one recorded failure. Active-interval coverage remains similar (median 86.2%, p10 71.3%); five cumulative successful clips are below 60%, adding `bed` training and `bath` validation to the three Batch 1 cases. All 40 cumulative test clips extracted successfully, and split signer overlap remains zero.
- Batch 3 completed `beside` through `brother`, bringing the cumulative screen to 30/250 signs and 270 videos (1,414,841,676 bytes). Extraction produced 269 finite tensors with the same single `alligator` failure; median active-hand coverage is 86.2%, p10 71.3%, and six successful clips are below 60%. Split signer overlap remains zero.
- Batch 4 completed `brown` through `chair`, bringing the cumulative screen to 40/250 signs and 360 videos (1,869,880,739 bytes). Extraction produced 359 finite tensors with the same single `alligator` failure and no decoded-frame mismatches; median active-hand coverage is 86.5%, p10 71.4%, and the cumulative weak-clip count remains six. Several new videos have low whole-clip hand detection, but active-interval selection recovered at least 60% dominant-hand coverage for every new training and validation clip. Split signer overlap remains zero. The train/validation-only quality ranking now starts with `cat`, `all`, `car`, `animal`, `bye`, `because`, `apple`, `book`, `awake`, and `bedroom`; this remains a tracking-quality ranking, not recognition accuracy.
- Batch 5 completed `cheek` through `cow`, bringing the cumulative screen to 50/250 signs and 450 videos (2,364,386,024 bytes). Extraction produced 449 finite tensors with no decoded-frame mismatches and the same single `alligator` failure. Median active-hand coverage is 87.0%, p10 71.4%; three new weak training clips (`child`, `clean`, and `close`) bring the cumulative sub-60% count to nine, while every new validation and test clip passed. Split signer overlap remains zero. The train/validation-only ranking now starts with `cheek`, `cloud`, `cat`, `all`, `car`, `animal`, `chin`, `chocolate`, `bye`, and `because`; face-adjacent signs are therefore not uniformly weak, but this remains tracking-quality evidence rather than recognition accuracy.
- `training/rank_popsign_screening.py` ranks data quality using training and validation clips only; it does not read test metrics. After Batch 3, the first ten signs with no failed or weak train/validation clips and the strongest minimum coverage were `all`, `animal`, `because`, `apple`, `book`, `awake`, `bedroom`, `blue`, `boat`, and `aunt`. This ranking produced the approved ten-sign accuracy checkpoint below; it is tracking-quality evidence, not recognition accuracy or proof of class separability.
- **Proposed first PopSign accuracy checkpoint:** expand those ten signs to 20 train, 5 validation, and 5 test clips; train one fixed compact temporal model with validation-only selection; then evaluate the untouched test split once and report top-1, top-3, per-sign recall, and the confusion matrix. A 70% top-1 target is a provisional feasibility bar, not a product-quality claim. Do not export the model automatically. This expansion and training require Developer approval.

### Nov 13 — First ten-sign PopSign accuracy checkpoint

- The Developer approved the fixed ten-sign checkpoint. The byte-range downloader retrieved 300 official PopSign videos (1,638,099,550 bytes): 20 train, 5 validation, and 5 test clips for each of `all`, `animal`, `because`, `apple`, `book`, `awake`, `bedroom`, `blue`, `boat`, and `aunt`.
- Contract v2 extraction produced 300 finite `48 x 167` tensors with no failures. The split contains 31 training, 8 validation, and 8 test signers with no cross-split overlap. Median active dominant-hand coverage is 87.5%, p10 78.9%; one clip is below 60%.
- One fixed one-layer bidirectional GRU (seed 20261109, hidden size 48, dropout 0.2, batch 16, AdamW 0.001/0.0001) selected epoch 26 by validation loss and stopped after 61 epochs. Validation was **68.0% top-1** and **92.0% top-3** on 50 clips. The untouched test split was then evaluated once: **78.0% top-1** and **92.0% top-3** on 50 clips, passing the provisional 70% feasibility gate.
- Test recall by sign: `all` 4/5, `animal` 4/5, `apple` 5/5, `aunt` 4/5, `awake` 5/5, `because` 3/5, `bedroom` 3/5, `blue` 4/5, `boat` 5/5, `book` 2/5. The largest confusion is `book` as `boat` (3/5), showing that tracking-quality selection does not establish class separability.
- Limits: five test clips per sign are imprecise; validation is 10 points lower than test; this is one seed and one selected vocabulary. The 78% figure must not be presented as expected live-webcam accuracy. Unknown rejection is still unsupported, so status is `not-ready` and browser export was not attempted.
- Local ignored evidence: `training-artifacts/popsign-ten-sign-v2-extraction/{extraction-manifest,quality-report}.json` and `training-artifacts/popsign-ten-sign-gru/{evaluation.json,gru-model.pt}`.

### Nov 16 — Phase 3 browser integration started

- The Developer approved entering Phase 3 with the ten-sign PopSign model without waiting for the separate 250-sign screen to finish. The result policy remains `Not sure` with three ranked possible matches; the browser does not claim that a softmax score recognizes or rejects an unknown sign.
- Added a reproducible PyTorch-to-ONNX exporter. The 256.2 kB model matched PyTorch's complete ranking on all 50 held-out test clips; maximum absolute logit error was 0.00000191. The generated ONNX and metadata files remain Git-ignored model assets.
- Added an ONNX Runtime Web adapter, a contract-v2 browser preprocessor, and a separate capture controller. One Scan action waits for a visible hand and shoulders, requires 0.5 seconds of readiness, counts down for three seconds, captures for three seconds, selects the active interval, resamples to `48 x 167`, and returns three possible matches. Pose runs every third processed scan frame and the latest anchors are reused between pose updates so hands remain the high-rate path.
- Replaced the obsolete five-sign sample catalog with catalog version 0.2.0 containing the ten supported model signs. The recognition adapter refuses to load if model labels and supported catalog entries differ.
- Verification: the catalog validator passed for 10 signs; TypeScript and the Vite production build passed; headless Chrome rendered the production page; and a production recognition smoke page loaded the ONNX model and returned 10 ranked candidates. The existing Python contract test was not rerun because its direct unittest invocation could not resolve the `training/` module path after two attempts; no further invocation variations were made.
- **Developer test remains open:** run several supported signs in desktop Chrome, record whether countdown/capture/retry work, whether rankings are plausible, result latency, and whether handedness/body-relative preprocessing matches the offline source. The first live result below proves one end-to-end browser scan, not live accuracy across the vocabulary.
- **First live browser result (Nov 16):** the initial two scans failed with `No dominant hand was tracked during the scan` even though the overlay reported a high-confidence hand. The browser preprocessor was incorrectly applying pose visibility semantics to Hand Landmarker points; contract v2 requires only finite hand coordinates. Separating finite-hand validation from pose visibility fixed the governing rule, and a zero-hand-visibility regression fixture now passes the complete synthetic capture-to-results smoke test.
- After the fix, the Developer's live `apple` attempt completed and visibly returned `animal` 41.4%, `apple` 23.9%, and `bedroom` 20.9%. This verifies the live capture, ONNX inference, and final result presentation, but the top-1 result is wrong and must be retained as browser-domain accuracy evidence. The Developer supplied a screenshot in chat; its original file is pending import into the repository image history.
- Three live `apple` attempts ranked `animal` first and `apple` second or third. The Developer approved a localhost-only numeric diagnostic export; it saves the normalized `48 x 167` tensor and scan metadata but no image or video. Replaying the supplied scan produced identical browser/PyTorch rankings (maximum probability difference 0.00000030), ruling out ONNX conversion as the cause: `animal` 39.3%, `bedroom` 32.0%, `apple` 18.5%.
- The capture was closest to the `apple` training centroid, but its shoulder-normalized wrist y median was `-0.77`; all 20 PopSign `apple` training clips ranged only from `-0.18` to `+0.31`. Every `apple` training video is portrait `1944 x 2592`; 19/20 `animal` and `bedroom` videos are the same size, while the live webcam is landscape. Contract v2 computes 2D palm and shoulder distances directly in normalized image x/y, where x and y use different pixel scales when aspect ratios differ. This is a source/browser geometry defect requiring an aspect-corrected versioned contract and model retrain, not a confidence-threshold adjustment.
- PopSign inspection also showed one-handed `animal` examples, and its extracted training tensors have median zero non-dominant-hand presence. A universal two-hand exclusion for `animal` would contradict the model's sourced variant and conceal the geometry problem; hand-count constraints remain a separate catalog/variant review.
- **Aspect-correct contract v3 checkpoint (Nov 16):** the Developer approved aspect-correct image geometry plus explicit wrist-to-nose `x/y` location, retaining the 48-frame sequence and all v2 hand/body features. V3 produces `48 x 171` tensors. Unit tests prove identical physical landmark geometry produces equal v3 features in portrait and landscape frames.
- Re-extraction of the same 300 official PopSign clips completed with 300 finite tensors, no failures, no split overlap, and the same one weak training clip as v2. The fixed single-GRU run used the same seed and settings, selected epoch 33 using validation only, and evaluated the untouched test set once: validation top-1 **64.0%**, test top-1 **68.0%** (34/50). This misses the approved 70% gate and regresses from v2's 78.0% test result, so no v3 browser model was exported and the working browser remains on v2.
- The v3 test result is diagnostically mixed: `apple` and `animal` each scored 5/5, while `all` scored 1/5 and `because` and `book` each scored 2/5. This supports the live Apple geometry diagnosis but does not justify silently replacing the stronger overall model. **Developer decision gate:** keep v2 deployed and choose whether the next approved experiment should isolate aspect correction from the added head offsets, reduce the supported vocabulary, or explicitly accept the 68% v3 result. Do not run another model variation without that choice.
- **Aspect-only isolation run (Nov 16, Developer-approved option A):** the same v3 tensors with only the four wrist-to-nose offset columns removed (`--drop-head-offsets`, `167` features per frame), same seed, split, and GRU settings. Best epoch 26 of 61 by validation loss. Validation top-1 **66.0%**, test top-1 **80.0%** (40/50), passing the 70% gate. Test recall: `all` 4/5, `animal` 5/5, `apple` 5/5, `aunt` 4/5, `awake` 5/5, `because` 3/5, `bedroom` 3/5, `blue` 4/5, `boat` 5/5, `book` 2/5. Unknown rejection is still unimplemented, so status stays `not-ready` and nothing was exported. Evidence: `training-artifacts/popsign-ten-sign-gru-v3-aspect-only/evaluation.json` (ignored).
- Reading: aspect correction alone keeps `apple`/`animal` at 5/5 and matches v2's 78% within noise (one clip is 2 points on 50 clips), while the head offsets are associated with the v3 regression (68%). Caveats: the same 50-clip test split has now been evaluated by three variants, so choosing this one carries selection bias; validation (66%) is below v2's 68%; one seed; and the live-browser `apple` failure has not been re-tested. **Developer decision gate:** approve exporting this aspect-only model to the browser for a live `apple` retest (needs a browser preprocessor change to v3 geometry without head offsets), or review further first.
- **Aspect-only browser integration (Nov 16, Developer-approved):** the aspect-only model replaced v2 in the browser (v2 files kept in `training-artifacts/sign-recognizer-v2-backup.*`). The browser preprocessor now converts landmarks to pixel-scale geometry using the video's width and height before any distance (`x*w`, `y*h`, `z*w`), matching `landmark_contract_v3.py` without head offsets. The ONNX export matched PyTorch on all 50 held-out clips (maximum logit error 0.00000143, identical rankings).
- Parity evidence: identical synthetic captures (70 frames, hand dropout, below-threshold pose points, left- and right-dominant, 1280x720 and 1944x2592 frames) were processed by the Python v3 pipeline and by the browser `frameFeatures` + `prepareSequenceDetailed` code. All four cases gave the same active interval and dominant hand, with maximum tensor difference 1.7e-5 (float32 noise). TypeScript build, production build, and the headless capture-to-results smoke page passed. This proves preprocessing parity on synthetic landmarks, not live accuracy.
- **Developer test open:** repeat the live `apple` scans (and a few other signs) in desktop Chrome; export the numeric diagnostic and replay it with `training/compare_browser_capture.py`. If `apple` still ranks below `animal`, geometry was not the governing cause.

- **First live results with the aspect-only model (Nov 16, Developer report plus two diagnostic exports):** `book` and `boat` were fairly consistent; `apple` was inconsistent with `because`; `awake` was inconsistent with `bedroom` and `aunt`. Browser and Python rankings matched on both exports (maximum probability difference 2e-7), so preprocessing parity holds live. The `apple` capture's shoulder-normalized wrist y median was -0.15, inside the PopSign `apple` range (-0.23 to 0.41), so the Nov 16 geometry defect is fixed.
- **`awake` cause (diagnostic only, no retraining):** the live capture tracked the non-dominant hand in 100% of frames (the idle hand stays in a webcam view), while the PopSign training clips almost never show a second hand (at most 1 of 20 clips per sign has it in 20% of frames; mean 1% to 5%). The capture sat far from every training clip (standardized RMSE about 2.0 to 2.5, against about 0.55 for the `apple` capture). With only the non-dominant-hand block zeroed, the frozen model returned `awake` at 94.5% (it was `because` 24.4%, `awake` 6.3%).
- **`apple` cause (not resolved):** the `apple` capture was one-handed and in range, and both its nearest training clip and nearest class centroid were `apple`, yet the GRU returned `because` 60.3% and `apple` 33.1%. Blanking the second hand changed nothing. This looks like a model-level `apple`/`because` weakness that one capture cannot size; offline `apple` was 5/5 but `because` was only 2/5.
- **Developer decision gate:** the second-hand mismatch is a source/browser distribution difference. Options: (a) zero the non-dominant slot at inference for this vocabulary, which matches what the model saw; (b) remove the non-dominant block from the contract and retrain; (c) keep it and add augmentation or data that shows an idle second hand. Collect more `apple` scans before changing the model for it.

- **Second-hand blanking applied (Nov 16, Developer delegated the choice; option A):** the browser preprocessor now zeroes the non-dominant hand block of the model tensor after the active interval is chosen, matching training data that almost never shows a second hand. Raw second-hand presence is still reported in diagnostics. Verification: the browser-versus-Python synthetic parity cases still match (maximum difference 1.7e-5 with the Python expectation blanked the same way), the blanked block contains 0 non-zero values while raw presence reads 0.81, and the production build passes. Live accuracy is not yet tested after this change. Limit: dominant-hand choice still counts tracked frames, so a left-handed signer whose idle right hand is tracked longer could be mirrored incorrectly; this was not tested.

- **Live retest after blanking (Nov 16, Developer report):** `awake` and the other signs tested worked; `apple` is still misread. Commit 909d705 holds the browser model and preprocessing change. The Developer noted that a left-hand solo sign should behave like a right-hand one (the contract mirrors left-dominant signs into right-dominant coordinates, so it does when only that hand is tracked) and that two-hand signs matter less because most are symmetrical. The idle-hand case for left-handed signers is still untested.
- **`apple` cause: body anchors act as a framing shortcut (diagnostic only, one live capture, frozen model).** Interval trimming is not the cause (no sub-window of the capture changes the ranking). Swapping individual feature groups of the capture for the training `apple` average: handshape alone left `because` first (50%), wrist position alone gave a near tie (47% vs 46%), and body anchors alone flipped it to `apple` at 89%. The capture's head sits lower relative to the shoulders than in training (nose y -0.41 against a training mean of -0.52, about 1.8 standard deviations), its shoulders are tilted (y +/-0.08 against +/-0.02), and its right elbow is 2.3 and 1.6 standard deviations out of range. In training, the `apple` and `because` clips differ in head height by about 0.65 standard deviations, so the model has learned head and shoulder framing, which is signer and camera setup, as a cue for the sign.
- **Developer decision gate:** options are (a) retrain one GRU without the face and elbow anchors, keeping shoulder-relative wrist position and handshape; (b) keep the anchors and add random per-clip shifts and tilts of the anchors during training; (c) normalize anchors against the user's own neutral pose captured during the countdown. Each model option reuses the same 50-clip test split a fourth time, so selection bias grows and results should lean on validation and on live scans.

- **Hands-only variant (Nov 16, Developer-approved option A):** one GRU on the same v3 tensors with the head offsets and the whole upper-body anchor block removed (`--drop-head-offsets --drop-body-anchors`, 134 features per frame), same seed, split and settings. Best epoch 26 of 61. Validation top-1 **74.0%** (the aspect-only variant scored 66.0%), test top-1 **80.0%** (40/50, the same as before), passing the 70% gate. Test recall: `all` 3/5, `animal` 5/5, `apple` 5/5, `aunt` 4/5, `awake` 5/5, `because` 3/5, `bedroom` 4/5, `blue` 4/5, `boat` 5/5, `book` 2/5. Unknown rejection is still unimplemented. The frozen model returned `apple` 91% on the Developer's live `apple` capture (the previous model gave `because` 60%) and `awake` 98% on the `awake` capture with the second hand blanked. The 50-clip test split has now been used by four variants, so selection bias applies; validation and live scans carry more weight.
- **Browser integration of the hands-only model:** the browser no longer builds body anchors (134 features per frame). The ONNX export matched PyTorch on all 50 held-out clips (maximum logit error 0.00000143), the synthetic browser-versus-Python parity cases still match (maximum difference 1.7e-5), and the smoke page passes. Previous model files are kept in `training-artifacts/sign-recognizer-*-backup.*`.
- **Browser video replay (Nov 16):** a dev-only harness (`app/video-replay.html`, `app/scripts/replay-videos.mjs`, `training/compare_browser_replay.py`) plays local PopSign clips through the real browser tracker, preprocessing and model in headless Chrome. The first attempt was invalid and is discarded: headless Chrome software-rendered the tracker (300 to 600 ms per frame), so real-time playback processed only 3 to 9 frames per clip and later clips got none. The harness now steps frame by frame with the CPU tracker delegate (about 65 frames per clip, about 90 ms per frame), which is deterministic but processes every frame, a little more than the live app does. Result on the 50 test clips: browser **39/50 = 78.0%** top-1 and 92.0% top-3, against 80.0% offline; browser and offline agree on 49 of 50 clips; no errors; dominant-hand presence in the kept interval had median 0.87 and minimum 0.56. This shows the browser tracker and preprocessing reproduce the offline result on the same videos. It does not test webcam conditions. Output: `training-artifacts/browser-replay/hands-only-test.json` (ignored).

- **Live retest of the hands-only model (Nov 16, Developer report):** `apple` is now recognized live, which confirms the body-anchor diagnosis (the anchors were acting as a framing cue). The weak signs found offline and in replay (`book`, `all`, `because`) are also weak live. The Developer also tested signing with the other hand; the outcome was not itemized, so left-handed accuracy is not yet recorded as verified. Developer accepted the hands-only model as the working browser model (commit 9c46aeb).

- **Vocabulary growth step 1 started (Nov 16):** the Developer asked to keep `book`, `all` and `because` and to grow the library in measured, iteratively tested stages. Next-ten candidates (ranked on train and validation tracking quality only): `cheek`, `cloud`, `cat`, `car`, `chin`, `chocolate`, `bye`, `closet`, `carrot`, `can`. The download stopped on `cheek`: its official validation split has only 3 distinct signers (47 clips), so 5 independent validation clips are impossible. Signer counts for the other candidates are being checked before any substitution; `cloud` and `cat` have 8 validation and 8 test signers.
- **"How to sign" reference built (Nov 16, Developer chose option A):** `training/build_sign_references.py` writes `catalog/sign-references.json` (136 kB for ten signs): one 48-frame dominant-hand landmark animation per supported sign, from the training clip closest to its class mean among clips with at least 85% dominant-hand tracking, with no video, signer ID, or file name. The app has a `How to sign` button and a per-candidate link that open a dialog with a looping animation, wrist-movement trail, pause, frame scrubber, caption, and the PopSign CC BY 4.0 attribution; it starts paused at the middle frame under reduced-motion preferences. The catalog validator now checks every supported sign has a well-formed reference. Verification: TypeScript and production builds pass, the validator reports 10 signs with 10 references, and headless Chrome screenshots at 1100 and 390 px widths show the dialog opens, lists all ten signs, animates, and fits the phone width. Limits: hand size is a schematic proportion (palm is 0.25 shoulder widths), only the dominant hand is shown, there are no written descriptions or dictionary links yet (these need a verified source such as ASL-LEX), and the Developer has not reviewed it yet.

- **Tutorial accuracy and clarity feedback (Nov 16, Developer report):** the Developer pointed out that `awake` is two-handed and that some tutorial signs are inaccurate and hard to read. Cause: the PopSign tracking almost never captured a second hand (at most 1 of 20 training clips per sign), so the animation drew one hand for signs that use two. ASL-LEX 2.0 (CC BY 4.0, peer reviewed) codes `all`, `animal`, `awake`, `bedroom`, `boat`, and `book` as two-handed and `apple`, `aunt`, `because`, and `blue` as one-handed. An earlier statement in chat that `all` has differing forms was wrong; it came from a prefix match that pulled in other glosses, and an exact match gives one two-handed entry.
- **Tutorial redesign (Nov 16):** added `catalog/sign-facts.json` (built by `training/build_sign_facts.py` from ASL-LEX; fields are omitted when forms disagree) and rebuilt the panel: a facts card (hands, starting location, movement, handshape), a large close-up with color-coded fingers, start/middle/end stills, a movement trail with start and end markers and labeled head and shoulders, and a caption that says when the other hand is not drawn. The validator now also requires facts for every supported sign. Verification: TypeScript, catalog validation (10 signs, 10 references, 10 fact sets), and headless Chrome screenshots of `awake` and `apple` at 1100 px. Limits: the animation still draws only the signing hand because the PopSign data does not contain the second hand, whether PopSign performers signed these two-handed signs one-handed has not been verified in the videos, hand drawings are 2D projections that can look flattened when the palm faces the camera, the ASL-LEX codes describe citation forms and the PopSign example may differ, and the Developer has not yet reviewed the redesign.

- **Second-hand data check (Nov 16, Developer asked for the second hand in the tutorial):** the second hand cannot be recovered from the sources we hold. In three `book` test clips I looked at locally, the signer opens one hand and the other hand is not in the frame (PopSign signers hold the phone). The browser replay's second-hand presence by sign (median over five test clips) is 0 for every sign except `boat` and `book` at 0.06. The Google landmark corpus, which has all 20 candidate signs, shows the same pattern: in 10 local clips each of `all`, `car`, `closet`, and `cloud` (all two-handed per ASL-LEX), none had the second hand tracked in half or more of the frames. ASL-LEX's own "ASL examples" folder has only 86 videos (of our 20 candidates only `apple` and `book`), and no license is stated on the OSF node for those videos, so it is not a usable source. ASL Citizen forbids redistributing data or modifications. A mirrored copy of the signing hand was rejected: PopSign wrist positions sit about 0.57 shoulder widths to the side, so a mirrored hand would be about 1.1 shoulder widths away instead of touching, as `book` requires. The tutorial caption now says why only one hand is drawn. **Developer decision gate:** record real two-handed references with the app's own tracker by a fluent signer (landmarks only), hide animations for two-handed signs until then, or hand-author second-hand keyframes for review.

- **Reference recorder built (Nov 16, Developer chose option A):** a development-only page (`app/record-reference.html`, localhost only, not in the production build) records a sign with the app's own tracker, normalizes both hands to the shoulder midpoint and width of the take (aspect-correct), canonicalizes the dominant hand like the model contract (including reflecting left-dominant signing), lets the signer trim the start and end, and saves landmark numbers only. `training/merge_reference_takes.py` validates takes (rejects a one-hand take for a sign ASL-LEX codes as two-handed) and merges them as `recorded` entries that a PopSign rebuild preserves. The tutorial draws a recorded second hand as a faded hand. The shared drawing code now serves both the tutorial and the recorder preview. Verification: 10 data tests pass (`npm run test:reference`: shoulder normalization, left-hand reflection, trimming, gap filling, error cases); a synthetic two-hand recording reviewed in headless Chrome produced a take with both hands and blocked saving when trimmed too short; merge and rebuild-preservation checked on temporary copies; TypeScript, catalog validation, and the production build pass (the recorder and replay pages are not in `dist`). Not yet verified: recording with a real camera and a fluent signer. Six two-handed signs await recordings: `all`, `animal`, `awake`, `bedroom`, `boat`, `book`.

- **`book` decision (Nov 16, Developer chose option B):** diagnostic on the training clips: `book` and `boat` class means are 0.47 apart in standardized units while `book` clips vary 0.93 from their own mean; `book` is also 0.46 from `bedroom`. Both are coded identically by ASL-LEX (open B, curved, repeated, neutral space, two hands), their training wrist paths are almost equal (1.19 and 1.15) and neither shows a second hand, so the recognizer cannot separate them from one hand (3 of 5 `book` test clips read as `boat`). The Developer chose to leave the model unchanged. Added `app/src/facts.ts`: two signs are look-alikes when ASL-LEX codes them the same on hands, both locations, movement, repetition, and both handshapes (a missing field never matches). The results panel shows a note when two of the top three candidates are look-alikes, and the tutorial adds a "Looks like" row. The only pair among the ten signs is `boat`/`book`. Verification: 6 new tests (16 total, `npm test`), type-check, build, and a screenshot of the `book` tutorial. The results-panel note itself was verified only through its message function, not on a live scan. The `book` tutorial animation still needs a recorded two-handed take.
- **Next ten signs downloaded (Nov 16):** `cloud`, `cat`, `chocolate`, `bye`, `closet`, `can`, `cow`, `boy`, `better`, `another` (replacing `cheek`, `car`, `chin`, and `carrot`, which have fewer than 5 independent validation or test signers; `backyard` and `arm` were also short). 300 clips (1,719.5 MB), 20 train, 5 validation, 5 test per sign, 31 / 8 / 8 signers with no overlap across splits. Local only (git-ignored `datasets/popsign-v1-0/accuracy-next-ten-v2-20-5-5`). The earlier partial `accuracy-next-ten-20-5-5` folder (109 MB, `cheek` only) was left in place, not deleted.

### Nov 16 — Twenty-sign checkpoint

- **Extraction:** the next ten signs (`another`, `better`, `boy`, `bye`, `can`, `cat`, `chocolate`, `closet`, `cloud`, `cow`) extracted with the v3 contract and `keep` handedness: 298 of 300 clips. Strict mode stopped at the first clip with no detected signing hand; the run resumed with `--continue-on-error` and recorded two failures, both training clips (`better` signer 4a.8014 and `bye` signer 7043), so `better` and `bye` have 19 training clips. All validation and test splits are full (5 per sign), signers are 31 / 8 / 8 with no overlap, active dominant-hand coverage is median 0.88 and p10 0.76, two clips are below the 0.60 review threshold (`boy` train 0.20, `cloud` validation 0.59, no test clip), and every tensor is finite with no decoded-frame mismatches. `training/merge_extraction_manifests.py` combined the two manifests (598 clips, 2 recorded failures).
- **Result:** one fixed GRU (same seed, settings, hands-only 134 features) on 20 signs, best epoch 38 of 73 by validation loss. Validation top-1 **74.0%** (top-3 90.0%); the untouched test split was evaluated once: top-1 **74.0%** (74/100 clips, 8 signers), top-3 89.0%, top-5 93.0%, passing the provisional 70% gate. Test recall: `all` 3, `animal` 4, `apple` 5, `aunt` 3, `awake` 5, `because` 3, `bedroom` 5, `blue` 3, `boat` 4, `book` 3, `another` 4, `better` 4, `boy` 5, `bye` 3, `can` 3, `cat` 2, `chocolate` 4, `closet` 5, `cloud` 2, `cow` 4 (each out of 5). The original ten score 38/50 and the new ten 36/50. Mistakes crossing between the old and new groups: 9 of 26. The most common single mistake is `cloud` read as `chocolate` (2). Unknown rejection is still unimplemented, so status is `not-ready`. The test estimate for 100 clips is roughly 65% to 82%. The test split has now been used by several model variants, so validation and live scans carry more weight.
- **Catalog 0.3.0:** 20 supported signs. The catalog validator requires a reference animation and a facts entry for each. ASL-LEX variant forms are matched as `gloss` or `gloss_<number>`; `another` has no ASL-LEX entry and is recorded as hands `unknown`, and the tutorial says its hand count is not verified. `cat` has forms with one and two hands (`varies`). Ten two-handed signs lack a recorded second hand: `all`, `animal`, `awake`, `bedroom`, `boat`, `book`, `can`, `chocolate`, `closet`, `cloud`. The look-alike rule still finds only `boat`/`book` among the 20.
- **Browser export and replay:** ONNX matched PyTorch on all 100 test clips (maximum logit error 0.0000031, identical rankings) and the smoke page loads 20 signs; the previous ten-sign model is kept in `training-artifacts/sign-recognizer-ten-sign-backup.*`. The browser video replay of the 100 test clips produced no errors: browser top-1 **77/100 = 77.0%**, top-3 90.0%, against 74.0% offline. Top-1 agreement is 83/100 (it was 49/50 with ten signs): disagreements are low-confidence clips (mean offline confidence 0.54 against 0.84 where they agree), are not tied to the new signs or the source frame rate, and the browser is right in 7 of the 17, offline in 4, neither in 6. So the browser path is sound, but with 20 classes near-tie clips flip with small tracker differences and live results will vary more.
- **Open:** Developer live test of the new signs (especially `cloud`, `cat`, `bye`); recordings for the ten two-handed tutorial signs; unknown-sign rejection; the next vocabulary stage.

For every later test, record the date, commit, environment, exact action, observed result, evidence location, and whether the Developer accepted it. Do not replace direct observations with a general statement that a feature works.

## Simplification reviews

A project this size invites Agents to pile on code. Redirect them away from bloat, stacked patches, obsolete features, and edge cases that a simpler design or code-structure rule would prevent. At the end of Phases 3, 4, and 5, have the Agent identify these problems, then decide yourself what to change. Record what it found, what you decided and why, and the result. Update the architecture in `spec.md` if the structure changes.

### Phase 3 review — pending

Check for duplicate browser/offline preprocessing, model-specific logic leaking into interface code, and more than one source of truth for landmark capture or labels.

### Phase 4 review — pending

Check for stacked tracking exceptions, inconsistent failure messages, unused experiments or assets, and lookup/filter logic that can be expressed as one shared rule.

### Phase 5 review — pending

Remove obsolete diagnostics and abandoned paths, verify credits and production assets, and re-run the accepted core behavior before final delivery.
