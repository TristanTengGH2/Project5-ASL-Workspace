# Session transcript: Contract v2, active intervals, and five-week scope

Saved November 9, 2026 at 20:33 CST. Messages are labeled Developer and Agent. Tool calls and output are summarized in brackets rather than reproduced. Credentials, dataset media, and identifiable source frames are not included.

---

**Developer:**

48 frames is good as a provision

**Agent:**

[Integrated landmark-contract v2 into the Google and PopSign source adapters, reran temporal fidelity on 150 Google sequences and 55 PopSign clips, generated a local active-interval review, found one suspicious `after` interval, documented the checkpoint, and pushed commit `b31ce6a`.]

48 frames is now provisionally confirmed against real v2 data from both sources.

- Google: 150 sequences passed.
- PopSign: 55 clips processed.
- Only 48 frames met all motion-retention thresholds.
- Visual review found one false-positive `after` clip with no visible hand; it should be excluded.
- No retraining or Phase 3 work started.
- Committed and pushed: `b31ce6a Integrate landmark contract v2 adapters`

Review the local, identifiable-participant sheet here: `training-artifacts/phase2-v2-active-interval-review/popsign-active-intervals.png`.

The training checks passed. The unrelated browser build was not completed because of the external Node PATH configuration; no app files changed.

Do you approve excluding visually rejected clips and reviewing the remaining PopSign intervals before the controlled retraining run?

---

**Developer:**

looking through the intervals, does it differentiate past motion blur, alot of the png middle images have some sort of blur. what do you mean excluding visually rejected clips

**Agent:**

It does not currently detect motion blur explicitly. MediaPipe analyzes each frame and may still return landmarks from a blurred hand. The model receives those landmarks—not the PNG pixels—but blur can produce inaccurate or jittery landmark positions.

A blurred middle image is not automatically a bad clip. Fast ASL movement naturally creates some blur, and removing every blurred frame could erase the movement we need to learn. More concerning cases are:

- No visible hand, but the tracker reports one.
- Landmarks jump to unrelated body parts.
- Most of the sign is obscured or outside the frame.
- The selected interval captures setup/reaching rather than the sign.

“Excluding a visually rejected clip” means marking that example as unusable and leaving it out of training. We would not delete the video. For example, the flagged `after` clip has no visible hand even though MediaPipe claims it detected one, so its generated landmarks should not teach the model.

My recommendation is to add a clip-quality review that flags excessive blur and landmark jumps, but does not reject ordinary movement blur. The reviewer would then approve or reject questionable clips before training. This would be the next Phase 2 checkpoint.

---

**Developer:**

can you show me an example of the clip

**Agent:**

Here is the rejected `after` example:

`datasets/popsign-v1-0/phase2-five-sign/test/after/gtsignstudy4a.8037-after-2023_01_26_22_56_49.401-0.mp4`

The tracker selected approximately **0.00–0.67 seconds** as the active interval, despite no clearly visible signing hand. That makes its generated landmarks unreliable for training.

---

**Developer:**

from human view its is visible what they are doing, can you show me the tracking that it did?

**Agent:**

