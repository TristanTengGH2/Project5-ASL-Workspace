# Session transcript: unknown handling, puppy diagnosis, fingerspelling letters

Saved 2026-11-09 (evening). Messages are labeled Developer and Agent. Tool calls and tool output are summarized in brackets, not reproduced.

This file continues the same conversation as `2026-11-09_2033_resume-and-recognition-gate.md` (which ends where the unsupported-sign negatives were chosen) and, before that, `2026-11-02_1547_pitch-and-tracking-spike.md`.

---

**Developer:**

go ahead

**Agent:**

[Wrote training/evaluate_unknown_rejection.py (a validation stage and a test stage that requires an explicit threshold). Started the download of the 20 unsupported-sign negatives. The first run failed because my shell passed the sign names as one argument; reran. The download then hit read timeouts twice (file 110 and file 143 of 420), so I stopped and reported.]

While that downloads, I'm writing the rejection script. It has two separate stages: a validation stage that only looks at validation signers, and a test stage that refuses to run without a threshold you've chosen.

That failure was my shell mistake, not Kaggle or the importer. zsh passed the 20 sign names as one argument. I'm rerunning with them split properly.

The first attempt failed on my shell quoting. The rerun is now downloading about 420 files, and I'll run the validation-only curve when it finishes. The test stage of the new script requires a threshold you've chosen, so I can't run it by accident.

The download hit a read timeout at file 110 of 420. That's the first real failure of this job, and the earlier retry for the 600-file set recovered from the same kind of error. I'm retrying once, and if it fails again I'll stop and report.

The negatives download timed out at file 110 of 420, on Google's storage host this time, not Kaggle. I started one retry, which reuses the 110 cached files. If it succeeds, I'll run the validation-only curve. If it fails a second time, I'll stop and report what happened and not keep retrying.

The negatives download failed twice, so I've stopped retrying. Each run ended in a read timeout, and nothing is wrong with the setup:

| Attempt | Stopped at | Failing host |
|---|---|---|
| 1 | file 110 of 420, after about 6 minutes | Google storage |
| 2 | file 143 of 420, after about 6.5 minutes | Kaggle |

- **Progress is kept.** About 143 files are cached on disk, so a later run resumes from there. Nothing was wasted, and no model or threshold work depended on the missing files.
- **The hang is on the remote side.** Each connection waited the full 120-second timeout and then died. The earlier 600-file download hit the same kind of timeout once, and its retry went through, so this looks like intermittent throttling. I haven't checked either host's status or limits.
- **The rejection script is written but not run.** It's `training/evaluate_unknown_rejection.py` and it's local only, not committed. I haven't run it on any model output, so there's no curve yet. Its test stage requires a threshold you've chosen.

**Options**
1. **Wait and retry later.** Run the same command in a while. The cached files mean it only needs the remaining ~277. This costs nothing but time.
2. **Reduce the negatives.** With the partial cache, I could shrink the plan, for example fewer signs, or 5 validation and 5 test clips per sign, so it needs fewer downloads. That's a change to the approved plan, and fewer negatives would make the curve noisier.
3. **Raise the request timeout or add a retry loop in the importer.** That's a code change and I'd rather not do it without your OK, since it could just hide a throttle.

I'd pick option 1, and then option 2 if it still stalls. Which do you want?

---

**Developer:**

lets carry on to that

**Agent:**

[Retried the import once; it completed. Verified: 200 validation and 200 test negatives from the same held-out participants as the five-sign sets, none from training participants, all tensors finite. Ran the validation stage only.]

I'll take that as option 1: retry the same command, with the cached files reused. I'm running it once now.

I'm retrying now, which resumes from the ~143 cached files. I'll tell you when it finishes. If it times out again, I'll stop and won't switch to the smaller-negatives option without asking you.

The download finished. I'm checking the negatives, then running the validation stage only.

The rejection test shows that a plain confidence threshold is a weak unknown detector for this model. I haven't touched the test participants. The script and the validation curve are committed and pushed (`d59544d`). A commit from another session, a transcript at 20:35, sits just before mine in the history, with no conflict.

**Validation results (100 real-sign clips, 200 unsupported-sign clips from the same held-out signers)**
- **Weak separation:** the AUROC is 0.640, where 0.5 is chance. The median top probability was 0.84 for real signs and 0.71 for unsupported signs. That's close enough that no threshold separates them cleanly.
- **The trade-off:**

| Threshold | Real signs kept | Unknown signs rejected |
|---|---|---|
| 0.50 | 90% | 16% |
| 0.70 | 68% | 49.5% |
| 0.80 | 61% | 62.5% |
| 0.90 | 42% | 82% |
| 0.95 | 34% | 89% |

- **What that means:** rejecting about 80% of unknown signs would also throw away 58% of real signs.
- **Idle and missing hands:** the synthetic inputs were all labeled `after`, with confidence 0.54, 0.74 and 0.97. A threshold wouldn't reliably reject those either.
- **Where unknown signs landed:** most often `after` (65 of 200), then `puppy` (47).
- **Data checks:** 200 validation and 200 test negatives from the same held-out signers, none from training signers, and all tensors valid. The download timed out twice and completed on the third run, which reused the cached files.

