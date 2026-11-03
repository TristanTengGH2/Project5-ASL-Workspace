# Session transcript: MediaPipe research and PopSign catalog

Saved November 2, 2026 at 19:47 CST. This continues after `2026-11-02_1611_specification.md`. Messages are labeled Developer and Agent. Tool calls and output are summarized in brackets rather than reproduced.

---

**Developer:**

would mediapipe be a good reource for this?

**Agent:**

[Checked the current official MediaPipe Hand, Pose, and Gesture documentation and repository license.]

Yes—MediaPipe is a strong choice for the tracking layer, but not the ASL recognition model itself.

Hand Landmarker supports two hands and returns handedness plus 21 landmarks per hand in image and world coordinates. Pose Landmarker supplies 33 body landmarks, including shoulders, elbows, face references, and visibility estimates. Both are available in the browser through `@mediapipe/tasks-vision`.

MediaPipe does not provide our ASL vocabulary, temporal understanding of a moving sign, ASL grammar, reliable unknown rejection, or guaranteed tracking through overlap and blur. Its Gesture Recognizer processes generic gestures frame by frame rather than providing a temporal ASL model. Its video detection methods also block the browser interface thread unless moved to a worker.

The planned architecture remains appropriate: MediaPipe hands and pose produce a normalized landmark sequence, which a separate trained ASL recognition model turns into ranked matches or Unknown. The existing spike already uses this foundation.

---

**Developer:**

is there already a usable library or is that somehting not already in the market

**Agent:**

[Searched current primary sources for reusable ASL recognition libraries, code, checkpoints, and licenses.]

There are usable research libraries and pretrained models, but no dependable, drop-in browser library was found that recognizes the chosen ASL vocabulary with clearly reusable data and model terms.

Microsoft released archived ASL Citizen baseline code and checkpoints, OpenHands provides unmaintained pose-based research tools and checkpoints, and SignBart publishes lightweight research code and weights but did not show a repository license. PopSign's authors used MediaPipe hand features and a bidirectional LSTM, but their baseline is not a plug-and-play browser package.

The recommendation was to keep MediaPipe, investigate PopSign's processed landmarks and baseline, train or fine-tune a small 20–30-sign model with the project's exact preprocessing and signer split, and export it only after its results are verified.

---

**Developer:**

what about non-standard vocab, like words that would have to be made up on the spot.

**Agent:**

[Verified ASL fingerspelling and context-dependent depicting-construction distinctions using Gallaudet and academic sources.]

A model cannot infer the meaning of a completely new sign from motion alone. Concepts without an established sign commonly use fingerspelling, while depicting/classifier constructions derive meaning from context and signing space. User-created gestures must not be presented as verified ASL.

For the MVP, unseen vocabulary should return No supported match. A future fingerspelling mode is the most useful conventional fallback. Emerging or regional signs require sourced review; personal gestures must remain explicitly separate from verified ASL.

---

**Developer:**

i got approval for the idea, but i was wondering if i can create a sign request addition

**Agent:**

Yes. A Request a sign feature fits if it requests vocabulary expansion rather than allowing users to create and publish supposed ASL signs directly.

A request can collect an English term or concept, an example sentence, whether an existing sign was encountered, and optional source or regional context. It must not update the model immediately. Requests must be checked against supported datasets, verified, confirmed to have sufficient licensed examples, retrained, evaluated, and released as a versioned update.

Because GitHub Pages has no backend, the recommended development implementation is a GitHub issue form. A third-party form is friendlier for general users but introduces a privacy dependency; a custom backend is outside the current static-site scope.

The Developer also reported Studio approval, satisfying the approval gate.

---

**Developer:**

like button

**Agent:**

Yes—a visible Request a sign button. Recommended placement is beside the supported vocabulary, in a No supported match result, and optionally in help. It should open a short request form and explain that requests are reviewed and do not create or verify ASL signs. The label should be Request a sign rather than Add a sign.

---

**Developer:**

so would creating a database being open source for a use for this be a market gap?

**Agent:**

[Reviewed current PopSign, ASL Signbank, Global Signbank, ASL 1000, and related official resources.]

An open-source ASL database by itself is not an empty market gap. PopSign, ASL Signbank, Global Signbank, ASL-LEX, and newer resources already cover substantial parts of the space under different access and license terms.

A narrower possible contribution is a browser-focused developer layer combining permitted stable sign IDs, English glosses and variants, sign parameters, dataset class IDs, source licenses, reference links, a versioned MediaPipe schema, model support, evaluation, and request status. This remains a possible gap, not a proven market gap.