[Inspected the saved MediaPipe overlays for the exact clip. The first overlay showed hand landmarks incorrectly attached to the signer's face; later overlays showed the actual moving hand.]

You’re right—the clip contains a valid sign. The tracking overlay reveals that our interval selection was wrong.

- Frame 0: incorrect hand landmarks placed on the signer’s face.
- Frame 31: actual hand detected.
- Frame 46: actual hand movement detected.

The yellow/red lines are the detected hand joints. At frame 0, MediaPipe mistakenly interpreted facial features as a left hand. Our “longest tracked run” rule then selected that false detection and missed the real sign later in the clip.

So the clip itself should not be excluded. Its current extracted interval should be rejected and regenerated. We need to revise the interval-selection rule before training, then rerun the 48-frame test.

---

**Developer:**

how much does the initial like bringing the hand up from rest matter for signs. especially for signs like after. You should review mediapipe's scan just to be safe

**Agent:**

[Reviewed official MediaPipe Hand Landmarker documentation and sign-segmentation research. Replayed all 69 frames through the project's exact MediaPipe thresholds, generated a local full overlay video and contact sheet, and inspected the detection timeline.]

The initial lift matters somewhat, but it should not dominate the sample.

A sign has a preparation phase, a meaningful stroke/hold, and a retraction phase. The model should retain a short part of preparation so it sees the starting handshape, orientation, and location. It generally should not learn the entire movement from the signer’s lap or resting position, because that varies with seating, camera placement, and signing style. Transitional movement is recognized as a separate segmentation problem in sign-language research.

For `AFTER`, the starting relationship and subsequent movement matter: one common form begins with the dominant hand over the non-dominant hand, followed by the dominant hand moving over it. Therefore, cutting directly to the middle would lose meaningful information.

### MediaPipe scan review

I reviewed all 69 frames using the project’s exact MediaPipe settings. The local evidence is stored at:

- `training-artifacts/phase2-v2-active-interval-review/after-8037-full-mediapipe-overlay.mp4`
- `training-artifacts/phase2-v2-active-interval-review/after-8037-mediapipe-scan-sheet.png`

What happened:

- Frames 0–18: MediaPipe intermittently places hand landmarks on the signer’s face.
- Frames 19–26: no hand detection.
- Frames 27–34: the real hand rises from rest into signing position.
- Frames 35–46: MediaPipe follows the main hand movement reasonably well despite some blur.
- After frame 46: the hand disappears from tracking.

So motion blur is not the main failure here. The real moving hand is tracked reasonably consistently. The problem is that our interval rule tied the false face run with the real-hand run and selected the earlier one.

MediaPipe’s returned score in our overlay data is handedness certainty, not proof that the detected object is actually a hand. Its internal presence and tracking thresholds control when detection is accepted, but those scores are not included in the result object we receive.

My recommended correction is:

- Prefer a dense, sustained detection run over an intermittent one.
- Keep several frames before the meaningful movement to preserve handshape formation.
- Retain the actual stroke and a short ending.
- Flag questionable one-hand detections for signs expected to use two hands.
- Continue producing overlay reviews before training.

For this clip, that would likely select roughly frames 27–48 rather than frames 0–20. This changes the interval-selection rule, so I would rerun extraction and the 48-frame fidelity test afterward.

---

**Developer:**

make sure to document all of this discussion btw, not only this but whatever you think is meaningful from earlier discussion. Also I wanted to discuss about waht would be possible in my 5 week plan. Would it only be a database where we can also have interpretive signs where you mismatch parts of signs together for words that dont directly exist in sign language

**Agent:**

[Reviewed the current `plan.md`, `spec.md`, `pitch.md`, and `research.md`, plus authoritative sources on fingerspelling, compounds, lexical innovation, and unfamiliar terminology.]

No—it does not have to become only a database. A realistic five-week result can combine:

- A small working webcam recognizer for a tested vocabulary.
- A searchable, open metadata catalog of established signs and variants.
- Component-based lookup using handshape, location, movement, orientation, and number of hands.
- A “request a term” feature for missing concepts.
- Guidance on how an unfamiliar term is conventionally expressed.

What should not be promised in five weeks is automatically creating valid ASL signs by freely mixing pieces. ASL does form compounds, lexicalized fingerspelling, and other new vocabulary, but these follow linguistic conventions; arbitrary combinations may be meaningless or misleading.

A safer catalog record for a term without one direct sign could say:

- Established lexical sign, if sourced.
- Fingerspell the English term.
- Use an established compound.
- Use a descriptive ASL phrase or depicting construction.
- Domain-specific variant and where it is used.
- Sources and verification status.
- “Community review needed” for a submitted proposal.

The app could show these as “ways this concept is expressed,” not claim that it generated an official sign.

### Realistic revised schedule

1. **Current checkpoint:** Correct interval selection, preserve meaningful preparation, rerun the five-sign v2 model.
2. **Browser prototype:** Integrate the small supported model if the held-out result is acceptable.
3. **Catalog and lookup:** Search established signs by English concept and visual components.
4. **Missing-term workflow:** Add term requests and sourced expression strategies—fingerspelling, compounds, or descriptions.
5. **Finish:** Unknown handling, accessibility, testing, documentation, and GitHub Pages deployment.

The database/catalog is the dependable deliverable. The recognizer remains an experimental feature whose supported vocabulary depends on the next evaluation. A general translator or automatic sign inventor is outside five-week scope.

For documentation, I proposed updating `research.md`, `plan.md`, and `spec.md` to correct the `after` finding, record the full scan, preserve 48 as provisional, document sourced variants and expression strategies, and exclude unsourced automatic sign invention and conversation translation. The approved `pitch.md` would remain unchanged.

---

**Developer:**

what about slanged signs, is there documentation on how that works?

**Agent:**

[Reviewed ASL Signbank, ASL-LEX, ASLLRP, regional-variation research, and academic work on ASL lexical and taboo innovation.]

Yes. ASL slang is documented, but usually through recorded community usage rather than a formal rulebook.

Slang can develop through:

- Existing signs taking on new meanings.
- Shortening or modifying established signs.
- Lexicalized fingerspelling.
- Compounding signs.
- Borrowing from particular communities or cultural settings.
- Nonmanual features such as facial expression, intensity, or signing style.

It also overlaps with—but is not identical to—regional variants, generational vocabulary, dialects such as Black ASL, idioms, and informal register.

For our catalog, slang should be represented as an attested variant, not simply another English translation. A slang record would need:

- Meaning in context.
- Video or corpus source.
- Region and community, when known.
- Approximate generation or period.
- Formal, informal, humorous, taboo, reclaimed, or other register.
- Related standard or widespread sign.
- Handshape, location, orientation, movement, and nonmanual features.
- Verification status and date last reviewed.
- A warning when meaning or acceptability varies between communities.

Within five weeks, we could make the catalog capable of storing slang and add a few properly sourced examples. Training the recognizer on slang would come later because it requires enough licensed examples from multiple signers and communities. A “request this slang/variant” workflow would be realistic now.

I recommend supporting documented slang and regional variants, while preventing the app from declaring an unsourced submission to be accepted ASL. I’ll include this distinction in the planned documentation update.

---

**Developer:**

okay, for reading asl and turning it into a transcript, would that be possible? i would want it to be able to keep up incase they use slang

**Agent:**

[Reviewed current continuous ASL recognition/translation research, How2Sign, FLEURS-ASL, and recent work on fingerspelling within translation.]

A true real-time ASL-to-English transcript is possible as a research direction, but not responsibly achievable within this five-week project—especially with open-ended slang.

There are three different features that could be called a “transcript”:

1. **Recognized-attempt history — feasible now**  
   Each deliberate scan adds a timestamped result such as `AFTER`, `PEN`, or `[unknown]`. Users can correct a result. This is a session log, not sentence translation.

2. **Limited continuous gloss stream — possible stretch goal**  
   The camera detects a small supported vocabulary in sequence, preferably with pauses. Output might be `I / GO / STORE`, but that is not yet grammatical English and would not reliably handle slang.

3. **ASL-to-English translation — outside five-week scope**  
   This requires continuous segmentation, coarticulation, ASL grammar, facial/nonmanual information, spatial references, classifiers, fingerspelling, context, and English generation.

Our current PopSign data is intended for isolated-sign recognition, not conversation translation. The current browser also cannot track hands, body, and face together fast enough: full Holistic tracking dropped to 11 results per second in our test.

A responsible system should therefore:

- Recognize supported established and slang variants.
- Detect likely fingerspelling separately.
- Return `[unknown sign]` when evidence is insufficient.
- Save a short timestamped segment for user review.
- Search the catalog for regional or slang candidates.
- Never have an English language model silently guess the missing ASL.

### Recommended five-week scope

Build a **timestamped recognition log**, not claim a full transcript:

```text
00:03  AFTER       78%
00:06  [unknown]   possible fingerspelling
00:09  PEN         84%
```

The user could open an unknown segment, compare slang and regional candidates, correct it, or submit a catalog request. A future continuous translator could build on those reviewed sequences.

My recommendation is to call the five-week feature **Attempt history** or **Recognition log**, reserving “ASL transcript” for a later continuous-language project. This distinction should also be recorded in the specification so the interface does not overstate what it understands.

---

**Developer:**

lets leave this for outside of the current scope for the 5 weeks, but if we get done early we can consider it.

**Agent:**

[Updated `spec.md`, `plan.md`, `research.md`, and `evidence/image-history.md`; corrected the earlier interpretation of the `after` clip; documented preparation versus stroke, slang/variant catalog considerations, and the decision to defer continuous transcription; committed and pushed `306f6a0`.]

Documented and pushed in commit `306f6a0`.

The project now explicitly states:

- Continuous ASL-to-English transcription is outside the five-week scope.
- It may be reconsidered only if the isolated-sign product finishes early.
- A list of isolated results must be called a recognition log, not a transcript.
- Slang-aware transcription requires separate continuous-language data and evaluation.
- The `after` clip is valid; its MediaPipe interval was incorrectly selected.
- The next checkpoint is revising interval selection and rerunning the 48-frame fidelity test.

The working tree is clean.

---

**Developer:**

what currently are we aiming to make btw, remind me

**Agent:**

We’re building **Handshape**, a free browser app for recognizing and looking up individual ASL signs.

The five-week target is:

- Live webcam tracking with visible hand boxes, joints, and movement.
- A hands-free “Scan a sign” flow.
- Recognition of a small, honestly tested ASL vocabulary.
- Up to five possible matches or `Unknown`.
- A searchable sign catalog with sourced signs, variants, visual properties, and attribution.
- Lookup help based on handshape, location, orientation, and movement.
- Local processing with no account, microphone, or uploaded webcam video.
- Public deployment through GitHub Pages.

We are not currently building:

- Full ASL conversation translation.
- ASL-to-English transcripts.
- Automatic invention of new signs.
- Fluency grading or replacement for interpreters/teachers.
- Guaranteed recognition of unrestricted slang.

Right now we’re still finishing Phase 2. The immediate task is to correct the interval selector so it chooses the real sign instead of false MediaPipe detections, then rerun the 48-frame test before retraining the five-sign model.

---

**Developer:**

after you tell me, keep going on the rerun or whatever you were asking me to check

**Agent:**

[Specified the checkpoint as revising active-interval selection to prefer a dense sustained detection run, retaining a short preparation lead-in, regenerating both v2 sources, and rerunning the 48-frame comparison. Added a shared sustained-run score, updated the contract, added manifest quality metadata, and added three regression tests. The first test invocation could not resolve the neighboring module from the repository root; rerunning with the training directory on Python's import path passed all three tests.]

The governing bug is the tie-break: the old rule compared bridged span length, so twelve intermittent face detections spanning nineteen frames tied nineteen continuous real-hand detections. The shared rule now scores each candidate by sustained detections and density, while keeping the existing two-frame context so the hand’s final approach into starting position is preserved.

[Re-extracted the exact `after` clip with the revised rule. It decoded 69 frames with 46.4% hand coverage and wrote a local rerun manifest. Full two-source regeneration and temporal-fidelity comparison had not yet run when the Developer requested the transcript.]

---

**Developer:**

save trascript

**Agent:**

I’m pausing the interval rerun long enough to save this session transcript in `transcripts/`, labeled `Developer` and `Agent` as required. The generated file will contain the available conversation text and decisions from this session; it will not include dataset media or credentials.