**Decision for you**
a. **Accept a threshold anyway** and state the trade-off plainly in the product.
b. **Test another score**, such as the gap between the top two predictions, on validation only. It's cheap and needs no new model.
c. **Train an explicit "unknown" class** from other signs' clips from the training signers. This changes the model, so it needs your approval.
d. **No hard rejection.** Show ranked candidates with a visible low-confidence warning, as lookup already does.

I'd try b first, since it costs minutes, and plan on d for the product either way. With b, if it doesn't help, c is the usual next step. Which do you want?

---

**Developer:**

what do you mean unknown

**Agent:**

"Unknown" means the person signed something the app wasn't trained on, or just moved their hands without signing. The app should say "I don't recognize this" in that case.

**Why it comes up**
- The model has five answers: `after`, `hear`, `man`, `pen`, `puppy`. It always picks one of them, even when the sign is something else.
- For example, if someone signs "car", the model still answers with one of the five, usually with some confidence. Of the 200 unsupported-sign clips I tested, it called 65 of them `after`.
- Idle hands or a tracking dropout get the same treatment. In my synthetic test, a scan with no hands was labeled `after`.

**Why it matters for this project**
- Your pitch promises an "unknown" state instead of forcing a match. Without it, the app would confidently show a wrong sign, which is the opposite of the honest tool you described.
- With only five signs, almost every real sign is unknown to the model. A larger vocabulary shrinks the problem but doesn't remove it.

**What I tested**
- I fed it 20 other signs the model had never seen, plus the real five signs.
- I asked whether the model's confidence score could separate the two groups. It can't, not cleanly: unknown signs often scored as high as real ones.

The options (a to d) in my last message are different ways of handling that: accept the limitation, try a better score, train the model to say "unknown", or show ranked guesses with a warning. Would a plain-language rewrite of those options help you choose?

---

**Developer:**

lets go ahead and try b first and see if anything improves.

**Agent:**

[Added margin and entropy scores to the validation stage (fixed in advance), ran all three on validation only. Recorded the result, committed `587200c`, pushed.]

I'm adding two alternative scores to the validation stage: the margin between the top two predictions, and normalized entropy. I'm fixing the list now so I can't pick a favorite after seeing results. Everything stays validation-only.

Option b did not help: all three scores separate real signs from unknown signs equally poorly. I'm recording that and committing.

Option b did not improve anything. I recorded it in [plan.md](plan.md) and pushed it as `587200c`.

**Result (validation signers only, where 0.5 is chance)**

| Score | How well it separates real from unknown signs |
|---|---|
| Top probability | 0.640 |
| Gap between top two predictions | 0.637 |
| Entropy | 0.649 |

- **Same practical trade-off:** to reject about 80% of unknown signs, each score keeps only 40–43% of real signs. At about 50% rejection, it keeps 66–68%.
- **The differences are noise.** With 100 real clips and 200 unknown clips, 0.637 versus 0.649 doesn't mean anything.
- **These are not three independent tests.** All three scores come from the same softmax output, so this is one approach, and it didn't work. The test signers were not evaluated and nothing was exported.
- **Code changes:** I added the margin and entropy scores to the evaluation script, and the training script now also saves each synthetic input's full probability list.

**What's left (your decision)**
- **c. Train an explicit "unknown" class:** the model learns what "not one of the five" looks like, using clips of other signs from the training signers. To measure it honestly, I'd test on unknown signs the model never saw in training. This changes the model, so it needs your approval, and it's the usual fix.
- **d. No hard rejection:** the app shows ranked candidates with a clear "low confidence" warning, as the lookup feature already does. This needs no new model and fits your honest-uncertainty goal.

I'd do both: plan on d for the product regardless, and try c to see whether an explicit unknown class helps. Do you want me to go ahead with c?

---

**Developer:**

so the reads have a high chance of failing is what you're saying?

**Agent:**

For signs it knows, it's right about three times in four. For signs it doesn't know, it can't reliably tell. Those are two different kinds of failure.

**When the person signs one of the five trained signs**
- It was right on 74 of 100 test clips from four signers it had never seen. Given that small sample, the true rate could be anywhere from roughly 65% to 82%.
- `puppy` was the weak one at 6 of 20 right. The others were 16–18 of 20.
- That is on landmark data from the Google corpus. On the 55 real PopSign clips, the same model got 65.5%. I haven't tested it with a live webcam, so real use could be lower.

**When the person signs something it doesn't know**
- It still picks one of the five, and often with high confidence. In my test it called a sign it had never seen one of the five every time.
- A threshold doesn't fix this. To catch about half of the unknown signs, it would also reject about a third of the real ones.

**What this means for the app**
- With only five signs, most things people try would be unknown to it. That makes lookup of a sign they don't know mostly useless at this stage.
- The failure to worry about is the confident wrong answer, not a refused read. That's the exact failure your honesty goals are meant to prevent.
- A wider vocabulary makes unknown signs rarer, but it doesn't remove the problem. That's why I recommended showing ranked candidates with a visible low-confidence warning (option d), whatever else we try.

Should I go ahead and try option c, an explicit "unknown" class?

---

**Developer:**

id rather it assume it doesn't know and when it comes to translating later it can give a possible answer in parenthesis based on context(is this a bad idea)?

**Agent:**

It's not a bad idea, and it's close to option d. The first half is sound. The second half needs limits.

