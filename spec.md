# Specification

> EDITING DIRECTIVE: DEVELOPER AND AGENT EDIT THIS FILE COLLABORATIVELY. THE DEVELOPER MUST REVIEW AND APPROVE ITS CONTENT.

Purpose: Keep a concise, testable description of what the project should do now and how the system is structured to do it.

## Working agreement

Developer: Approve the intended behavior and the system's structure, test directly, understand each part well enough to explain it in your own words, and update this file whenever either changes.

Agent: Read the project documents and inspect the project. Turn the Developer's decisions into acceptance checks without inventing product choices or freezing details that still need testing. Propose structures suited to the project's scope, with their trade-offs, in plain language. Keep the architecture consistent with the actual project and point out where they have drifted apart. Do not restructure the project without the Developer's approval.

When you begin this step, start a fresh chat so its transcript stays clean. For example:

`Read the project documents, inspect the project, and help me specify what the next version should do.`

## Intended experience

What Users should be able to do and experience in the current version, tied to the goals in your pitch.

The current version is a local-first prototype for recognizing and looking up one isolated ASL sign at a time. A User starts the webcam, sees the system track their hands in real time, selects Scan a sign, performs the sign after a hands-free ready check and countdown, and receives up to five ranked matches from a visible supported vocabulary of about 20–30 signs. If the evidence is weak, the app reports an unknown sign instead of forcing a match.

The experience should feel responsive, honest, and low-pressure. The camera view visibly shows what the system can see: a box around each detected hand, points at the tracked joints, and lines connecting those joints. A tracking failure must never be presented as a signing mistake. The interface explains that it recognizes a limited set of isolated signs; it does not translate ASL conversation, judge complete signing form, or replace a teacher, interpreter, or translator.

Translate and unknown-sign lookup are the priorities for this version. Learn mode, saved attempts, uploaded video, and an optional in-browser LLM re-ranker remain later work.

Continuous ASL recognition and ASL-to-English transcription are outside the five-week scope. A future investigation may consider them only if the approved isolated-sign experience is complete early. A timestamped list of isolated recognition attempts, if later added, must be called an attempt history or recognition log rather than an ASL transcript. Open-vocabulary slang, fingerspelling, sentence grammar, and conversational translation are not implied by that log.

The supported language is American Sign Language (ASL) only. Other sign languages are separate languages and are not included. Results use English glosses as labels for possible ASL sign matches; a gloss is not assumed to be a complete or one-to-one English translation.

The first supported environment is the current desktop version of Chrome on the Developer's Mac. Safari, other desktop browsers, and mobile devices are compatibility checks after the core works; they are not allowed to silently broaden the initial acceptance target.

## Behavior and acceptance checks

For each feature or behavior you are building, describe what it should do and what counts as working, including failure cases and accessibility where they apply. Distinguish approved behavior from provisional ideas, and leave untested details open until they are needed.

### Camera and live tracking

- The User can start and stop the webcam deliberately. Stopping releases the camera, and the microphone is never requested.
- While the camera is active, the view draws a visible bounding box around each detected hand, all tracked hand joints, and the connections between joints. Optional body reference points may also be shown when they help locate a hand relative to the signer.
- Tracking supports up to two hands and records finger positions, hand location, and motion over time.
- Recognition uses hand-relative and body-relative landmarks rather than raw pixel distances. Hand joints are normalized to a stable hand scale, while general hand location and motion are measured against visible body anchors such as the shoulders, torso, or face. Location stays broad enough to tolerate normal differences in hand size, camera placement, framing, and distance while preserving distinctions needed between signs.
- The overlay stays aligned with the video when the preview is mirrored. Mirroring the preview must not silently reverse the coordinates used for recognition.
- The interface provides a clear mirror or handedness correction control because browser, camera, and model conventions may disagree. Before recognition is accepted, a real-camera test confirms that raising the User's right hand produces the intended right-hand data after any correction.
- Camera-off, permission-denied, no-camera, no-hands, one-hand, two-hand, and recently-lost states have distinct readable messages.
- Tracking only processes a new camera frame once; faster display refresh rates must not cause duplicate observations.
- The target is a smooth real-time preview on the Developer's test device. The accepted current baseline is approximately 19 detailed hand results per second without a growing queue; large side-to-side movements still trail slightly. The app measures processed frames per second, capture-to-result latency, skipped frames, and tracking time during testing.
- During a scan, the capture controller keeps a small, documented set of body reference points even if the User hides body points in the overlay. Display visibility and model input are separate settings.
- If the camera disconnects, the tab becomes inactive, or the tracker fails, capture stops safely and the User receives a recovery message instead of a result from an incomplete scan.
- Tracking-quality messages describe only observable conditions: hands or body anchors outside the frame, missing hands, overlapping hand boxes, unstable landmark movement, or lost anchors. The app does not claim that a particular finger is hidden when the tracker may only be estimating it.