For the five-week project, the recommendation was to build a small open-source catalog/adapter for supported signs, preserve provenance, link sources, and avoid creating or claiming an authoritative ASL database.

---

**Developer:**

so would mediapipe be a good respurce since we also have to track facial expression in ASL

**Agent:**

[Checked the current official MediaPipe Face Landmarker documentation and academic work on ASL nonmanual marking.]

MediaPipe is useful for measuring facial motion but does not interpret ASL facial grammar. Face Landmarker outputs 478 face landmarks, 52 generic expression blendshapes, and head transformation data. Those are measurements, not labels such as ASL negation or question marking. ASL nonmanuals also depend on timing and linguistic context.

For the approved MVP, use face references for location and optionally measure blendshapes experimentally, but do not grade or interpret facial expression at launch. Required nonmanual recognition would need a labeled dataset, ASL review, additional browser performance work, and a material scope update.

---

**Developer:**

okay, should we get started referencing popsign's database to create a library

**Agent:**

[Checked the current official PopSign version pages, download guide, source routes, and licensing.]

Yes, but as a small versioned Handshape sign catalog that references PopSign rather than copying PopSign or claiming an authoritative database. The proposed catalog goal was one source of truth for the browser and training tools, with stable IDs, ASL language code, separate English glosses, exact source version, license, attribution, status, and source URLs. Raw videos and landmarks stay out of Git.

The proposed first checkpoint was to verify a downloadable release, define and validate a schema, add five structural samples, verify source links and split availability, and expand to 20–30 candidates only after reviewing the structure.

---

**Developer:**

Okay, lets continue

**Agent:**

[Inspected the app structure. Verified that the official PopSign v1.0 archive route returned HTTP 200 while the equivalent v2.1 route returned 404. Verified train, validation, and test archives for `after`, `hear`, `man`, `pen`, and `puppy`. No dataset archives were downloaded.]

[Updated the specification, plan, research, and project instructions. Added a formal JSON Schema, a five-entry metadata-only catalog, an Ajv validator, dataset/training-artifact ignores, and catalog validation to the app build. Installed Ajv as a development dependency. The first validator run used Ajv's older default draft and failed; the import was corrected to Ajv 2020 and the second run passed.]

Created the first working Handshape sign catalog infrastructure. Validation reported five signs, one source, schema version one. The production build passed, the deployed catalog matched its source, npm reported no vulnerabilities, and no videos or landmark archives were downloaded. The five signs remained structural samples rather than selected MVP vocabulary.

---

**Developer:**

should the catalog be a separate repo?

**Agent:**

Not yet. A separate repository would add independent releases, cross-repository coordination, duplicated documentation, and the risk of incompatible schema versions. The recommendation was to keep a self-contained `catalog/` module in the Handshape repository and split it only after another consumer, independent maintainers, separate governance, or independent releases exist.

---

**Developer:**

okay what next

**Agent:**

The next sequence proposed was to move the source catalog into the root module, add a preparation script, add a catalog README, validate and build, commit and push the catalog checkpoint, and then begin the separate real-camera tracking baseline.

---

**Developer:**

how do i do 2

**Agent:**

The preparation step was explained as a small Node script that copies the validated root `catalog/sign-catalog.json` into `app/public/data/sign-catalog.json`. Package scripts would run validation and copying before development or production builds, and the generated app copy would be git-ignored so it could not drift from the source.

---

**Developer:**

can you do that?

**Agent:**

[Moved the source catalog under `catalog/`, added `prepare-catalog.mjs`, updated validation and npm scripts, ignored the generated copy, and updated the architecture documentation. The first move patch expected an old path and made no changes; the actual current path was inspected and the corrected patch succeeded.]

Implemented the catalog preparation flow. `npm run dev` and `npm run build` now validate the root catalog and generate the app copy. The generated file matched the source and was confirmed git-ignored. The production build passed.

---

**Developer:**

okay what is next

**Agent:**

The next steps were to add `catalog/README.md`, run validation and build, save the transcript, commit and push the catalog checkpoint, then begin the separate real-camera tracking baseline with hand boxes, landmark labels, mirror/handedness testing, and performance measurements.

---

**Developer:**

just do these steps

**Agent:**

I’ll complete and push the catalog checkpoint first, including its README and a new transcript. Then I’ll begin the separate tracking checkpoint by adding hand boxes and optional landmark labels, verify the build, and stop at the real-webcam test that requires you.

[Added the catalog README. This transcript was then saved before final catalog validation, commit, and push.]