**"Assume it doesn't know" (good)**
- It matches your honesty goal, and it fits what we measured, since the model's confidence can't tell a real sign from an unknown one.
- In the interface, that means the app never says "this is *pen*". It says something like "Not sure — closest matches: *pen*, *man*," with the scores shown. You'd show them as possibilities the user can check, not as results.
- The cost is that real, correct reads get shown as "not sure" too, which makes the app feel less capable. That's the honest trade-off. You decide how cautious it should be.

**A possible answer in parentheses based on context (fine if limited)**
- A parenthetical guess reads as a weaker claim, but people tend to trust anything shown next to a translation. It needs to be visibly different, for example "(possible: *pen* — a guess, not recognized)".
- The context guess must stay inside what the model produced: it can reorder the model's own candidates, but it must not add a word the model never proposed. That's the "no unsupported meaning" rule from your original brief and the scoped re-ranker we discussed.
- It is more than the current scope. Your plan puts continuous recognition outside the five weeks, and the PopSign data card lists sign-to-English translation as an unsuitable use. So context guesses would be a later, separately approved feature, tested against doing nothing. We'd check whether context actually improves the answer before trusting it.
- Deaf community critics have objected to overclaiming translation, so the wording matters.

**What I'd suggest**
1. Adopt "unknown by default, candidates shown as possibilities" now, in the spec and the interface.
2. Keep context guesses as a later stretch feature, labeled as guesses, drawn only from the model's candidates, and tested before it ships.

Do you want me to record that in `spec.md` as your design decision? And should I still try option c, the explicit "unknown" class, or leave it for now?

---

**Developer:**

yes, what can we do to make the statistical read higher for the translator though?

**Agent:**

