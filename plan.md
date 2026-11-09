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
| Phase 2 — Prove the core, Nov 2–9 | Real-camera tracking baseline, feasible PopSign subset, first held-out-signer model result | Prove tracking and recognition before expanding the interface |
| Phase 3 — Revise and integrate, Nov 9–16 | Temporary landmark capture and real ranked results in the browser | Reduce or revise vocabulary if model accuracy is inadequate |
| Phase 4 — Build and test, Nov 16–30 | Unknown handling, lookup references/filters, accessibility, GitHub Pages build, peer-review version | Learn mode begins only if the primary lookup loop is stable |
| Phase 5 — Finish and showcase, Nov 30–Dec 7 | Peer-review revisions, public deployment, final evaluation, breakdown and debrief | Fix and simplify before adding stretch work |

Current priorities are Translate (single supported signs) and unknown-sign lookup. Learn mode, saved attempts, uploads, and an LLM re-ranker remain stretch work in that order only after the core passes its checks.

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
7. **Optional expansion:** Learn mode only after checkpoints 1–6 pass. Saved attempts, uploads, and the in-browser LLM re-ranker require separate approval and spec revisions.

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

For every later test, record the date, commit, environment, exact action, observed result, evidence location, and whether the Developer accepted it. Do not replace direct observations with a general statement that a feature works.

## Simplification reviews

A project this size invites Agents to pile on code. Redirect them away from bloat, stacked patches, obsolete features, and edge cases that a simpler design or code-structure rule would prevent. At the end of Phases 3, 4, and 5, have the Agent identify these problems, then decide yourself what to change. Record what it found, what you decided and why, and the result. Update the architecture in `spec.md` if the structure changes.

### Phase 3 review — pending

Check for duplicate browser/offline preprocessing, model-specific logic leaking into interface code, and more than one source of truth for landmark capture or labels.

### Phase 4 review — pending

Check for stacked tracking exceptions, inconsistent failure messages, unused experiments or assets, and lookup/filter logic that can be expressed as one shared rule.

### Phase 5 review — pending

Remove obsolete diagnostics and abandoned paths, verify credits and production assets, and re-run the accepted core behavior before final delivery.
