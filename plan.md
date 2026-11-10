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
| Phase 3 — Revise and integrate, Nov 9–16 | Temporary landmark capture and real ranked results in the browser | Reduce or revise vocabulary if model accuracy is inadequate |
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

For every later test, record the date, commit, environment, exact action, observed result, evidence location, and whether the Developer accepted it. Do not replace direct observations with a general statement that a feature works.

## Simplification reviews

A project this size invites Agents to pile on code. Redirect them away from bloat, stacked patches, obsolete features, and edge cases that a simpler design or code-structure rule would prevent. At the end of Phases 3, 4, and 5, have the Agent identify these problems, then decide yourself what to change. Record what it found, what you decided and why, and the result. Update the architecture in `spec.md` if the structure changes.

### Phase 3 review — pending

Check for duplicate browser/offline preprocessing, model-specific logic leaking into interface code, and more than one source of truth for landmark capture or labels.

### Phase 4 review — pending

Check for stacked tracking exceptions, inconsistent failure messages, unused experiments or assets, and lookup/filter logic that can be expressed as one shared rule.

### Phase 5 review — pending

Remove obsolete diagnostics and abandoned paths, verify credits and production assets, and re-run the accepted core behavior before final delivery.