[Recorded the design decision in spec.md (default result is "not sure"; candidates shown as possible matches; a later context guess must stay inside the model's candidates and be tested against showing none). Committed `a62d273`, pushed. Rechecked the PopSign certificate: still expired.]

I recorded your design decision in [spec.md](spec.md) and pushed it as `a62d273`.
- **Default result:** the app doesn't know. Candidates show only as labeled possible matches, with scores.
- **Recognized claim:** the app won't call a sign recognized until a tested rule supports it.
- **Context guesses:** they're a later feature, labeled as guesses and drawn only from the model's own candidates. They also appear in the decisions table.

**How to raise the accuracy**
I haven't tested most of these, so the order is judgment, and I can't promise gains.

1. **Train on the real source, which is the biggest likely lever.**
   - The model learned from older Google landmark data. The browser will use the newer MediaPipe tracker, and on the 55 PopSign clips the same model got 65.5% against 74% on Google's own test signers.
   - PopSign has 31 training signers (the Google split had 13), recorded on phones and run through our own tracker, so it should match the browser better. The official download is still blocked, because the certificate expired Nov 8 and I rechecked just now.
2. **Check how much of 74% is luck, which is cheap.**
   - I trained once with one seed. Training with five seeds on the same data would show the spread without tuning anything. If it swings by 5–8 points, small changes mean nothing.
3. **Find out why `puppy` fails.** It got 6 of 20 right and was mislabeled `after` 7 times. It might be a trimming problem, a sign that's too similar to another, or a single signer. Fixing one weak sign could lift the total by several points.
4. **Pick signs that look different from each other.** The spec already calls for that. Right now the five signs were picked for earlier tests, not for being easy to tell apart.
5. **More signers, not just more clips.** Going from 20 to 80 clips per sign helped a lot, but those extra clips come from the same 13 signers. More signers would help held-out accuracy more.
6. **Data augmentation and velocity features.** These are standard tricks with modest expected gains, and they change training, so they'd need your approval.
7. **Show several candidates.** A top-3 list is right more often than a single answer. With only five signs that isn't informative yet, but it will matter at 20–30 signs.

**What I'd do next:** check the certificate again later, run the five-seed spread now, and diagnose `puppy`. All three are measurement and need no new model. Should I do those two?

---

**Developer:**

puppy failing might be due to the longer sequence, can you send me what it tracked?

**Developer (sent mid-turn):**

it is because it is a composite of baby and dog possibly

**Agent:**

[Wrote training/render_tracked_sequences.py, rendered a detection timeline and middle-frame skeletons for the 20 held-out `puppy` clips, and counted detected hand-frames inside and outside the kept interval. An earlier version of my measure was flawed (it compared interval length with detection counts); I replaced it with a count of detected frames outside the kept interval. Recorded the diagnosis in plan.md, committed `2440b95`, pushed.]

I'll check that. Google's data is landmarks only, so I can show the tracked skeletons rather than video. First the numbers: sequence lengths for `puppy` against the other signs, and whether the clips it got wrong were the longer ones.

The numbers go against the longer-sequence idea. The clips `puppy` got wrong were shorter, not longer. Let me render what was tracked so you can see it.

That's a plausible mechanism, and I can test part of it. A compound sign has two movement phases, with a pause or a drop in tracking between them. My trimming keeps only the single densest tracked run, so it may cut a compound sign down to one half. That would fit the short intervals, so I'm checking whether the wrong clips have several separate runs and a trimmed interval covering only part of them.

That share measure was flawed: it compared interval length against detected frames, so it can't show truncation. I'm redoing it by counting the detected hand frames that fall outside the kept interval.

The renders show the clips `puppy` got wrong were shorter and sparser than the ones it got right, not longer. Your compound idea is plausible, but landmarks alone can't confirm it. I recorded it in [plan.md](plan.md) and pushed it as `2440b95`.

**The images** (landmark points only, written to the Git-ignored `training-artifacts/tracked-sequences/`):
- [puppy-test-timeline.png](training-artifacts/tracked-sequences/puppy-test-timeline.png) shows when a hand was found in each of the 20 held-out clips.
- [puppy-test-skeletons.png](training-artifacts/tracked-sequences/puppy-test-skeletons.png) shows the hand and arm skeleton at the middle of each clip's kept interval.

**What the tracker found**
- **Wrong clips are short and sparse.** The median kept interval was 6 frames for wrong clips and 17.5 for right ones. Median detected hand-frames were 5 for wrong clips and 22 for right ones. The longest clips include several right answers.
- **Only a right hand is ever found.** No left hand shows up in any of the 20 clips.
- **Hands sit low and near the left edge,** close to the shoulders. Six of the 14 wrong clips have no hand at all at the middle of the kept interval.
- **A few right answers came from almost nothing.** Two right clips have almost no tracked hand, so the model got them right with little evidence.
- **Trimming may be cutting content.** It discarded at least a quarter of the detected hand-frames in 9 of 14 wrong `puppy` clips and 4 of 4 wrong `pen` clips. The samples are small, so this is only suggestive.

**On the compound idea**
- Several long clips show separate bursts of detection, which would fit two phases. A compound's structure needs an ASL source, and I haven't verified that `puppy` is BABY plus DOG.
- If it is a compound with a low or two-handed part, the tracker may be missing much of it. That would fit what we see, but we haven't shown it.

**Next steps, your call**
1. Check with an ASL source, such as your instructor contact or another fluent signer, whether `puppy` is a compound or is signed low.
2. If it can't be tracked reliably, replace or drop it. The plan says to revise the vocabulary rather than hide poor performance.
3. Separately, test a trimming rule that keeps several dense runs for multi-phase signs, on validation signers only.

Which do you want first?

---

**Developer:**

show me the clip for baby
[Request interrupted by user]
show me the clip for puppy

**Agent:**

[Opened one local official PopSign `puppy` test clip in the default video player. Checked: no `baby` clip is local, and `baby` is not in the Google corpus (`dog` and `puppy` are).]

I opened a `puppy` clip in your default video player. It's an official PopSign test clip from signer 8037, `datasets/popsign-v1-0/phase2-five-sign/test/puppy/gtsignstudy4a.8037-puppy-2023_01_28_14_18_22.573-0.mp4`. It shows a real participant, so it stays local in the Git-ignored `datasets/` folder.

I have 10 more `puppy` clips from this download: 2 more in test, 5 in train and 3 in validation. They're under `datasets/popsign-v1-0/phase2-five-sign/*/puppy/`. I can open any of them.

**I can't show you `baby`.**
- It isn't in my local set, because we only downloaded the five signs. We can't fetch more from PopSign until its certificate is renewed.
- It isn't in the Google corpus either. That corpus has `dog` and `puppy`, but no `baby`.

What I can show instead is `dog`, as a skeleton timeline rather than video, because the Google data is landmarks only. It would let you compare the tracked pattern of `dog` against `puppy`, which is a partial test of your compound idea. It needs a small download from Kaggle, which has been timing out, so I'd keep it to a few clips. It also can't show `baby`, so it's only half the comparison. Do you want me to do that?

---

**Developer:**

there are 2 ways, they are finger spelling & doing the sign for baby and finger spelling dog, maybe we should get on the fingerspelling too soon.

**Agent:**

[Checked what the project documents say about fingerspelling and variants.]

Two forms means the `puppy` label may be mixing two different signs. I haven't verified that `puppy` has those two forms, so please treat it as your claim, but it fits what we saw.

**Why two forms would hurt the model**
- The model is trained to call both forms `puppy`. If a held-out signer uses the other form, the model sees something unlike its training examples and gets it wrong.
- PopSign's own data page sorts videos into "game" and "variant" categories, so the dataset also notes this problem.
- The skeletons are consistent with fingerspelling: only a right hand ever appears, near the shoulder. That's a pattern, not proof, because the landmarks can't tell a fingerspelled word from other signs.
- Your project's own rules already cover this case. [plan.md](plan.md) says to document known variants and exclude pairs the features can't responsibly separate, and [spec.md](spec.md) says highly ambiguous entries may be excluded. Dropping or replacing `puppy` fits both rules.

**Fingerspelling**
- It's a real feature, but a separate one from what we've been building. It would mean its own data, since the letters are mostly static handshapes (J and Z move), its own model, and a way to read letter sequences as words.
- It's outside the approved scope. [research.md](research.md) already lists it as one strategy for unfamiliar terms, and as a future catalog extension.
- It also fits the app's name and the unknown-term problem, because fingerspelling is how people write a word that has no sign.
- A search result earlier described the FSboard fingerspelling dataset as CC BY 4.0, but I haven't verified that, and it would need a license check before any use.
- Adding it now would cut into the five-week budget. I'd suggest planning it after the core loop works, as an expansion.

**What I'd do**
1. Replace or drop `puppy` and pick a sign with one standard form. Then redo the five-sign checkpoint, so the accuracy number isn't dragged down by a mixed label. It's a vocabulary change, so it needs your approval.
2. Add fingerspelling to `research.md` as a researched expansion candidate, and look into datasets and licenses, without changing the approved scope.

Do you want both, and should I choose the replacement sign using the earlier rule of distinct and trackable, or do you want to name one?

---

**Developer:**

what the llm should recognize is that it is baby before it is dog therefore it is puppy

**Agent:**

The order idea is sound: you'd recognize the parts in sequence, and BABY followed by DOG means PUPPY. I wouldn't use the LLM for it, though, and it needs things we don't have yet.

**It should be a fixed rule, not an LLM**
- A compound is a known pattern. A lookup table would hold "BABY then DOG → PUPPY". It's deterministic and checkable against a source, and it can't invent a meaning.
- An LLM could guess a compound that doesn't exist. Your original brief says never to generate meaning the recognition didn't support. Keep the LLM for the scoped re-ranker we discussed, if we add it at all.
- The table's entries should come from a source, such as a dictionary or ASL-LEX, and not from us. [research.md](research.md) already says established compounds can be catalog entries but arbitrary assembly can't be justified.

**What it would need**
- **Recognizing the parts:** BABY isn't in the Google corpus, and in the data we have I can't see it at all. DOG is there, but we haven't tested it.
- **Order and segmentation:** the app would need to find where one sign ends and the next begins. That's continuous recognition in miniature, and the spec puts it outside the five weeks.
- **The fingerspelled form:** your other version, BABY plus fingerspelled DOG, would also need letter recognition.

**A simpler route that fits the current design**
- Treat each form as its own sign with its own ID, both mapping to the English word "puppy". The spec already separates sign IDs from English glosses, so this fits.
- The model learns "fingerspelled puppy" and "BABY+DOG puppy" as separate classes, and the app shows the same gloss for either.
- That needs clips labeled by form. The Google labels don't say which form was used, so someone would have to sort them, for example by watching the PopSign clips.

**What I'd do**
1. Keep `puppy` out of the first vocabulary for now.
2. Record your compound-rule idea in `research.md` as a later feature, with fixed table entries, sourced pairs, and the separate-IDs approach noted as the first step.

Should I write that into `research.md`?

---

**Developer:**

we should do finger spelling, it covers a majority of our gaps

**Agent:**

[Searched for fingerspelling datasets and licenses: FSboard, the 2023 Kaggle fingerspelling competition data, and static letter datasets.]

Fingerspelling is your scope decision, and I'll plan it with you. First I'll research the data, since the license and the data decide what's feasible.

Fingerspelling is a good addition, but I'd check the claim that it covers a majority of our gaps. Here is what I found.

**What fingerspelling would and wouldn't cover**
- **It covers:** words with no sign in our vocabulary, such as names and unfamiliar terms. It also gives a way around variants like the BABY plus DOG form of `puppy`, since a word can be spelled out. Your Handshape brand fits it too.
- **It doesn't fix:** the weak "unknown" detection, the accuracy of the sign model, or compound signs like BABY.
- So it addresses one gap, vocabulary breadth, and I'd say so in the scope note.

**What I found about the data (licenses are not all verified)**
- **FSboard (Google, 2024):**
  - 147 Deaf signers and over 3 million characters, recorded on phones, with a MediaPipe Holistic baseline at 11.1% character error rate ([paper](https://arxiv.org/abs/2407.15806)).
  - Earlier searches called it CC BY 4.0, but this one couldn't confirm that, so check the project page.
  - It's phrase-level fingerspelling, not single letters, and the baseline model is large.
- **Kaggle ASL Fingerspelling (2023):** MediaPipe landmarks, about 170 GB compressed ([write-up](https://blog.tensorflow.org/2023/05/american-sign-language-fingerspelling-recognition.html)), and its license wasn't confirmed. Winning models are heavy.
- **Static letter image sets:**
  - The [Mendeley ASL Alphabet](https://data.mendeley.com/datasets/jdyksv2jhh/1) is listed as CC BY 4.0, and I didn't confirm whether it includes J and Z.
  - Sign Language MNIST is listed CC0 in a derivative's page, with 28×28 images and no J or Z.
  - These have few signers, and I found no diverse-signer landmark dataset. We'd extract landmarks ourselves with our own tracker, which at least matches the browser.

**Two scopes, very different in effort**
1. **Letter by letter.** The user holds one handshape, and the app names the letter.
   - It's mostly static handshapes (J and Z involve motion), so it's a much easier model than signs, and a small landmark classifier may do.
   - It needs enough different signers to measure held-out accuracy, which the image sets may not give us.
2. **Whole fingerspelled words.** This needs sequence recognition and segmentation of letters. It's far heavier and arguably continuous recognition, which is out of scope.

**What I'd suggest**
- Go for letter by letter, with a feasibility check first, as we did for signs. Extract landmarks from a static dataset, split by signer if signer IDs exist, and measure held-out accuracy before building anything in the browser.
- Check the licenses first: FSboard, Mendeley and MNIST.
- Record it in `research.md` as a scope change once you choose a scope. The approved pitch stays frozen.

Which do you want, letter by letter or whole words? Should I start with the license checks?

---

**Developer:**

letter by letter

**Agent:**

[Read the Mendeley dataset pages and the arXiv page. Read the FSboard Kaggle dataset metadata through the Kaggle API with the project's existing local token, without printing it: license CC BY 4.0, about 1.45 TB. Recorded the scope change and dataset findings in research.md, committed `3c61d9d`, pushed.]

I'll check the licenses and what each letter dataset actually contains: image size, signers, and whether J and Z are included.

I recorded letter-by-letter fingerspelling as a scope change in [research.md](research.md), with the dataset findings, and pushed it as `3c61d9d`. No letter dataset I've found so far fits our standards, so the data is the open problem.

**What I verified**
- **FSboard:** its [Kaggle metadata](https://www.kaggle.com/datasets/googleai/fsboard) lists CC BY 4.0 for the dataset itself, which the earlier searches couldn't settle. It has 147 consenting Deaf signers, about 1.45 TB of phone video, and fingerspelled phrases rather than isolated letters.
- **The two Mendeley letter sets, [SignAlphaSet](https://data.mendeley.com/datasets/8fmvr9m98w/3) and the [ASL Alphabet Dataset](https://data.mendeley.com/datasets/jdyksv2jhh/1):** both are CC BY 4.0 per their pages, with A–Z folders. Their pages don't state the number of signers, the image resolution, or how the letters were captured, and one doesn't say whether it includes J and Z.

**Why that's a problem**
- Without signer IDs, we can't test on signers the model never saw, which has been our standard throughout. A random split would likely overstate accuracy.
- FSboard has the signers and a verified license, but no isolated-letter labels. Turning it into letters would mean aligning each letter to video frames, which is real work.

**Options**
1. **Download and inspect the two Mendeley sets.** They're free to look at. We'd check image size, whether the hand is visible, J and Z coverage, and any signer clues in filenames or backgrounds, then decide. I can't promise held-out-signer testing, so any result would be labeled as not signer-separated.
2. **FSboard letter segments.** Use its phrase videos and find single letters through alignment. It's the best data but the heaviest to build.
3. **Collect a small letter set** from consenting volunteers, such as you and people you know, with signer IDs. It's the cleanest evaluation, but it needs consent and recruiting.

I'd start with option 1, since it's cheap and shows whether the Mendeley sets are usable at all. Do you want me to download and inspect them?

---

**Developer:**

wait we just need to learn the letters or otherwise how do we know its fingerspelling

**Agent:**

Yes, for letter by letter the model just needs the 26 letter handshapes. The app knows it's fingerspelling because the user tells it. It doesn't detect fingerspelling itself.

**How it would work**
- The app has a "Fingerspell" mode, separate from the "Sign" mode, and the user picks it. In that mode, every scan is read as a letter. The user holds one letter at a time.
- The model's whole job is then to tell the letters apart: A through Z.
- Most letters are static handshapes. J and Z involve movement, so they're the harder two.

**Why we don't try to detect it automatically**
- Telling "this is fingerspelling" from "this is a sign" is its own classification problem. Fingerspelling has some tells, like small hand movements near the shoulder and quick successive handshapes, but nothing reliable that I've tested. In real signing the two are mixed together continuously.
- That mixing is the continuous-recognition problem already outside the five weeks. An explicit mode avoids it entirely.

**What "learn the letters" still requires**
- Training data of people forming each letter, which is what the dataset search is about. The model has to learn them from examples, and those examples need enough different people for us to trust the accuracy.

If you meant the app teaching a user the letters, that's Learn mode, which is a stretch goal. A letter recognizer could serve as the practice check inside it. Which did you mean, and should I go ahead and inspect the two Mendeley sets?

---

**Developer:**

right?

**Agent:**

Yes, that's right. Fingerspell mode is chosen by the user, and the model only has to tell the letters apart. That makes it much simpler than recognizing signs.

I'm still waiting on one thing: should I download and inspect the two Mendeley letter sets? They're CC BY 4.0, and I'd check image size, J and Z coverage, and whether there's any way to tell the signers apart. It's a small download, and I won't train anything yet.

---

**Developer:**

do whatever you think is good, if it works for the signs that fingerspell at a good level then its good, toherwise we will have to use the other one right?

**Agent:**

[Listed the Mendeley files and sizes through the public API. Downloaded both archives into new Git-ignored directories under `datasets/fingerspelling/`, verified size and SHA-256 against the published values, listed contents without extracting, then extracted small samples to render contact sheets. Wrote training/measure_letter_detection.py and measured the browser hand model's detection rate on samples.]

Roughly yes, with one condition: "works at a good level" has to be measured on signers the model hasn't seen, or the number will flatter it. If these sets can't support that test, we move to FSboard or collecting our own letters. I'll start by checking what the files are and how big, before downloading.

The two letter sets total about 1.4 GB (a 445 MB static-image archive and a 935 MB one). I'm skipping the 1.25 GB video archive for now. The files go into the Git-ignored `datasets/` folder, each in its own new directory, and I'll verify their checksums. They contain scripts too, and I won't run those.

Both archives are downloading, about 1.4 GB in total. I'll verify their checksums when they finish. Nothing gets extracted or run until they check out. My note on your question: yes, that's the plan. If these sets measure well on unseen signers, we use them. If they don't, or if they can't support that test, we go to FSboard or collect our own letters.

Both archives match their published size and SHA-256. Now I'm listing what's inside each one without extracting.

The archives contain no unsafe paths. Here's what stands out:
- **SignAlphaSet:** exactly 1,000 JPGs per letter for all 26 letters, including J and Z, named `A_0.jpg` through `A_999.jpg`. No signer information anywhere in the names.
- **Cabana:** about 177,000 JPGs for 24 letters, with no J or Z (it also contains macOS junk files).

Next I'm extracting a small sample from each to look at the images and test whether our hand tracker can read them.

Both sample sheets are informative. Before judging them, I'm checking whether our hand tracker can read these images, since landmarks are what the model would learn from.

The two letter datasets can supply landmarks, but neither can prove we do well on new signers, so I haven't trained anything yet. I recorded the findings in [plan.md](plan.md) and [research.md](research.md) and pushed them as `062eabb`.

**What I found**
- **Downloads:** both archives matched their published size and checksum, and had no unsafe paths. The bundled scripts weren't run, and the data stays in the Git-ignored `datasets/` folder.
- **SignAlphaSet:**
  - 26,000 images, exactly 1,000 per letter A–Z, including J and Z, as static poses.
  - Close-up hands on a dark cloth.
  - Consecutive files are near duplicates, and a repeated wristband across letters suggests only a few signers.
- **Cabana:**
  - 24 letters, no J or Z.
  - About 88,000 Train images that come from only 1–5 videos per letter, so thousands of frames per video.
  - A separate 720-image Test set (30 per letter) with varied real-world backgrounds.
- **The hand tracker can read them.** I ran the browser's own Hand Landmarker model on samples. It found a hand in 99.3% of 1,040 SignAlphaSet images, 95.0% of Cabana Train, and 95.1% of Cabana Test. `O` was the weakest letter in all three.

**The limits, which matter for your "good level" condition**
- **No signer IDs in either set.** A split inside one dataset would put the same person in training and testing, and the accuracy would look better than real use.
- **Static images only.** J and Z need real motion, and Cabana doesn't include them.
- **Close-ups don't match the webcam view.** The app will see a waist-up person, so a domain gap is likely.

**A fairer check I propose**
- Train one small landmark classifier on one dataset and test it on the other dataset, and also on Cabana Test. Different datasets mean different people and settings.
- It's stricter than a random split, and it should show whether these sets work at all.
- If it fails, we move to FSboard or collecting our own letters.
- The plan is to label any single-dataset result as not signer-separated.

Do you want me to run that cross-dataset check?

---

**Developer:**

yes

**Agent:**

[Wrote training/extract_letter_landmarks.py and training/evaluate_letter_transfer.py. Ran the extraction in the background.]

Understood. First I'll write down the design, so the results can't shape it afterward:

- **Letters:** the 24 shared by both sets (A–Y without J). J and Z need motion, and Cabana has neither.
- **Features:** 21 hand landmarks per image from the browser's own model, wrist-relative and scaled by palm size, converted to pixel units so image shape doesn't distort proportions.
- **Model:** one small classifier with fixed settings and no early stopping. Neither set has clean validation signers to stop on, so stopping on a random split would leak.
- **Mirroring:** training includes flipped copies, because handedness labels may disagree between datasets. Test data is never flipped.
- **Experiments:** train on Cabana and test on SignAlphaSet, train on SignAlphaSet and test on Cabana Test, and Cabana to Cabana Test as a labeled, non-signer-separated reference.

While extraction runs, I'm writing the evaluation script with all of its settings fixed in advance.

The evaluation script is written. I'm waiting for the landmark extraction to finish before running it.

---

**Developer:**

okay are we good to say phase 2 is basically done

**Agent:**

Yes, you can say it, as long as you call it done for what Phase 2 set out to prove and list what's carried forward. I wouldn't call it done without those caveats.

**What Phase 2 targeted, and where it stands**
- **Real-camera tracking baseline:** done.
- **A feasible sign subset:** done. We used five signs, with the Google landmark data standing in for PopSign.
- **A first held-out-signer model result:** done. It scored 74% on the test signers, against the 70% target, and you accepted it.

**What's carried forward**
- **Unknown handling:** unsolved, and the confidence tests were weak. Your decision to default to "not sure" and show candidates as possibilities is a way to build around it, but the plan's export gate still says unknown rejection must pass. Whether the browser phase can start on your approach is a plan change for you to make, and I haven't made it.
- **Official PopSign data:** still blocked by the expired certificate, so everything so far is on the Google corpus.
- **`puppy`:** it has two signed forms and tracks poorly, so it's out of the first vocabulary.
- **The accuracy estimate is imprecise:** 100 clips from four signers.
- **Fingerspelling:** it's a new scope item. Its data feasibility isn't established yet. The cross-dataset check is still running, and I'll report when it finishes.

I can add a short Phase 2 summary to `plan.md` with those carry-forwards, and update the Phase 3 gate wording if you decide to proceed on candidates-as-possibilities. Do you want that? It would also give you a clean paragraph for today's milestone report.

---

**Developer:**

yes say that and say we are working for it to be better, all phase two is a known working model, it is wokring just not to its 100% it is a prototype right now.

**Developer (sent mid-turn):**

push & commit

**Agent:**

[Added a Phase 2 summary entry to plan.md and marked the Phase 2 row of the five-week map as complete as a working prototype. Committed `5d05801`, pushed. Then committed and pushed the two letter scripts as `f420245`.]

I added the Phase 2 summary to [plan.md](plan.md) and pushed everything (`5d05801` and `f420245`). The working tree is clean and matches the remote.

**What the Phase 2 summary says**
- **Status:** Phase 2 is complete as a working prototype. The five-week map's Phase 2 row now says the same.
- **What works:** hand tracking on your camera, and the model recognizing five signs at 74% on held-out signers (65.5% on the 55 real PopSign clips).
- **What it doesn't yet do:** it isn't perfect, the 74% estimate is imprecise, and it was trained on the Google bridge data. It has also not been tested live in a browser, and it can't yet tell an unsupported sign from a supported one.
- **What we're improving:** unknown handling, getting the official PopSign data, vocabulary growth to 20–30 signs, and fingerspelling.
- **Phase 3 gate:** I did not change it. Whether the browser phase can start on your "default to not sure" approach is still your decision.

**The last commit:** it adds the two fingerspelling scripts. The extractor has been running fine in the background on the letter data. The evaluation script has not been run, so no letter results exist. The extraction is still in progress, so I'll run the evaluation once it finishes and report the numbers either way.

---

**Developer:**

yes

**Agent:**

[Extraction finished: hand found in 98.6% of SignAlphaSet, 96.3% of Cabana Train and 94.9% of Cabana Test samples. Handedness labels disagreed across datasets. Ran the three planned experiments. Recorded the result in plan.md, committed `b051074`, pushed.]

All three extractions finished. Hand detection was 98.6% for SignAlphaSet, 96.3% for Cabana Train and 94.9% for Cabana Test. The handedness labels disagree across the datasets: Cabana Train is 81% "Left", while SignAlphaSet and Cabana Test are mostly "Right". That matches why I trained on mirrored copies. Now I'm running the three planned experiments.

Letters can be recognized from landmarks, but not yet at a good level on new people. I recorded the result in [plan.md](plan.md) and pushed it as `b051074`.

**Results (24 letters, chance is 4.2%)**

| Train on | Test on | Top-1 | Top-3 |
|---|---|---|---|
| Cabana | SignAlphaSet (different people and setting) | **68.3%** | 84.9% |
| SignAlphaSet | Cabana Test (different people and setting) | **49.3%** | 73.8% |
| Cabana | Cabana Test (signers may overlap, not signer-separated) | 86.7% | 95.0% |

- **The gap is the lesson.** Accuracy drops from 86.7% to 49–68% when the test people and settings change. The cause isn't isolated, because signers are unknown.
- **Some letters fail completely.** In the cross-dataset runs `G`, `M` and `X` scored 0% in one direction, and `G`, `M`, `O` and `X` in the other. The common mistakes were `M` as `S`, `G` as `C`, and the fist-like letters (`A`, `S`, `T`, `N`) mixed together.
- **Why, untested:** the fist-like letters differ mainly in thumb position, and `G`, `Q` and `X` depend on hand orientation, which differs between the datasets.
- **Setup:** the classifier is a small network on the same hand landmarks the browser uses. I fixed every setting before running anything, and each experiment trains on mirrored copies of the training images only.

**Against your condition:** it doesn't work at a good level yet, though it isn't hopeless. Top-3 is 74–85%, which suits a "closest letters" display. It's one fixed configuration, so any changes I tune against these same test sets would make later numbers exploratory.

**Options**
- **a. One declared improvement attempt on these sets.** Rotation normalization and training on both datasets, tested by leaving one dataset out. It's cheap, probably under an hour.
- **b. Move to FSboard letter segments.** It's the most signer-diverse option, but needs alignment work on a 1.45 TB dataset.
- **c. Collect a small signer-labeled letter set** from consenting volunteers.

I'd try (a) first because it's quick. If it can't reach a good level, we move to (b) or (c), as you said. Should I run (a)?

---

**Developer:**

yes

**Developer (sent mid-turn):**

for right now lets also save transcript & commit & push

**Agent:**

[Added `rotaug` and `invariant` variants to the evaluation script and ran all three variants on the same three experiments. Recorded the results in plan.md. Saved this transcript.]

One correction to my own proposal before I run it: "train on both sets and leave one dataset out" doesn't work with only two datasets, because training on both leaves nothing unseen. So I'm not doing that. I'm testing two clearly declared feature changes on the same three experiments instead:
- **rotation:** the same model with random in-plane rotation added to the training copies, since hand orientation differs between the datasets;
- **invariant:** pairwise landmark distances, which don't depend on rotation or mirroring, plus one orientation direction so orientation-dependent letters like `G` and `Q` can still be told apart.

I'll report both, since running two variants on the same test sets means picking between them adds some selection bias.

Results are recorded in the plan. Now I'm saving the transcript for this stretch of the session.

[Results of the three variants, as recorded in plan.md: top-1 train Cabana to test SignAlphaSet 68.3% (baseline), 68.9% (rotation), 71.8% (invariant); train SignAlphaSet to test Cabana Test 49.3%, 51.8%, 62.2%; train Cabana to Cabana Test (not signer-separated) 86.7%, 89.0%, 92.8%.]

---

## Notes on this transcript

- Tool calls and tool output are summarized in brackets, not reproduced.
- The final Agent message of this session (after the transcript was saved) is not included, because it is written after this file.
- Agent replies are reproduced from the session. Where the Agent wrote short lead-in sentences before tool calls and a longer summary after, they appear together under one Agent label. They were separate messages in the live session.
- Work done by other sessions is in the git history, not in this transcript.