### Device capability and performance

- Calibration runs a short capability check and selects one of two explicit modes; it does not silently reduce hand landmark detail.
- Standard mode keeps detailed hands at the highest sustainable rate and obtains the approved upper-body anchors outside the critical hand path, such as in a separate worker or at a tested low cadence.
- Reduced mode still keeps all 21 landmarks for each detected hand. It establishes stable face/shoulder references during calibration and updates body anchors only occasionally or between scans. Signs requiring unavailable body or facial distinctions are not presented as supported in this mode.
- The minimum-device provisional target is at least 15 detailed hand results per second, no growing frame queue, and no more than approximately 120 ms p95 capture-to-result latency. These numbers must be tested on an identified lower-capability device before becoming a support claim.
- The preview may stay visually sharp while inference receives a documented downscaled frame. Resolution is reduced only as far as finger tracking remains stable in calibration and real sign tests.
- Only the latest camera frame may wait for tracking. Old frames are dropped rather than processed late.
- Raw video frames are released immediately after tracking. A bounded in-memory landmark sequence and small model state are retained during a scan; training data is never loaded by the public app.
- Camera and workers stop when the User stops scanning or leaves the active experience. Repeated-scan testing checks memory, battery use, and thermal slowdown.
- Tracker, model, and WASM assets are cached for repeat visits and should total under 10 MB where accuracy permits. Quantization is evaluated only after the unquantized model passes accuracy checks.
- The baseline must work with WASM in supported Chrome. WebGPU and multithreaded WASM may be optional accelerators but cannot be required because browser support and static-hosting headers vary.

### Calibration and recalibration

- On first use, a guided setup checks framing, visible body anchors, neutral hand/body scale, the comfortable signing area, mirror/handedness convention, lighting, and tracking stability.
- Setup stores only numeric calibration parameters and settings in local browser storage. It does not store frames, video, or extracted attempt sequences.
- Later visits use the saved setup after a short passive validation. A camera, orientation, resolution, scale, or framing change can invalidate only the affected calibration step.
- Recalibrate is available from Settings and beside relevant setup or tracking errors. It reruns the affected step rather than restarting every step by default.
- The User may reset calibration or continue with safe defaults, with a clear warning that results may be less reliable. Essential missing landmarks can still prevent a scan.
- Calibration data has a schema version and is reset when the normalization rules change.
- The interface distinguishes a calibration problem, a live tracking problem, and recognition uncertainty. Recalibration is never presented as correcting the User's ASL and cannot be used as a generic response to a weak model result.

### Sign capture and results

