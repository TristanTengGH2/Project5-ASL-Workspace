# Session transcript: resuming the project, interval selector, GRU retrains

Saved 2026-11-09 20:33. Messages are labeled Developer and Agent. Tool calls and tool output are summarized in brackets, not reproduced.

This file continues the same conversation as `2026-11-02_1547_pitch-and-tracking-spike.md`, which covers everything up to the push of the tracking spike and the first transcript save. Between those two dates the repository also received work from other sessions (see the commit log); those sessions' transcripts are the other files in this folder where they were saved.

---

**Developer:**

do you have what codex was just working on? Can you keep working off of it and make sure to have a commit for any big milestones you have?

**Agent:**

[Inspected the repository. Found the log running from Nov 2 to Nov 9 (catalog, worker spikes, landmark extraction, Google landmark bridge, contract v2) and six uncommitted training files. Read the plan's checkpoint and evidence sections, the project rules in AGENTS.md, and the uncommitted diff. Ran the unit tests (3 passed). Regenerated the contract-v2 intervals for both sources into new local folders. My first PopSign extraction accidentally used a 3-clip folder instead of the 55-clip folder; I noticed from the example count, deleted those outputs, and reran on the right folder. Ran the 48-frame fidelity test and compared old and new intervals. Rendered and viewed a local review sheet. Updated plan.md and training/README.md, committed `fa1a05c`, and pushed.]

I have no record of Codex's work in this conversation, so I'll check the repo for what it left behind.

Codex's trail is in the repo: nine days of commits and uncommitted edits. It was in the middle of revising the active-interval selector, the step the Nov 9 plan entry names as the next gate. Let me look at the unfinished test and how to run things.

Both sources are regenerated with the new selector. Next I'm running the 48-frame fidelity test on them and comparing the `after` clip against the old result.

The new PopSign result used only 3 clips, not the 55 the plan cites. I pointed the extractor at the wrong folder, so I'm checking which folder holds the 55 clips and rerunning.

The 48-frame recommendation holds on all 205 sequences, and PopSign's weakest clips now retain 100% of their motion (it was 83.4% at the 10th percentile). Now I'll check the `after` clip that the old selector got wrong.

The review sheet confirms it. The `after` clip's interval now covers 0.87–1.60 s, where the hand is raised and moving, and no longer the false-detection frames at the start. Next I'll update the docs that still describe the old rule, then commit.

I don't have Codex's session. I picked up its work from the repo, and since 2 Nov it has built the training pipeline and the PopSign catalog. It was partway through one step when it stopped, and I've finished that step and pushed it.

**Where it stopped**
The 9 Nov plan gate said to revise the active-interval selector, regenerate the intervals, and repeat the 48-frame fidelity test before retraining. The selector change and a new test file were uncommitted.

**What I did**
- **Tests:** the three unit tests in `training/test_landmark_contract_v2.py` pass.
- **Regenerated:** I re-ran both adapters into new `*-v2b-*` folders, so the old evidence is untouched. That covered the 150 Google sequences and the 55 PopSign clips.
- **The bad clip:** the PopSign `after` clip (signer 8037) was being trimmed to the false face detections at 0.00–0.67 s. It's now 0.87–1.60 s, and the review sheet shows the raised, moving hand. It was the only PopSign clip whose interval changed. Five of the 150 Google intervals changed.
- **Fidelity at 48 frames:** it still passes on both sources, so the 48-frame choice stands. PopSign's 10th-percentile motion retention rose from 83.4% to 100%.
- **A concern I didn't resolve:** in 27 of the 150 Google intervals and 1 PopSign clip, the dominant hand is detected in under 60% of frames. I haven't reviewed or filtered them.

**Commit**
`fa1a05c` is pushed to origin/main. I updated `plan.md` and `training/README.md` with the evidence, and no secrets, datasets or artifacts were staged. I made one mistake on the way: I first pointed the PopSign extraction at the 3-clip folder and caught it from the clip count before using any result.

I didn't retrain the model or start Phase 3. The plan says retraining needs your approval, and the earlier GRU runs missed the 70% target (48% test top-1).

Decision for you: retrain the one approved GRU on the regenerated v2 tensors, with or without filtering the low-detection intervals first?

I'll commit and push each verified checkpoint as I go. I'll stop at the plan's decision gates, such as retraining.

---

**Developer:**

[IDE note: the user opened plan.md.]

which one are you reading for the plan 5 wk map, the one in file or the one in vs code

**Agent:**

[Read the Five-week map section of plan.md.]

I read the file on disk. I can't see unsaved edits in your VS Code editor, so anything you've typed but not saved isn't visible to me. I also haven't read the Five-week map section yet. I only read the checkpoint and evidence sections. Let me read it now.

That is the five-week map as saved on disk. Phase 2 (Nov 2–9) is the phase still open, since the first held-out-signer model result missed the 70% target. Phase 3 (Nov 9–16) is the temporary browser capture and ranked results, which is blocked until the model clears that gate.

If you've changed the map in VS Code and haven't saved it, save the file and tell me. I'll re-read it before doing anything that depends on it. If you meant a different map, such as the one in `pitch.md` or `spec.md`, tell me which and I'll check that one too.

---

**Developer:**

its alright, what is next iwth what we have to do

**Agent:**

[Checked the PopSign site certificate: it still shows an expiry of Nov 8, 2026, and a plain request fails.]

The next step is a decision for you. Phase 2 is still open, and today is the Nov 9 milestone check.

**Where things stand**
- **Tracking baseline:** done earlier.
- **First model result:** the one approved GRU scored 48% test top-1 on the Google landmarks, against a 70% target.
- **Fixes since then:** handedness, a shared contract v2, and the interval selector are now corrected. Nothing has been retrained on the corrected data yet.
- **PopSign downloads:** still blocked. The site's certificate expired on Nov 8, I just rechecked, and we're not bypassing verification.

**Options for the next step**
1. **Retrain the one approved GRU on the regenerated v2 tensors.** This is the plan's next step, and it takes minutes to run.
   - If it reaches 70%, Phase 3 (browser capture and ranked results) opens.
   - If it misses, the plan says to review data and vocabulary, not add architectures.
2. **Filter or flag the sparse intervals first, then retrain.** 27 of the 150 Google intervals have the dominant hand detected in under 60% of frames, so they may be dragging the score down. This risks tuning the data toward the result, so I'd set the rule before looking at any new scores.
3. **Report at the milestone as "Phase 2 blocked, not failed".** You'd show the tracking baseline, the audit findings, and the corrected pipeline.

My recommendation is to do option 1 first, with no filtering. That gives a clean before-and-after of the pipeline fixes. If it misses 70%, decide on filtering with that result in front of you.

**Other open items**
- PopSign: check the certificate again in a day or two, since it's the official source.
- The Phase 3 browser work can't start until the model clears the gate, unless you approve a reduced vocabulary.
- If you want, I can draft your Nov 9 milestone summary from `plan.md`'s evidence log.

Which should I do: retrain unfiltered, filter first, or write the milestone summary?

---

**Developer:**

lets do option 1

**Agent:**

[Found that train_temporal_model.py only accepted the v1 contract. Changed it to choose the contract file and hand-block width from the manifest's contract version. Trained the single GRU on the regenerated v2 data (best epoch 16, validation 44.0%, test 52.0%). Ran the frozen-model PopSign check (34.5%). Regression-checked the trainer on a v1 manifest. Recorded the result in plan.md, committed `f4c924a`, and pushed.]

The trainer is hard-wired to the v1 contract and will refuse a v2 manifest, so I need a small change before the retrain. Let me read the parts that depend on the contract.

Retrain finished and missed the gate. I'm running the PopSign transfer check on the frozen model now.

I retrained the one approved GRU on the regenerated v2 data. It missed the 70% gate again, with 52% test top-1, and the result is pushed as `f4c924a`.

**Result**
- **Same data and settings as before:** 150 signer-separated Google sequences (20 train, 5 validation and 5 test per sign), same seed, `48 x 167` inputs.
- **Accuracy:** validation 44.0% and test 52.0% (13 of 25), against the 70% gate. The earlier run scored 60.0% validation and 48.0% test.
- **Noise:** with only 25 test clips, one clip is 4 points. The change from 48% to 52% is one clip, so it isn't evidence of improvement.
- **Overfitting:** training loss reached 0.02 while validation loss rose after epoch 20. 100 training clips look too few.
- **Per sign (test):** `after` 2/5, `hear` 4/5, `man` 3/5, `pen` 2/5, `puppy` 2/5.
- **PopSign check:** the same frozen model scored 34.5% on the 55 PopSign clips (33.3% on the 15 official test clips), up from 25.5% before. Chance is 20%. It's better, but nowhere near usable.
- **Unknown handling:** unknown-input rejection still isn't implemented, and synthetic idle and missing-hand inputs still get confident predictions. I exported nothing.

**What I changed**
I made the trainer pick its contract and hand-block width from the manifest, so it accepts v2. I checked that a 2-epoch run on a v1 manifest still works.

**The plan says to stop and review here, not add models.** Your options:
1. **More training data:** more than 20 clips per sign. The model is overfitting, so this may help most. The Google corpus has far more clips than the 150 we pulled.
2. **A smaller or different vocabulary:** some pairs may be too hard to tell apart at this sample size.
3. **Accept a deliberately tiny proof vocabulary** for the browser demo and say so plainly.

My recommendation is option 1 first, because the plan's own diagnosis (too little data) matches what the loss curve shows. It needs your approval for a bigger download and a new target size, since the plan fixes the sample at 20 per sign. Which do you want?

---

**Developer:**

I also like 1 for now, it makes sure there is enough data to work with and be sure on.

**Agent:**

[Counted the Google corpus: 21 participants in total; per-sign clips available in each participant-disjoint split (13 train, 4 validation, 4 test participants).]

Before I pick a size, I'm checking what the Google corpus can actually supply for these five signs. The split is by participant, so that sets the limit.

The Google corpus can supply more clips, but it has a ceiling that matters for what option 1 can prove.

**What's available for these five signs**
- The whole corpus has only **21 participants**. The importer's participant-disjoint split gives 13 train, 4 validation and 4 test signers.
- Clips available per sign in each split, with the smallest count in bold:

| Split | after | hear | man | pen | puppy |
|---|---|---|---|---|---|
| Train | 231 | 272 | 250 | 267 | 247 |
| Validation | 65 | 72 | 80 | 77 | 67 |
| Test | 51 | 61 | 62 | 55 | **43** |

**What more clips can and can't fix**
- It should reduce the overfitting I saw, because the model currently trains on only 20 clips per sign.
- It won't add signer variety. Extra clips come from the same 13 training signers, so held-out accuracy can still be limited by signer variety. Still, 4 test signers and 25 test clips is a very noisy measurement, and a larger test set would make the next result much more trustworthy.

**What I recommend**
- **80 train, 20 validation and 20 test clips per sign.** That's 400, 100 and 100 clips in total, 600 sequences against today's 150.
- It's well inside the limits above, and the test set grows from 25 to 100 clips, so one clip is 1 point instead of 4.
- It keeps the same seed and participant split. If the importer's shuffle behaves as I expect, the earlier 150 sequences stay inside the new set, so the comparison is fair. I'd verify that before training.
- The download should be roughly 370 MB, estimated from the 92 MB the 150 existing files take. It goes into the Git-ignored `datasets/` folder and uses the Kaggle token you already set up outside the repo.

The plan fixes the sample at 20/5/5 per sign, so this needs your approval. Same rules as before: one GRU, the same 70% gate, and no model changes. If it still misses, we'd be down to vocabulary or accepting a tiny proof set.

Should I go ahead with 80/20/20, or would you prefer different numbers?

---

**Developer:**

With this, we will have how many terms we are doing?

**Agent:**

[Checked what spec.md and plan.md say about vocabulary size.]

Five signs for this test: `after`, `hear`, `man`, `pen` and `puppy`. Option 1 adds more clips for those same five and doesn't add terms. With 80/20/20 per sign, that's 600 sequences in total.

Five is a feasibility test, not the planned product vocabulary. [spec.md](spec.md) sets the first real vocabulary at about 20–30 PopSign signs, which would be chosen later. I'm using five so a single change in the data is easy to compare against the earlier runs.

Two caveats on widening:
- **Signs:** the five were chosen for the earlier tests. Hard-to-tell-apart pairs may be limiting accuracy, and I haven't checked that. A different or larger set would be a separate decision.
- **Data source:** the Google corpus has 250 signs and the same 21 signers, so more signs doesn't fix the signer-variety limit.

Do you want to keep the five signs and go ahead with 80/20/20 per sign?

---

**Developer:**

we have alot of vocab to go through no? how long would this take? are we done with phase 2 yet?

**Agent:**

No, Phase 2 isn't done, and yes, there's a lot of vocabulary left.

**Phase 2 status**
- **Done:** the real-camera tracking baseline, and a five-sign PopSign sample.
- **Not done:** a held-out-signer result that clears the 70% gate. The best so far is 52%, and unknown-sign rejection doesn't exist yet.
- The plan keeps Phase 2 open until you approve a way forward. The official PopSign downloads are also still blocked by the expired certificate, so the Google corpus is a stand-in.
- At today's Nov 9 meeting you can report it as "blocked on model accuracy, not failed", with the pipeline fixes and measurements as evidence.

**Vocabulary**
- We have 5 signs and the spec wants about 20–30, so most of the vocabulary is still to do.
- I wouldn't scale up first. If five signs can't reach 70% even with 80/20/20, more signs won't help. Passing on five tells us the pipeline works before we widen it.

**How long it takes**
These are estimates, not timings:
- **The 80/20/20 five-sign run:** it should take well under an hour, mostly downloading about 370 MB. The extraction and training runs I did today each finished within a few minutes.
- **A 25-sign vocabulary:** roughly five times the data and a few GB of download. The compute is still manageable. The real cost is your review time per step, the decision gates, and picking signs sensibly.
- **The bigger schedule risk:** accuracy, not compute. Phase 3, the browser capture and ranked results, can't start until a model clears the gate. Peer review is Nov 30 and final delivery Dec 7.

**What I'd do**
1. Run the five-sign 80/20/20 test now. It's the cheapest way to learn whether data quantity is the problem.
2. If it passes, widen in stages, such as 10 signs and then 25, with the same gate each time.
3. If it misses, the next question is which signs are being confused, and whether to pick a different vocabulary.

Do you want me to go ahead with step 1 at 80/20/20?

---

**Developer:**

I'm asking if we did this for EACH sign how long would it take

**Developer (sent mid-turn):**

I am okay with doing this for the first 5 signs

**Agent:**

[Timed the conversion of the 150 cached sequences (8.3 s), a fresh 20-file download (about 19 s), and a short training run (10 epochs in 3.5 s). Started the 80/20/20 import in the background. It failed at file 389 of 600 with a Kaggle read timeout after about 23 minutes. Retried once; the retry reused cached files and finished in about 3 minutes. Verified the new data: 600 sequences, the earlier 150 included, participants disjoint, all tensors finite 48 x 167. Trained the single GRU. Ran the frozen-model PopSign check.]

Good question. I'll measure instead of guessing: time the conversion, a small fresh download, and one training epoch, then scale up.

**How long doing this for every sign would take**
I measured on small samples, so these are extrapolations, not promises. The 20-file download came from one sign.

| Step | What I measured | At 250 signs × 120 clips (30,000 files) |
|---|---|---|
| Download | 20 files took about 19 s, around 1 s per file, 0.45 MB each | About 8 hours one file at a time, about 13 GB. Parallel downloads could cut that to a few hours. |
| Convert | 150 sequences in 8.3 s | About 30 minutes |
| Train | 10 epochs in 3.5 s on 100 clips | About 70 s per epoch on 20,000 training clips, so roughly 1–2 hours for 50–100 epochs |

- **Per sign:** about 2 minutes of download and conversion.
- **Total:** roughly 10 hours unattended, mostly downloading. It's a lot of waiting but little of your time.
- **Not included:** your review and decision gates, and picking which signs are worth including. Those cost more than the compute.
- **Uncertainty:** training with 250 classes isn't something I've tested, so that estimate is the shakiest.

**Five-sign run (approved)**
It's downloading and converting the 80/20/20 sample in the background. I'll tell you when it finishes. About 450 new files at roughly 1 second each is about 8 minutes. Then I'll check the old 150 sequences are inside the new set, train the same single GRU, and run the PopSign check.

The first attempt failed on a Kaggle read timeout at file 389 of 600, after about 23 minutes. I've started one retry, which reuses the files already downloaded. I'll check the data and train once it finishes, and if the retry fails too, I'll stop and report.

The download finished. I'm checking the result, including whether the earlier 150 sequences are inside the new set.

The retry finished in about 3 minutes, and all 600 sequences are in. I'm verifying the data before training.

The data checks out: the earlier 150 sequences are inside the new set, the participant splits are still disjoint, and every tensor is finite and `48 x 167`. Now the one approved GRU, with the same settings.

The model passed the 70% accuracy gate with more data, scoring 74% on test, but the result is less solid than it looks. I recorded it in [plan.md](plan.md) and pushed it as `f12630a`.

**Result (same GRU, same settings, 400 train / 100 validation / 100 test clips)**
- **Test top-1:** 74.0% (74 of 100 clips from four held-out signers). Validation was 70.0%. Going from 20 to 80 clips per sign took the model from 52% to 74%, so data quantity was the problem.
- **The test was run once.** It was evaluated after the best-validation checkpoint was restored, and I tuned nothing on it.
- **The estimate is imprecise.** With 100 clips from four signers, the 95% interval is roughly 65% to 82%, which includes values below 70%.
- **Per sign (test):** `after` 17/20, `hear` 17/20, `man` 18/20, `pen` 16/20, **`puppy` 6/20**. Most of the missed `puppy` clips were predicted as `after`.
- **PopSign check:** the frozen model scored 65.5% on the 55 PopSign clips, up from 34.5%. That is the real-source check, but only 15 of those clips are official test clips, where it scored 40%.

**Still not done**
- **Unknown rejection:** it isn't implemented. Idle and missing-hand inputs still get confident predictions, so the export gate fails and nothing is exported.
- **Phase 2:** I haven't declared it complete, because you haven't accepted this as the feasibility result.

**One correction to my earlier estimate**
The first import timed out at file 389 of 600 after 23 minutes. That is about 3.6 s per file, not the 1 s I measured on a small sample. The retry finished the rest in 3 minutes. The all-signs time estimate is therefore much less certain: serial downloading could take anywhere from about 8 to 30 hours.

**Decision for you**
1. **Unknown-input rejection:** build and test it on this model. It's required before any browser export.
2. **`puppy`:** find out why it fails. Some of that is probably the signer split.
3. **Widen the vocabulary:** go in stages, such as 10 signs, with the same gate each time.

I'd do 1 first, because without it nothing can go into the browser. Which do you want? Also tell me if you accept this as the Phase 2 feasibility result.

---

**Developer:**

yes, this is good.

**Agent:**

[Recorded the Developer's acceptance of the 74% result in plan.md, committed `b95a777`, and pushed.]

I recorded your acceptance of the 74% result as the Phase 2 feasibility result in [plan.md](plan.md), pushed as `b95a777`.

I read "yes, this is good" as accepting that result. You hadn't picked a next step, so I'm not assuming option 1. Unknown rejection involves real choices, so here is a short plan to check before I build it.

**Proposed approach: unknown-input rejection**
- **Rule:** reject a scan when the model's top probability is below a threshold. It's the simplest rule, and it works with this model as it is. The scores aren't calibrated probabilities, so the threshold has to be tuned on data.
- **Negatives to test with, all held-out participants:**
  - **Unsupported signs:** other signs from the Google corpus. This is the realistic "unknown sign" case.
  - **Idle and missing hands:** the synthetic inputs we already have.
  - **Real webcam idle and gestures:** these come later, in the browser phase.
- **Method:** fit the threshold on validation participants (real signs plus unsupported-sign negatives) and evaluate it once on the test participants.
- **Report:** at the chosen threshold, how many real signs get wrongly rejected, how many unknown signs wrongly get through, and the accuracy on accepted scans.
- **Your decision:** you set the acceptable trade-off after seeing the curve. For example, how many unknown signs must be rejected, and how many real signs you're willing to lose.

**One limit to expect:** with only five known signs, almost anything else counts as unknown, and the rule may need re-tuning once the vocabulary grows to 20–30.

Do you want me to go ahead with this, or change the approach?

---

**Developer:**

go ahead w this, does this mean phase 2 is done?

**Developer (sent mid-turn):**

also push & commit everything, save trascript

**Agent:**

[Sampled 20 unsupported signs with seed 20261109 from the 245 corpus signs outside the five-sign vocabulary, each with at least 10 validation and 10 test clips from the held-out participants. Read the transfer-evaluation script. Added the selection to plan.md. Saved this transcript. Committed and pushed.]

Phase 2 first: the feasibility result is accepted. The plan's three Phase 2 targets (tracking baseline, a feasible sign subset, and a first held-out-signer model result) now all exist. The official PopSign benchmark is still blocked, and Phase 3 stays gated on unknown rejection, so I'd call Phase 2 done in substance with those caveats. I haven't edited the map's wording, so tell me if you want it marked closed.

Now building unknown rejection. First step is choosing the unsupported signs fairly and checking availability.

The working tree is clean, so everything so far is already committed and pushed. I'm recording the unsupported signs I picked in `plan.md`, then saving the transcript.

---

## Notes on this transcript

- Tool calls and tool output are summarized in brackets, not reproduced.
- The final Agent message of this session (after the transcript was saved) is not included, because it is written after this file.
- Agent replies are reproduced from the session. Where the Agent wrote short lead-in sentences before tool calls and a longer summary after, they appear together under one Agent label. They were separate messages in the live session.
- Work done by other sessions between Nov 2 and Nov 9 is in the git history, not in this transcript.