- The User selects Scan a sign once. The app waits until required hands/body anchors are visible and reasonably stable, then gives a visible countdown before capturing landmarks.
- The scan captures a timestamped landmark sequence for a tested maximum duration and stops automatically; there is no Finish button whose reaching motion could contaminate the sequence.
- Leading and trailing stable frames may be trimmed under a documented rule. Stability-based early ending remains provisional and is added only if real-use testing shows that it does not cut off slow or repeated motion; the maximum duration is always the fallback.
- The interface says capture or scan, not record video. Webcam frames are neither saved nor uploaded.
- An attempt with too few usable frames or inadequate tracking asks the User to retry and does not produce a confident sign result.
- A replaceable recognition model returns up to five candidates drawn only from the supported vocabulary, ordered by model score.
- The default result is that the app does not know. Candidates appear only as labeled possible matches with their scores. The app presents a sign as recognized only if a tested rule shows that its confidence measure separates supported signs from unknown input; that has not been shown yet (validation AUROC 0.640 for top probability, 0.637 for margin, 0.649 for entropy), so otherwise the result is `Unknown` or `Not sure` rather than a forced match.
- A later, separately approved translation feature may show a context-based guess in parentheses. A guess is labeled as a guess, is drawn only from the model's own candidates, never adds a word the model did not propose, and is tested against showing no guess before it ships.
- Results identify that they are possible matches, show the model's uncertainty, and provide a reference for comparing candidates when licensing permits.
- The complete supported vocabulary and the single-sign limitation are visible before or alongside the results.
- Recognition is evaluated on signers excluded from training. The project reports top-1 and top-5 performance, unknown-sign behavior, and browser latency rather than describing the model as generally accurate.
- Unknown-sign tests include idle hands, ordinary non-signing gestures, poor tracking, and signs outside the supported vocabulary. A confidence threshold is accepted only if those negative examples show that it works; confidence alone is not assumed to prove an input is unknown.
- After the first held-out-signer evaluation, the Developer sets a minimum acceptable top-1 and top-5 result. If the model misses it, the first response is to reduce or revise the vocabulary rather than hide poor performance.
- Candidate results show licensed reference video or imagery when available. If redistribution is not permitted, the result provides an attributed source link or text label instead of copying the asset.
- When several candidates remain similar, the result explains that handshape, movement, orientation, or location may distinguish them. Verified sign metadata or reference material supports any specific distinction; the app does not invent signing advice.
- A Try again for clarity action starts a new hands-free scan without restarting the camera. It preserves the prior candidate list long enough for comparison, then replaces the temporary landmark sequence. After one useful retry suggestion, persistent ambiguity shows the ranked candidates rather than trapping the User in repeated retries.
- Similar or valid ASL variants are not labeled wrong merely because the model cannot separate them. Highly ambiguous pairs may be excluded from the initial vocabulary.

### Accessibility and privacy

- Primary controls work by keyboard, have visible focus states, and use readable text labels rather than relying only on icons or color.
- Status changes are available as text. The overlay uses high-contrast points, lines, and boxes but is not the only indication of tracking state.
- Motion not required for understanding the interface respects reduced-motion preferences. Live camera motion and tracking remain present because they are the function being requested.
- Webcam frames stay on the device. The current version has no account, upload, analytics, cloud inference, or server dependency.
- Attempts and landmark sequences exist only in memory and are cleared when the camera stops, the page reloads, or a new attempt replaces them. Persistent saving requires a later approved change.

### Deployment

- The production app is deployed publicly with GitHub Pages from the project repository.
- The Vite base path and all model, WASM, image, and script URLs work from the repository subpath, not only from local development at `/`.
- A production build loads without missing-asset errors, starts the camera over GitHub Pages' HTTPS connection, and can be used without a separate backend.
- If a model or runtime asset cannot load, the page remains usable enough to explain the failure and retry; it does not present tracking-only output as sign recognition.

## Architecture

How the system works and the structural decisions that keep it coherent, consistent, and easy to change. Adapt these sections to your project and tech stack.

### Overview

The main parts of the system, what each is responsible for, and how they connect. Include a simple diagram.

The browser app keeps camera access, tracking, visualization, temporary landmark capture, recognition, and presentation separate so the tracker or model can change without rewriting the whole experience.

```text
Webcam
  |
  v
Camera capture --> MediaPipe tracker --> Live overlay
                         |
                         v
                  Capture controller
                         |
                         v
                 Recognition model
                         |
                         v
              Ranked/unknown results
```

- `camera.ts` owns webcam permission, the media stream, and start/stop behavior.
- `tracker.ts` wraps MediaPipe and returns normalized hand and optional pose landmarks. Nothing outside this module depends directly on MediaPipe result objects.
- `overlay.ts` draws hand boxes, joints, connections, and optional pose reference points in the same coordinate system as the raw video. Preview mirroring is a presentation transform.
- A new capture controller will own readiness, countdown, bounded capture, validation, and the temporary timestamped sequence.
- A new model interface will accept one normalized sequence and return ranked candidates and scores. The initial implementation may use TensorFlow.js or ONNX Runtime Web; that choice remains open until model export is tested.
- `main.ts` wires these parts together and renders the current state. It should not contain tracking or model-specific algorithms.

### Data and state

What information the system keeps, where each piece lives, and how it moves and changes. Name the single source of truth for each important piece of state.

- The `Camera` instance is the source of truth for whether a webcam stream is active.
- The latest unmirrored tracking frame is the source of truth for detected hands, landmarks, handedness, pose reference points, and per-frame tracking time.
- Presentation settings hold whether the preview is mirrored, whether handedness needs correction, and whether body points are visible. These settings change display or interpretation deliberately; they do not mutate captured pixels invisibly.
- The capture controller is the source of truth for whether a scan is idle, waiting for readiness, counting down, capturing, ready to classify, or invalid. While capturing, it holds timestamped landmark frames in memory only.
- The recognition result contains either ranked supported candidates with scores or an unknown result with a reason. It is cleared when a new attempt begins.
- Supported vocabulary and label metadata come from a versioned project data file derived from the approved dataset subset. Training videos and extracted dataset landmarks are not shipped in the public app.
- `catalog/sign-catalog.json` is the single source of truth for sign metadata. `catalog/sign-catalog.schema.json` defines its machine-checkable structure, and the catalog validator adds cross-entry checks such as unique IDs and valid source references. A preparation script copies a validated, git-ignored build artifact into `app/public/data/` for the browser.
- Catalog entries use stable source-scoped IDs, identify their language as ASL (`ase`), keep English glosses separate from IDs, and record source version, license, attribution, status, and verified archive URLs. A `sample` or `candidate` entry is not presented as a supported sign.
- The catalog contains metadata and source links only. Raw videos, preview media, extracted landmarks, and other dataset files are neither copied into the catalog nor committed to the public app.
- The first vocabulary contains about 20–30 PopSign signs selected for adequate examples and visual distinction, with some movement-based and two-handed cases when the source data supports them. Selection is documented before training; favorite words alone are not a selection rule.
- Every model class has a stable ASL sign identifier separate from its displayed English gloss, so alternate meanings or gloss wording do not silently change the model label.
- A versioned preprocessing contract defines coordinate origin, scale, body-relative location, active interval, frame sampling or padding, missing landmarks, handedness, and sequence length. Offline training and browser inference use the same contract.
- The preprocessing contract includes broad location features, such as near the face, chest, or neutral signing space and left/right or above/below body anchors, rather than requiring an exact physical distance.
- Raw capture retains timestamps and every stable detailed hand result before normalization. The fixed model sequence is derived from the active signing interval; reducing model frames never changes the live overlay or raw capture cadence.
- Contract v2 retains all 21 local hand landmarks in `x/y/z`, shoulder-relative wrist `x/y`, relative wrist-depth movement, and explicit presence. It removes tracker confidence from recognition input but keeps confidence in quality metadata.
- Contract v2 uses nose, eyes, ears, mouth corners, shoulders, and elbows as upper-body anchors. Optional hips are removed. Body inputs use shoulder-normalized `x/y` and binary presence so both approved sources can supply comparable values.
- Absolute wrist depth is not a model feature. Visible wrist depth is centered within the active interval so toward/away movement remains while camera-dependent depth offset is removed.
- Sample dataset videos are reviewed with the extracted hand and body skeleton drawn over the original frames. This visual check verifies joint order, alignment, handedness, body anchors, and movement before extracted sequences are used for training.
- Left/right normalization is evaluated per sign. The system does not assume that mirroring every sign preserves its meaning.

### Interaction loop

How User input or other events lead to changes in state and then to what the User sees, hears, or receives.

1. The User starts the camera and grants permission.
2. Each new webcam frame is passed to the tracker once.
3. The overlay immediately draws boxes, joints, and connections, while text reports the tracking state.
4. The User corrects mirror or handedness presentation if the real-camera check shows it is reversed.
5. The User selects Scan a sign. The app waits for stable required landmarks, counts down, and captures one sign without a Finish action.
6. The capture controller stops at the tested maximum duration, applies only the approved trimming rule, and validates that the sequence contains enough usable tracking data.
7. The model returns ranked candidates or an unknown result.
8. The interface shows possible matches and their limits. The User may retry without reloading or granting camera permission again.

### Visual and content rules

The shared rules that establish the art style and keep the presentation consistent, such as branding, layout, color, type, motion, sound, and asset conventions.

- Use the working _Handshape_ identity: deep navy, warm coral, high contrast, rounded geometry, and a calm video-first layout.
- The AI-generated logo draft is an abstract brand mark, not a depiction of a specific ASL sign.
- Keep the camera, overlay, current status, attempt controls, and results visually connected in one coherent layout. Controls must not cover the hands in the video.
- Use coral for visible joint points and navy or another contrasting color for joint connections and hand boxes, subject to contrast testing against varied camera backgrounds.
- Pair visual tracking cues with short text such as `Both hands tracked`, `Tracking lost`, or `Move both hands into frame`.
- Draw joint names only in an optional calibration/debug view or on hover, focus, or tap; keep the normal overlay uncluttered. User-facing errors use readable names such as `right index fingertip`, not landmark numbers.
- Say `possible matches`, `supported signs`, and `single-sign recognition`. Do not claim conversational translation, complete form correction, or fluency assessment.
- Avoid unnecessary animation and sound. Reference video, if later included, must have captions or an equivalent written label and comply with its source license.

### Structure rules

The conventions that keep the system lean: how files and code are organized, where new features belong, and the general rules that handle cases by design instead of one-off fixes.

- Each module owns one responsibility: camera access, tracking, drawing, temporary landmark capture, recognition, or interface coordination.
- Recognition consumes a project-defined landmark-sequence type, not MediaPipe objects, so training and browser inference share an explicit input contract.
- The landmark contract uses canonical names rather than unexplained indexes: wrist; thumb CMC, MCP, IP, and tip; and MCP, PIP, DIP, and tip for the index, middle, ring, and pinky fingers. Selected body anchors are also named explicitly: nose, eyes, ears, mouth corners, shoulders, and elbows. Derived face, neck, chest, shoulder, elbow/forearm, and neutral-space regions use broad proximity rather than claiming exact physical contact.
- Landmark contract v1 is stored in `training/landmark-contract.v1.json`. It preserves hand orientation, normalizes hand shape to palm scale and body location to visible shoulder width, canonicalizes left-dominant signing into right-dominant coordinates, represents missing values explicitly, and resamples a reviewed sign interval to 64 frames. Facial-expression features are excluded from v1; vocabulary that depends on non-manual facial distinctions is not supported by the first model.
- Provisional landmark contract v2 is stored separately in `training/landmark-contract.v2.json` until its temporal sample count passes the approved fidelity test. It is source-neutral and does not overwrite v1 evidence. No v2 model is trained or exported before the Developer approves the final count.
- Mirroring is handled through one documented coordinate rule. Do not scatter left/right swaps or negative coordinates through feature code.
- Failure states are represented in shared app state and rendered consistently, not inferred independently by several UI elements.
- Model labels must come from the versioned supported-vocabulary file. The UI and model must not maintain competing label lists.
- Training and evaluation splits are grouped by signer so the same person cannot appear in both training and held-out evaluation data.
- Model files and the MediaPipe runtime are served locally by the static app. Secrets and API keys are not part of the browser build.
- Deployment configuration belongs with the app build rather than in feature modules. The GitHub Pages workflow publishes the production build and does not commit generated build output unless the deployment method requires it.
- Experimental performance displays may remain during the spike, but production-facing controls and copy should not expose unexplained developer metrics.

### Decisions and changes

Consequential structural decisions, the alternatives considered, and why you chose as you did, including later changes to the structure.

| Decision | Alternatives considered | Current reason |
|---|---|---|
| Specify an isolated-sign MVP with about 20–30 signs | Full 250-sign dataset or conversational translation | Small enough to train and measure in five weeks; matches the dataset's isolated-recognition use and avoids overclaiming |
| Track two hands, finger joints, motion, and body reference points | Static handshape or hands alone | Signs can depend on two hands, movement, and location relative to the body |
| Show hand boxes, joints, and connections | Hide tracking or show points only | Makes the system's evidence visible and helps separate tracking failure from signing performance |
| Keep raw coordinates unmirrored and mirror only the preview | Transform input frames or scatter coordinate reversals | One coordinate rule reduces handedness and overlay mistakes; a real-camera correction check remains required |
| Run webcam processing and inference locally | Hosted video or model API | Supports privacy, free static hosting, and no account requirement |
| Deploy with GitHub Pages | A custom server or paid host | The app is static, GitHub Pages is available with the repository, and no backend is required for the approved MVP |
| Use structured lookup filters before an LLM | Hosted or in-browser LLM at launch | The app should first test whether handshape and location filters add enough value without model download or server costs |
| Keep TensorFlow.js versus ONNX open | Commit to one runtime now | The export format and browser performance have not been tested yet |
| Target desktop Chrome on the Developer's Mac first | Promise broad desktop and mobile support immediately | Gives real-camera performance and behavior one reproducible initial target; other platforms can be checked after the core works |
| Use a bounded hands-free scan after one explicit action | Manual Start/Finish controls or fully automatic continuous segmentation | Avoids capturing button-reaching motion without adding open-ended continuous sign segmentation |
| Reduce or revise vocabulary if accuracy is inadequate | Keep all selected signs and lower expectations silently | Preserves an honest, usable result while model feasibility is still being tested |
| Use targeted local calibration and recalibration | Require full setup every visit or treat calibration as a model fix | Reduces normal camera/framing variation without blaming the User or claiming to solve recognition errors |
| Support ASL only and separate sign IDs from English glosses | Treat glosses as universal translations or include unsourced sign languages | Matches the sourced datasets and avoids implying that sign languages or English meanings are interchangeable |
| Build a small versioned Handshape catalog that references PopSign | Copy PopSign into a new database or claim an authoritative ASL dictionary | Gives the app and training tools one licensed metadata contract while preserving provenance and keeping media out of Git |
| Use Standard and Reduced device modes | One lowest-common-denominator tracker or many hardware tiers | Preserves detailed hands, makes reduced body support explicit, and avoids multiplying untested configurations |
| Revise preprocessing through a separate contract v2 | Keep incompatible v1 source features or overwrite historical evidence | Cross-source testing exposed reversed handedness, unequal clip intervals, and tracker-specific hip/visibility channels; a versioned contract keeps the correction reproducible |
| Default to "unknown" and show candidates as possible matches | Show the top candidate as the recognized sign, or reject with a confidence threshold | Nov 9 validation tests found that softmax-based scores separate supported from unsupported signs poorly, so a forced or thresholded answer would be confidently wrong too often; the Developer chose to assume the app does not know and offer candidates, with context guesses only as a later labeled feature |
| Keep continuous ASL transcription outside the five-week scope | Treat isolated gloss predictions as a transcript or expand immediately into conversation translation | Continuous translation needs sign segmentation, coarticulation, facial and spatial grammar, fingerspelling, context, and continuous-language data that the current isolated-sign sources and performance baseline do not provide |

### Provisional evaluation record

Each evaluated model version records:

- dataset source and exact supported vocabulary;
- training, validation, and held-out signer split counts;
- preprocessing-contract version and tracker/model versions;
- top-1 and top-5 accuracy on held-out signers;
- results for idle hands, non-signing gestures, unsupported signs, and poor tracking;
- processed frame rate, tracking time, and result time on the target browser and device; and
- known failure cases and any resulting scope change.

The exact performance and accuracy thresholds are deliberately unset until the first real-camera baseline and held-out-signer model result exist. Updating them is an expected spec revision, not a reason to overstate the first result.
