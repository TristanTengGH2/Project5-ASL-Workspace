# Session transcript: pitch, sources, tracking spike

Saved 2026-11-02 15:47. Messages are labeled Developer and Agent. Tool calls and tool output are summarized in brackets, not reproduced. Notes about what was omitted are at the end.

---

**Developer:**

[Attached file: ASL_Project_Chat_Transcript.txt, a transcript of an earlier brainstorming chat (Nov 2, 2026) covering the ASL web app concept, a VS Code project prompt, and a webcam motion tracking addendum. Not reproduced here; see the note at the end.]

**Agent:**

[Inspected the repository: it is the blank Project 5 template. Node, npm, bun and Homebrew were not installed; Python 3.9.6 is present.]

I inspected the repo. I haven't written any code yet, because the project's rules (AGENTS.md) have me check the spec and plan with you first.

**What's here**
- The repo is the blank Project 5 template. It has no source code, and `pitch.md`, `spec.md`, `plan.md` and `research.md` are all unfilled.
- This machine has no Node, npm, bun or Homebrew. The brief's React + TypeScript + Vite default needs Node installed first. Python 3 is available.
- Your brief puts Phase 2 (Nov 2–9) at "prove the core". Your transcript's Week 1–2 plan (webcam and landmark tracking, then a real prediction) matches that phase. Your pitch is being reviewed today, and `pitch.md` is still empty, so this transcript would need to be turned into the pitch.

**Largest risk: sign recognition, not the interface**
- The transcript's Translate mode needs a real isolated-sign model that is licensed for reuse, trained on diverse signers, and runs in the browser on webcam landmarks.
- Hand tracking (for example MediaPipe) is mature. A reusable recognition model is much less certain.
- I haven't verified any candidate model or dataset yet. I'd check that first, before building any interface.

**Proposed first checkpoint (Phase 2 vertical slice)**
1. Install Node, then scaffold Vite + React + TypeScript.
2. Start and stop the camera, and draw a two-hand landmark overlay.
3. Run a feasibility spike on one candidate recognition model, recording its license and vocabulary, then report latency and any blockers.
4. Only then add attempt recording, saving, and annotation.

**Questions that change the plan**
1. **Scope:** The transcript covers three modes (Translate, Learn, Review) plus tracking, and your brief asks for roughly 2× the last projects. Should the five weeks aim at all three modes, or at one core loop first, with the other modes as stretch goals?
2. **Pitch:** Should I help draft `pitch.md` from this transcript now, or have you already written the pitch somewhere else?
3. **Install:** Can I install Node, via the official installer or nvm? This needs your go-ahead.
4. **Spike order:** Should I start by researching candidate recognition models and datasets (licenses, vocabulary), or by building the camera and landmark overlay first?

Once you answer, I'll write a short spec in `spec.md` for you to review before I build anything.

---

**Developer:**

at least one 3 modes & I want to include the webcam tracking(It seems interesting & my main focus on this project), I have the previous projects linked to my github, tristantengGH2. Including all the projects except for those about CopyPanda. You should help draft pitch. You can install node and you can start researching candidate LLMs & ideally look for open source & free use. We can worry about camera & landmark overlay later.

**Agent:**

[Listed the developer's public GitHub repos. Searched for open-source isolated sign recognition models, the Kaggle ISLR dataset, and WLASL / ASL Citizen licensing. Downloaded Node v26.13.0 LTS for darwin-arm64, verified its SHA-256 checksum, and extracted it to ~/.local. The first npm run failed only because Node was not on PATH; with PATH set, node 26.13.0 and npm 11.20.0 worked.]

**Developer (sent mid-turn):**

You can also link to GH to start a new repo

**Agent:**

[Checked `gh` login (TristanTengGH2). Created the private repo TristanTengGH2/Project5-ASL-Workspace, ran `git init -b main`, and added the remote. Nothing was committed.]

Node 26.13.0 and npm 11.20.0 are installed, and `gh` is logged in as TristanTengGH2. Next I'll create the new GitHub repo and link it to this folder. I won't commit or push anything yet.

I created a private repo, [Project5-ASL-Workspace](https://github.com/TristanTengGH2/Project5-ASL-Workspace), and linked it to this folder. Nothing is committed or pushed yet. I picked the name and made it private, and both are easy to change.

**Setup**
- Node 26.13.0 (the current LTS release) and npm 11.20.0 are installed in `~/.local`. I checked the download against its published checksum. It isn't on your shell PATH yet, so tell me if you want that added.
- Your earlier repos use plain HTML, CSS and JS with no build step. The brief's React + Vite default would be a new stack, so the choice is yours. Keeping your usual no-build setup is also viable.
- Your public repos besides CopyPanda are Ai-Explorations-Unit-1, Project3-WeatherInClass and Project-4-Holloweenie. I've only read the Holloweenie README (static site, GitHub Pages, keyboard and reduced-motion support). That accessibility habit fits this project.

**Recognition model research**
(These are recognition models, not LLMs.)

1. **I found no ready-to-use pretrained ASL landmark model with a clear license.** The open-source repos I found, such as [WLASL100 biGRU](https://github.com/Bakkarranna/sign-language-recognition) and [this toolkit](https://github.com/veerendrakosuri/sign-language-recognition), are training pipelines. At least one of them warns that no commercial use is implied.
2. **The datasets are research-only.** WLASL uses the [C-UDA](https://github.com/dxli94/WLASL), described as academic and computational use only. ASL Citizen uses [Microsoft's non-commercial research terms](https://www.microsoft.com/en-us/research/project/asl-citizen/dataset-license/). A free class project is probably fine under both, but I haven't confirmed that against your course's rules.
3. **Hand tracking is the safe part.** MediaPipe is [Apache 2.0](https://github.com/google/mediapipe/blob/master/LICENSE). That covers the landmarks, not any sign model trained on them.
4. **I couldn't confirm the license of the Kaggle Google ISLR (asl-signs) dataset.** It has 250 signs and about 94k sequences, with landmarks already extracted by MediaPipe Holistic. I'd read its Data and Rules page directly before using it.

**Most likely path:** train a small model of our own, a biGRU or transformer, on landmark sequences for roughly 20–50 signs. It would run in the browser through TensorFlow.js or ONNX Runtime Web. Training and testing it would be the riskiest part of the five weeks.

**Choices for you**
1. **Model:** train our own on WLASL or Kaggle landmarks, or record our own small vocabulary (full control and clean licensing, but only one or a few signers)?
2. **Modes:** I read "at least one 3 modes" as at least one of the three, with live webcam tracking as the core. Which mode should be first: Translate, or Learn with a tracking overlay?
3. **Pitch:** do you want me to draft the Ideation and Pitch sections of `pitch.md` now from the transcript? You'd then rewrite them in your own words.

---

**Developer:**

Let's start with translate and then push for a learn mode if we have tiem. Let's start doing the pitch, instead of using my signs lets work with a documented database of handsigns or a video database with signs that are verifiied. I am scared to get it wrong. We can site them as the basis aswell

**Agent:**

[Searched for ASL-LEX, ASL Citizen, Kaggle ISLR licensing, and WLASL label problems. Read the developer's previous project READMEs. Wrote draft Ideation and Pitch sections into pitch.md (about 1,200 words).]

I drafted the Ideation and Pitch sections in [pitch.md](pitch.md). It's a draft for you to rewrite, and open items are bracketed. I haven't committed anything.

**Data sources, with what I could and couldn't verify**
- **ASL Citizen (primary):** 83,399 videos of 2,731 signs from 52 signers, recorded with consent. Its vocabulary comes from ASL-LEX. The [paper](https://arxiv.org/abs/2304.05934) reports a baseline of 63% accuracy on signers not in training, across the full vocabulary. This is the closest match to "verified". Its license is [non-commercial research](https://www.microsoft.com/en-us/research/project/asl-citizen/dataset-license/), and I haven't confirmed whether we can publish trained weights.
- **ASL-LEX 2.0:** a peer-reviewed lexical database with 2,723 signs and ratings from Deaf signers ([Sehyr et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7977685)). I couldn't confirm the dataset license, so we need to check its OSF page.
- **Kaggle Google ISLR:** a fallback with 250 signs and landmarks already extracted. I couldn't confirm its license or signer details.
- **WLASL (avoided):** its labels came from video titles, and [Boston University researchers documented inconsistent glosses](https://open.bu.edu/server/api/core/bitstreams/3bf02cc0-5fce-4afa-b8e0-8dbd28822e92/content). I couldn't find a source on whether Deaf signers reviewed it.

**What this means for your worry about getting it wrong**
- Using a verified dataset covers label quality. It doesn't cover tracking errors, webcam conditions, or generalization.
- The full-vocabulary baseline is 63%. A 20–30 sign subset should do better, but we have to measure that, not assume it.
- The pitch frames the app as isolated-sign recognition with an "unknown" state, not translation. The draft also says it isn't a replacement for interpreters.
- I'd still recommend having an ASL instructor or fluent signer review the chosen vocabulary.

**Needs your decision or edits**
1. **Length:** the pitch section is about 1,200 words, over the ~1,000 target, mostly because of the source table. Should I trim it, or keep it?
2. **Branding:** I listed four title options (SignBridge, Handshape, Signpost, Lumen) as placeholders. Pick one, or give me a direction.
3. **Tech stack:** the draft assumes Vite + TypeScript, MediaPipe, and Python for training. Confirm or change it.
4. **License check:** should I read the ASL Citizen and ASL-LEX license texts next?

---

**Developer:**

for the choice, is there competition for a plan like this on the market, am I directly copying anything?

**Agent:**

[Searched for existing webcam ASL learning tools, PopSign, and Deaf community responses to sign language technology.]

Yes, there is competition. From what I found, you wouldn't be copying any of it. I haven't compared their code or interfaces in detail, though. Most of the descriptions below come from the vendors themselves, so I haven't verified them.

**Existing products in the same space**
- **Webcam ASL learning tools:**
  - [Signpost](https://signpost.cv/) is a browser tool that says it gives webcam feedback and keeps footage on your device.
  - [ASL Pal](https://aslpalpilotprogram.com/) is a university pilot that scores signs against handshape and movement criteria.
  - [AISA School](https://www.aisa.solutions/) and the [CLERC demo](https://clerc.io/demo) give camera practice feedback.
  - [Lingvano](https://aitoolsbakery.com/blog/best-ai-sign-language-apps/) has Deaf teachers and checks fingerspelling.
  - An NVIDIA browser game covers 100 basic signs.
  - Open-source fingerspelling projects such as [SignLearn-ASL](https://github.com/Rohini-durga/SignLearn-ASL) also exist.
- **Research-backed:** [PopSign](https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/) is a Georgia Tech and RIT/NTID game for hearing parents of Deaf children. Its recognition version, PopSignAI, covers 250 signs from 47 Deaf signers and reports about 82–84% accuracy.
- **Not found:** my searches turned up nothing on SLAIT, Learn Signs or Ace ASL, so I can't say whether they overlap.

**What this means for the pitch**
1. **Learning with webcam feedback already exists.** Recognizing isolated signs for hearing learners is a crowded space. Your Learn mode in particular would not be new.
2. **I can't support the claim that this "hasn't been done right, or at least together."** A combined translate, learn and annotate tool wasn't in my results, but I didn't search for that specifically. I'd drop the claim from the pitch unless we verify it.
3. **Your real differentiators are honesty and openness, not novelty.** These would be the "unknown" and "tracking lost" states, evaluation on held-out signers, and a documented dataset basis. A review and annotation workspace would also set you apart, but that's a stretch goal. I haven't confirmed that others lack it.
4. **Deaf community skepticism is documented.** A [2026 Northeastern survey](https://news.northeastern.edu/2026/03/19/sign-language-technology-skepticism/) found it, and there was a [2016 open letter on the SignAloud gloves](https://faculty.washington.edu/ebender/papers/SignAloudOpenLetter.pdf). Complaints included overclaiming translation and shifting the burden onto Deaf people. Your plan already avoids the translation claim, and it targets hearing learners. I'd keep that framing explicit.

**A data finding that changes the sources table.** PopSign v1.0 is licensed [CC BY 4.0](https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/). It has 250 signs from 47 Deaf signers. That is far more permissive than ASL Citizen's non-commercial research terms. It could be the better primary dataset, and it would ease the question of publishing trained weights. I haven't confirmed how it relates to the Kaggle asl-signs data.

**Two decisions for you**
- Should I update the Choice, Why and Starting point sections to say honestly that this space is crowded and your angle is the honest-evaluation and openly-sourced approach?
- Should I make PopSign v1.0 the primary dataset, with ASL Citizen as a second source, after I read the PopSign license page in full?

---

**Developer:**

Am I at least filling the niche of not needing anything more than a webcam to learn ASL, i think there are methods in which they use motion tracking via gloves but that is equipment oen would have to purchase.

**Agent:**

No. Webcam-only is already how most of these tools work, so it isn't a gap.

- **Tools I found that need only a camera:** Signpost, ASL Pal, AISA School, the CLERC demo, NVIDIA's Signs game, and PopSign on a phone all do this, going by the vendors' own descriptions. The Google Play ASL app runs on-device. Several of these are free.
- **Gloves are a different category.** The glove projects I found were research prototypes, like SignAloud and the UCLA glove, that aimed at translation. I didn't find a mainstream glove-based learning product. Deaf critics also pushed back on those gloves, partly because they shift the burden onto Deaf people. Webcam-only is simply the default, so you wouldn't be filling a niche against gloves.

**What you could still claim, in the pitch and not just the branding**
These are weaker than a market gap, and I haven't verified that the others lack them.
- **Honest uncertainty:** visible "unknown" and "tracking lost" states, and results shown with their limits.
- **Documented, openly licensed data:** a stated dataset basis, with held-out-signer evaluation reported.
- **Local-only processing, and open source** if you choose to publish the code. Signpost already says its footage stays on-device, so privacy alone isn't unique.
- **Review and annotation of saved attempts:** this is the stretch goal, and it's the only part I didn't see in the tools above. I only checked a handful of products, so I can't say it's absent elsewhere.

**Where that leaves the project:** the case for it is the course goals and your own interest, not a market gap. Webcam tracking is your main focus, you'd be building and measuring the recognition model yourself, and the honesty design is a deliberate choice. That's a legitimate pitch, but it should say so plainly.

Do you want me to rewrite the Choice and Why sections that way, with no market-gap claim? I'd also drop the line from your original brief that this "hasn't been done right."

---

**Developer:**

Is there a niche to be filled and what features can I include to fill that niche?

**Agent:**

[Searched for learner-app feedback gaps and for ASL reverse-dictionary research.]

There may be a niche, but not a large one, and I can't prove it's empty. I'd frame it as **sign lookup**: a learner sees a sign they don't know, or can't name one they half-remember, and wants to find it. Recommending that is my judgment. It's your decision.

**Why lookup looks like a real gap**
- Researchers describe looking up an unknown ASL sign as hard. Dictionaries ask for handshape and location selections, or for a webcam performance. A [2025 paper](https://arxiv.org/html/2504.05857v1) notes that learners often can't isolate or replicate the sign themselves. (Details are from search snippets, so check the paper.)
- Video lookup tools exist as research prototypes, including that 2025 AI-driven dictionary. I didn't find a polished consumer product, but I only ran two searches.
- ASL Citizen's authors name dictionary retrieval as the dataset's main use. Its baseline gets 91% recall-at-10 against 63% top-1 ([paper](https://arxiv.org/abs/2304.05934)).

**Why it fits your constraints**
- Showing a ranked list of candidates with reference videos is more honest than forcing one answer. It also tolerates a modest model, and it matches your "unknown" and uncertainty design.
- Webcam tracking stays the core of the project, and Translate mode is what gets built.

**Features that would serve it** (my suggestions, in rough build order)
1. **Top-5 candidate results.** Each result has a reference video and an English label, and the user can reject any of them.
2. **Handshape and location filters.** These could use ASL-LEX phonological data, as in the hybrid search that [performed better in a 20-learner study](https://arxiv.org/html/2504.05857v1). Tracking can pre-fill them.
3. **Video quality feedback.** "Hands out of frame", "too dark" and similar, so a tracking problem isn't read as a signing error.
4. **Local-only processing** and no account.
5. **Side-by-side compare** of the user's attempt with the reference. This is the bridge to Learn mode.
6. **Upload a clip and mark a span**, which later becomes the annotation stretch.
7. **A personal word list** of saved signs.

**What to avoid claiming**
- Feedback on facial grammar and nonmanual markers is a real, documented gap in learning apps. Automated detection is a hard research problem ([example](https://arxiv.org/pdf/2005.00253)), so it's out of scope for five weeks.
- Reference-video reuse is an open question. Redistribution terms for ASL Citizen and ASL-LEX videos aren't confirmed. Linking to the source may be safer than hosting copies.

Do you want me to reframe the pitch around lookup, with Learn as the stretch goal and no market-gap claim? Or should I keep the pitch as a general recognizer and note lookup as one use?

---

**Developer:**

We can utilize this as a way to make a webapp that pushes it out for a public use case, that it is free & you dont need specialized equiptment. I also like the sign look up. I think we can use LLMs to have it function in context, lets say someone doesn't know what it is but they understand the signs around it and have a general idea of what the sign looked like. It can translate it for them.

**Agent:**

That works as a direction: a free, camera-only lookup tool that runs in the browser. Here is how I'd make the LLM part safe, and the cost and privacy trade-offs.

**The LLM idea, in a safe form**
- **The user gives context:** typed text of the signs or sentence around the unknown sign, plus what they remember (handshape, where, how it moved).
- **Tracking and the sign model produce candidates:** from the webcam attempt, the app gets a ranked top-K list drawn only from the supported vocabulary.
- **The LLM only re-ranks that list:** it picks which candidates fit the context best. It cannot add signs, so it can't invent a meaning the model never produced. That matches the "no unsupported meaning" rule in your original brief.
- **The interface shows both signals:** the model's candidate score and the context fit are separate and labeled.

**Limits to put in the pitch**
- **The LLM can't see the signs.** It only knows what the user types, so "the signs around it" means the user supplies glosses or a sentence. It also isn't a translator of natural ASL grammar.
- **Re-ranking can't fix a wrong candidate list.** If the right sign isn't in the top-K, the LLM can't recover it.
- **Structured filters might do most of the work.** Handshape and location filters from ASL-LEX data are deterministic, free and testable. We should compare the LLM against filters alone, because the LLM may add little for its cost.

**Where the LLM runs: your decision**

| Option | Free | Privacy | Cost and risk |
|---|---|---|---|
| In-browser small model (e.g. WebLLM or Transformers.js) | Yes | Fully local | Large first download, slow on weak devices, weaker re-ranking |
| Hosted API through a small proxy | Free tiers have limits and change | Typed text goes to a third party and must be disclosed | Needs a backend to keep the API key off the client; abuse and rate limits |
| No LLM at launch, structured filters only | Yes | Fully local | Less novel; LLM added as a stretch |

I haven't checked current free-tier terms for any API, so that needs checking before you choose. A static site on GitHub Pages, as with your earlier projects, only supports the first and third options without extra infrastructure.

**Scope check for five weeks:** "free, public, no equipment" is the goal. The riskiest part is still recognition accuracy, and the vocabulary has to stay small enough to measure honestly (about 20–30 signs for the MVP, or PopSign's 250 if the data and compute work out).

Three questions:
1. **LLM placement:** in-browser, hosted with a proxy, or filters first with the LLM as a stretch?
2. **Priority:** should lookup be the main Translate flow, with Learn still a stretch?
3. **Pitch:** want me to rewrite the Concept, Choice and Why sections around "free camera-only sign lookup", drop the market-gap claim, and add the LLM as a scoped, optional re-ranker?

---

**Developer:**

it doesn't have the be exclusively a sign look up, but that can be one of the features. I want this to still generally be a database where one can look up, learn, and translate. What do you mean scoped, optional reranker. Lets prioritize the translate & unknown sign lookup as the main fucntions with the learn as a secondary priority.

**Agent:**

[Rewrote the Choice, Branding and Pitch sections of pitch.md (about 750 words).]

**"Scoped, optional re-ranker," in plain terms**
- **Scoped:** the LLM does one narrow job. It gets the sign model's top candidates, such as five possible signs, plus the context the user typed. It returns a better ordering of those same five. It can't add a sixth sign or write a free-form translation.
- **Optional:** the app works without it, using only the sign model and the handshape and location filters. Users can switch it on or off, and it can wait until after launch. That way a missing or rate-limited LLM never breaks lookup.

I've updated [pitch.md](pitch.md) to match your priorities. Translate and unknown-sign lookup are primary, Learn is secondary, and the app is a free, camera-only lookup, learn and translate tool.

I rewrote the Choice, Branding and Pitch sections of [pitch.md](pitch.md). The Pitch section is about 750 words, under the 1,000 target. It's still a draft for you to review, and nothing is committed.

**What changed**
- **Concept:** a free, camera-only app built around a verified sign database. It covers recognizing a supported sign, looking up an unknown sign, and learning a sign.
- **Priorities:** Translate and unknown-sign lookup come first, and Learn is a stretch goal. The LLM re-ranker, annotation, and uploaded-video recognition are lower stretch goals.
- **Competition:** the market-gap claim is gone. The Choice section now says webcam-only tools exist and links to them.
- **Data:** PopSign v1.0 is now listed as the leading candidate dataset. The sources table also keeps ASL Citizen and ASL-LEX. I'm relying on a search snippet for PopSign's CC BY 4.0 license, so I still need to read its page and license text.
- **MVP:** it now returns a top-5 ranked prediction, which suits lookup.

**Still open (bracketed in the file)**
- **Branding:** the title is a placeholder. Signpost is also an existing product's name.
- **Tech stack:** the stack is a proposal for you to confirm.
- **LLM location:** where the LLM runs is undecided.

Two next steps I'd suggest. First, I read the PopSign and ASL Citizen license texts and check whether landmarks or raw videos are what's distributed. That decides what we can train on, publish and show. Second, I scaffold the Vite and TypeScript project and start the webcam tracking spike. Which should come first?

---

**Developer:**

I like handshape alot, anyways for the choice, does the lookup not kind of fill a market gap?

**Agent:**

[Searched for handshape-based and camera-based ASL reverse-dictionary tools.]

Partly, and I'd call it a possible gap, not a proven one. Here is what the evidence supports.

**Already exists: feature-based lookup**
- You pick handshape, location and movement from menus, and the tool lists matching signs. Tools I found:
  - [Handspeak's reverse dictionary](https://www.handspeak.com/word/asl-eng/)
  - [ASL Interactive](https://aslinteractive.com/reverse-dictionary/)
  - [WhatsThatSign](https://www.whatsthatsign.com/)
  - [Rochester's LSF-ASL dictionary](https://projects.lib.rochester.edu/lsf-asl/dictionary/)
  - The Dawnsign dictionary
- A [2025 study](https://arxiv.org/html/2504.05857v1) reports that learners rarely use these, and preferred video-based lookup. The sample was small.

**Not found as a consumer product: camera-based lookup**
- The camera-based work I found is research:
  - A [2021 reverse dictionary prototype](https://link.springer.com/chapter/10.1007/978-3-030-70650-0_14) where you show a handshape to a phone camera.
  - Boston University's webcam lookup, tied to its annotation software ([2024 paper](https://arxiv.org/abs/2407.13571v1)).
- I found no public, free, camera-based consumer tool. That is the possible gap.

**Why I'm hedging:** I ran four searches in total, and I didn't search app stores. Newer products like AnySign and Sign Language AI turned up in results, and I couldn't verify what they do. Before the pitch says "gap", we should check them and the app stores.

**On handshape:** it fits well. It's also the most tractable thing to recognize from hand tracking, because it's a static pose and not a moving sign. A "show me the handshape" lookup would be a useful first version, and a hybrid of camera plus handshape filters is what the learner study favored. I haven't verified that handshape classifiers from MediaPipe landmarks are accurate enough, so that needs a spike.

**Suggested Choice wording:** "Feature-based ASL reverse dictionaries exist. Camera-based lookup appeared only in research prototypes in my search. This project explores a free, camera-only version, with handshape as a key input."

Do you want me to put that wording into the Choice section? Also, should handshape lookup be the first thing we prototype, ahead of full-sign recognition?

---

**Developer:**

handshape is just the marketing name because generally asl is based in handshape. I think we can implement motion tracking in a sense because some signs do include bigger movements. I like our idea

**Agent:**

Understood. I'll set "Handshape" as the working title and write the movement tracking into the pitch. One note for the copy: handshape is one of five ASL parameters (handshape, orientation, location, movement, nonmanual features). The app's marketing shouldn't say ASL "is based in" handshape. Calling it a key part of a sign is accurate.

[Edited pitch.md: working title, movement tracking, competition wording.]

I updated [pitch.md](pitch.md) with the edits below. Nothing is committed.

- **Title:** the working title is now _Handshape_, in both the Branding and Title sections. I added a note not to claim ASL "is based in" handshape.
- **Movement:** the Concept now says tracking follows hand shape, location and movement over time. The technical goals now call for timestamped landmark sequences, so larger movements are captured and not just the handshape. The MVP already uses a Start/Finish attempt and a sequence model.
- **Competition:** the Choice section now says plainly that feature-based reverse dictionaries exist, and that camera-based lookup appeared only as research prototypes in my searches. It calls this a possible gap, not a proven one.

Before the studio review, I'd suggest checking that no existing product already uses the name "Handshape" for sign language.

Two things are still open from before: the tech stack and where the LLM runs. For the next step, should I read the PopSign and ASL Citizen license texts, or scaffold the project and start the webcam tracking spike?

---

**Developer:**

lets read the liscense text, where are we pulling our sign database from

**Agent:**

[Fetched the ASL Citizen license page, the OSF API record for ASL-LEX, the PopSign dataset page (via curl, since the fetch tool rejected its certificate), and the NeurIPS PopSign abstract. The Kaggle page could not be read. Updated the sources table in pitch.md.]

I've read the license pages. Next I'm updating the pitch's data table with what I found.

I read the license pages and updated the sources table in [pitch.md](pitch.md).

**Where the sign data comes from**
- **PopSign v1.0 (leading candidate):**
  - The [dataset page](https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/) states "licensed under CC BY 4.0". That allows reuse, including for trained models, with attribution.
  - It has 250 signs from 47 Deaf signers and 200,686 videos (1.1 TB). It's collected from phone cameras and openly accessible.
  - The page lists suitable use as isolated sign recognition. It lists unsuitable uses as continuous recognition and sign-to-English translation. That matches the pitch's scope.
  - The [NeurIPS paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/00dada608b8db212ea7d9d92b24c68de-Abstract-Datasets_and_Benchmarks.html) says its signs are focused on one-handed signs. That matters for any two-hand tracking claims.
- **ASL-LEX 2.0 (sign metadata):** the OSF project lists CC BY 4.0, and its files include documentation and "ASL examples" folders. I haven't checked whether the example videos fall under the same license.
- **ASL Citizen (not a primary source):** it's [non-commercial research only](https://www.microsoft.com/en-us/research/project/asl-citizen/dataset-license/). It forbids distributing the data or your modifications to it, and it grants Microsoft a perpetual, irrevocable license to your modifications. The license doesn't say whether trained models count as modifications, so I'd treat it as evaluation-only unless you get clarification.
- **Kaggle asl-signs:** I couldn't read the Kaggle page, so its license is still unverified. I haven't confirmed how it relates to PopSign.

**What this means for the plan**
- The PopSign vocabulary comes with its own constraints. It's 250 signs, mostly one-handed. Lookup would cover those 250 signs, not all of ASL, and the app should say so. This is a limit of the dataset, so I'd treat it as a scope decision for you.
- The raw video is 1.1 TB. We'd likely extract landmarks from a subset of signs rather than the whole set. Whether PopSign offers a smaller or landmark-only download is the next thing I'd check.
- We must credit PopSign, and ASL-LEX if we use it, in the app and in `research.md`.
- I'm not a lawyer. If you want certainty on ASL Citizen's terms for trained models, you could email the maintainers.

For next steps I'd check PopSign's download guide and whether landmarks are available, then pick the first 20–30 signs from the 250. Do you want me to look at the download guide now?

---

**Developer:**

I'm not a lawyer. If you want certainty on ASL Citizen's terms for trained models, you could email the maintainers.

Give me the email and a proposal stating I am a student wanting to create a free project.

**Agent:**

Written for: the ASL Citizen maintainers at Microsoft Research, who would read this cold.

**Address:** ASL_Citizen@microsoft.com. This comes from a search summary of [Microsoft's ASL Citizen page](https://www.microsoft.com/en-us/research/project/asl-citizen/), which gave it as the contact for commercial-use questions. Check it against the page before sending. I haven't sent anything, and you should send it from your own account.

**Subject:** Student question: training and publishing a model with ASL Citizen for a free class project

Hello,

My name is [Your name], and I'm a student at [University] working on a class project for [course name, e.g. AET 330T AI Explorations, Fall 2026]. I'm writing to ask whether a use of the ASL Citizen dataset I'm considering is within its license terms.

**The project.** A free web app for people learning ASL, such as hearing family members and classmates of Deaf signers. A user performs an isolated sign on a webcam, and the app shows ranked candidate signs with reference videos. The app also helps users look up a sign they don't know. Hand tracking and recognition run in the browser. The app has no ads, accounts, revenue or commercial purpose. It recognizes isolated signs only, and it will say plainly that it is not an ASL translator or a substitute for interpreters. I'm treating the dataset's consent and its Deaf signers' contributions with care and want to use it as intended.

**What I'd like to do with ASL Citizen:**
1. Extract hand landmarks from the videos locally and use them to train a small recognition model.
2. Publish the trained model so it can run in users' browsers. The model would contain learned weights only. I would not distribute any videos or landmark data.
3. Credit ASL Citizen and its contributors in the app, and cite the NeurIPS 2023 paper.

**My questions:**
1. Is training a model on the data for a free, non-commercial, public project within the license?
2. Is publishing the trained model weights permitted?
3. Does a trained model count as a "modification" of the data under the license's grant-back clause?
4. May the app show ASL Citizen video clips as reference examples, or only link to them?
5. Do you have attribution or consent-related requirements I should follow?

If any of this is not permitted, I'll adjust the project, for example by using the dataset only for private evaluation. Thank you for building the dataset and for any guidance you can give.

Sincerely,
[Your name]
[University, course, contact email]

**Before you send it**
- Fill in the bracketed fields, including whichever email you want them to reply to.
- Question 3 comes from [the license text](https://www.microsoft.com/en-us/research/project/asl-citizen/dataset-license/), which has the grant-back clause but doesn't address trained models.
- PopSign's CC BY 4.0 license may make this unnecessary. If you go with PopSign as the main data source, you could skip the email, or send it only if you still want ASL Citizen for evaluation.

Do you want me to save the draft in the repo, or leave it here?

---

**Developer:**

write me an email i can copy and paste that sounds more human

**Agent:**

Written for: the ASL Citizen maintainers at Microsoft Research.

**To:** ASL_Citizen@microsoft.com (confirm this address on the [project page](https://www.microsoft.com/en-us/research/project/asl-citizen/) before sending)

**Subject:** Question from a student about using ASL Citizen for a free project

Hi,

I'm [Your name], a student at [University], and I'm building a class project this semester that I'd like to ask you about.

It's a free web app for hearing people learning ASL, like family members or classmates of Deaf signers. You sign into your webcam, and it suggests which sign it might be and shows you reference videos. It's also meant to help when you've seen a sign and have no idea what it means. Everything runs in the browser, there are no ads or accounts, and I'm not making any money from it. It only recognizes single, isolated signs. I'm not trying to build a translator, and I'll say clearly in the app that it's no replacement for interpreters.

I'd love to use ASL Citizen to train the recognition model. Before I do, I want to make sure that's okay. I read the license, but it doesn't say anything about trained models, so I didn't want to guess. Here's what I'm hoping to do:

- Train a small model on hand landmarks I extract from the videos
- Publish only the trained model, with no videos or landmark data, so it can run in people's browsers
- Credit ASL Citizen and cite the NeurIPS paper in the app

Could you let me know:
1. Whether training on the data for a free, non-commercial project like this is okay
2. Whether I can publish the trained model
3. Whether a trained model counts as a "modification" under the license's grant-back clause
4. Whether I can show ASL Citizen clips in the app, or should only link to them
5. Whether you'd like the credit written a particular way

If any of this isn't allowed, no problem. I'll adjust, maybe by using the data only for my own testing. Thanks so much for making the dataset, and for any help you can give.

Best,
[Your name]
[Your university and course]
[The email you'd like them to reply to]

I made it shorter and plainer, but all five questions are still in. You'll want to fill in the brackets. If PopSign ends up being your main dataset, you may not need to send this at all.

---

**Developer:**

wait i still want a translate function, but specify this is no replacement for a translator

**Agent:**

Written for: the ASL Citizen maintainers at Microsoft Research.

**Subject:** Question from a student about using ASL Citizen for a free project

Hi,

I'm [Your name], a student at [University], and I'm building a class project this semester that I'd like to ask you about.

It's a free web app for hearing people learning ASL, like family members or classmates of Deaf signers. It has a translate feature: you sign into your webcam, and it suggests which English words the sign might be and shows you reference videos. It also helps with signs you've seen but don't know. Everything runs in the browser, there are no ads or accounts, and I'm not making any money from it. For now it only recognizes single, isolated signs, not full conversation. It's meant as a learning aid, not a replacement for a qualified interpreter or translator, and the app will say so clearly.

I'd love to use ASL Citizen to train the recognition model. Before I do, I want to make sure that's okay. I read the license, but it doesn't say anything about trained models, so I didn't want to guess. Here's what I'm hoping to do:

- Train a small model on hand landmarks I extract from the videos
- Publish only the trained model, with no videos or landmark data, so it can run in people's browsers
- Credit ASL Citizen and cite the NeurIPS paper in the app

Could you let me know:
1. Whether training on the data for a free, non-commercial project like this is okay
2. Whether I can publish the trained model
3. Whether a trained model counts as a "modification" under the license's grant-back clause
4. Whether I can show ASL Citizen clips in the app, or should only link to them
5. Whether you'd like the credit written a particular way

If any of this isn't allowed, no problem. I'll adjust, maybe by using the data only for my own testing. Thanks so much for making the dataset, and for any help you can give.

Best,
[Your name]
[Your university and course]
[The email you'd like them to reply to]

**The PopSign data card lists "sign to English translation" as an unsuitable use.** The [PopSign data card](https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/) lists continuous recognition and sign-to-English translation as unsuitable uses. Its suitable use is isolated sign recognition. Showing an English label for one recognized sign is arguably the first, but a "translate" feature could be read as the second. To stay on the safe side:
- The app should call the feature something like "Translate (single signs)" and show English labels for isolated signs only.
- It shouldn't turn multiple signs into English sentences.
- You could add a question to the PopSign maintainers (thad@gatech.edu is listed as the contact) asking whether showing English glosses for isolated signs fits the "unsuitable use" note.

I haven't changed pitch.md. Do you want me to rename Translate mode there as "single signs only"?

---

**Developer:**

[Pasted text from the ASL Citizen project page: describes the dataset (about 84k videos, 2.7k signs), its framing as dictionary retrieval, the research team, the license pointer and commercial-use contact ASL_Citizen@microsoft.com, download links, the open-source repo microsoft/ASL-citizen-code, and the citation request with BibTeX.]

This is on their website

**Agent:**

Thanks, this helps. I'll make two small edits to [pitch.md](pitch.md) from it and explain why below.

[Edited the ASL Citizen row in pitch.md.]

**What the page tells us**
- **It supports the lookup idea.** The authors describe dictionary retrieval as the real-world task: you see a sign, repeat it on an ordinary camera, and get a list of the closest signs. That's your lookup feature. Citing it in the pitch gives lookup a research basis, which strengthens the "verified" angle.
- **It speaks to your worry about getting it wrong.** The data was collected with consent under IRB approval, and Deaf research team members were involved throughout. That is stronger than the WLASL-style sources we avoided.
- **The accuracy figure differs slightly.** The page says the baselines improve the state of the art "from about 32% to 62%". The search summary I used earlier said 63%. I've changed the pitch to cite about 62% from the project page and flagged the difference, so check the paper before citing one number.

**Open items**
- **The email address:** the page lists ASL_Citizen@microsoft.com only for commercial-use questions. It's still the only contact given, so I'd keep using it. You could add a line saying you're a student and the project is non-commercial, so they know why you're writing. The paper's PI is Danielle Bragg, but I don't have an address for her and wouldn't guess one.
- **Citation:** the page asks users to cite their paper. That goes into the credits in `research.md`, and I'll add it when we write that file.
- **Code:** a [microsoft/ASL-citizen-code](https://github.com/microsoft/ASL-citizen-code) repo exists. I haven't checked its license, but it could be a baseline to learn from if the license allows.
- **Download:** the page gives a direct zip link. I haven't checked its size, so I'd check that before downloading anything.

For the email, I can add one sentence saying your lookup feature is the dictionary retrieval task they describe. It may help them see the project is in line with their intent. Want me to add it?

---

**Developer:**

yes

**Agent:**

Written for: the ASL Citizen maintainers at Microsoft Research.

**To:** ASL_Citizen@microsoft.com

**Subject:** Question from a student about using ASL Citizen for a free project

Hi,

I'm [Your name], a student at [University], and I'm building a class project this semester that I'd like to ask you about. It's non-commercial, so I'm writing to check the license terms rather than about commercial use.

It's a free web app for hearing people learning ASL, like family members or classmates of Deaf signers. It has a translate feature: you sign into your webcam, and it suggests which English words the sign might be and shows you reference videos. It also helps with signs you've seen but don't know. That second part is the dictionary retrieval task you describe in your paper: someone repeats a sign on an everyday camera and gets a ranked list of the closest signs. Everything runs in the browser, there are no ads or accounts, and I'm not making any money from it. For now it only recognizes single, isolated signs, not full conversation. It's meant as a learning aid, not a replacement for a qualified interpreter or translator, and the app will say so clearly.

I'd love to use ASL Citizen to train the recognition model. Before I do, I want to make sure that's okay. I read the license, but it doesn't say anything about trained models, so I didn't want to guess. Here's what I'm hoping to do:

- Train a small model on hand landmarks I extract from the videos
- Publish only the trained model, with no videos or landmark data, so it can run in people's browsers
- Credit ASL Citizen and cite the NeurIPS paper in the app

Could you let me know:
1. Whether training on the data for a free, non-commercial project like this is okay
2. Whether I can publish the trained model
3. Whether a trained model counts as a "modification" under the license's grant-back clause
4. Whether I can show ASL Citizen clips in the app, or should only link to them
5. Whether you'd like the credit written a particular way

If any of this isn't allowed, no problem. I'll adjust, maybe by using the data only for my own testing. Thanks so much for making the dataset, and for any help you can give.

Best,
[Your name]
[Your university and course]
[The email you'd like them to reply to]

Fill in the bracketed fields before sending. I haven't sent anything.

---

**Developer:**

it states how it wants to be credited though & the use case. Please read what I sent you

**Agent:**

You're right. The page asks users to cite their paper and gives the BibTeX entry, so question 5 was unnecessary. It also states the intended use as dictionary retrieval, which is what your lookup does. I've removed the credit question and now say you'll follow their citation request and that your use matches their stated one.

Written for: the ASL Citizen maintainers at Microsoft Research.

**To:** ASL_Citizen@microsoft.com

**Subject:** Question from a student about using ASL Citizen for a free project

Hi,

I'm [Your name], a student at [University], working on a class project this semester. It's non-commercial, so I'm writing to check the license terms, not to ask about commercial use.

I'm building a free web app for hearing people learning ASL, like family members or classmates of Deaf signers. It has a translate feature that suggests English words for a sign you perform on your webcam, and it helps you look up signs you've seen but don't know. That second part is the dictionary retrieval task from your paper. Everything runs in the browser, with no ads or accounts and no income. It only handles single, isolated signs, not full conversation, and the app will say clearly that it isn't a replacement for a qualified interpreter or translator.

I'd like to train the recognition model on ASL Citizen, and I'll cite your paper as your page asks. My plan is to extract hand landmarks locally and train a small model, then publish only the trained model so it can run in people's browsers. I wouldn't distribute any videos or landmark data.

The license doesn't say anything about trained models, so I'd rather ask than guess:
1. Is training on the data for a free, non-commercial project like this okay, and may I publish the trained model?
2. Does a trained model count as a "modification" under the license's grant-back clause?
3. May the app show ASL Citizen clips as reference examples, or should I only link to them?

If any of this isn't allowed, no problem. I'll adjust, maybe by using the data only for my own testing. Thank you for making the dataset, and for any help you can give.

Best,
[Your name]
[Your university and course]
[The email you'd like them to reply to]

I merged two of the earlier questions, so there are now three. Fill in the brackets before sending. I haven't sent anything.

---

**Developer:**

okay emial is sent, what else do i have to finihs in pitch, what is tech stack?

**Agent:**

[Checked pitch.md for remaining bracketed items.]

**Tech stack** means the tools the app is built with. The draft proposes these, and you haven't confirmed any of them:

| Part | Proposed tool | What it does |
|---|---|---|
| App and interface | TypeScript + Vite | TypeScript is JavaScript with type checks. Vite builds and serves the site. Your earlier projects used plain HTML, CSS and JS with no build step. |
| Hand tracking | MediaPipe Tasks Vision | Finds the 21 landmarks on each hand in the webcam video, in the browser. It's Apache 2.0. |
| Training the sign model | Python | Used once, offline, to extract landmarks from the dataset videos and train the model. |
| Running the model | TensorFlow.js or ONNX Runtime Web | Runs the trained model in the visitor's browser, so nothing leaves their device. |
| Hosting | GitHub Pages | Free static hosting, as in your Project 4. It can't run server code, which affects the LLM option. |

The new parts for you are Python training and getting the model into the browser. I haven't verified current package versions for any of these. We'd check them in the first spike.

**Still to do in the pitch**
1. **Confirm the Choice section** (line 33). It should say what you chose and why, in your own words.
2. **Confirm the Tech stack** (line 87), or tell me what to change. One decision is whether you'd rather keep your usual no-build setup.
3. **Add a title and logo.** "Handshape" is a working title, and there's no logo yet. I'd also check the name isn't taken by an existing sign language product.
4. **Decide where the LLM runs.** It's currently a stretch goal, with in-browser versus hosted undecided.
5. **Trim the length.** The whole file is about 1,300 words, and the Pitch section is under 1,000 (unverified since the table grew). Check it.
6. **Rewrite in your own voice.** The working agreement says the pitch should be in your terms, so edit anything that doesn't sound like you.
7. **Get approval.** Once the pitch is final, send it to the studio director for approval.

The "Ideas" and "Choice" sections should also say what's your own thinking and what came from me.

Once you confirm the stack, I'd next write `research.md` and `spec.md` entries. Do you want to confirm the stack now, or should I list the stack decisions with their trade-offs first?

---

**Developer:**

[IDE note: the user opened pitch.md.]

I got a bounceback from the email. I chose this because it reminds me of my friend's sister who is deaf, how hard it is and limited communication people have in accessing ASL and having proper form. I want a easier way to make sure without hvaing another human check you.

give me a prompt to send to gpt for a logo.

Where the LLM runs, explain.

The pitch is in my terms, edit the why to sound like what i wrote for hte why.

**Agent:**

[Rewrote the Why section of pitch.md in the developer's voice. Searched for an alternative ASL Citizen contact; could not verify author email addresses from the paper PDF.]

**Bounced email**
- The error `550 5.4.1 Recipient address rejected: Access denied` is a Microsoft 365 rejection. It usually means the address isn't accepting mail from outside, or doesn't exist. I'm inferring that from the code, not from Microsoft's documentation.
- The address appeared on the project page for commercial-use questions, so it may simply be unmonitored or internal. Nothing I found confirms it handles general questions.
- **Options:**
  - Write to the PI, Danielle Bragg. A search summary of the paper listed `dabragg@microsoft.com`, but I couldn't verify that, so check the paper's first page yourself.
  - Open a question on the [ASL-citizen-code GitHub repo](https://github.com/microsoft/ASL-citizen-code). That's public and visible to the maintainers.
  - Use PopSign (CC BY 4.0) as the main data. That way this question isn't blocking, and you can ask again later if you still want ASL Citizen for evaluation.
- I can retarget the email to Dr. Bragg if you want, but I'd wait for you to decide whether to cold-email her.

**Why section**
I rewrote it in your voice from what you wrote: your friend's sister, the limited access to ASL, and wanting to check a sign without another human. I kept it plain. I added one sentence of limits: the tool can show whether the model recognized the sign you meant, but it can't judge form, facial expression or grammar. Edit or cut anything you don't want. I wrote "a friend's sister who is deaf" without a name, and you can remove that line if you'd rather not mention her.

Your goal is checking proper form, but the tool can't fully do that. Recognizing the intended sign is not the same as signing it correctly, and the model doesn't analyze facial grammar. The pitch should keep the honest wording above. A "check my sign" feature, where you pick a target sign and see whether it's recognized, would serve your goal best. That's close to Learn mode, which is currently secondary. Do you want to raise its priority?

**Where the LLM runs**
This means which computer does the LLM's work.
- **In the visitor's browser:** a small LLM downloads to their device. It's free and fully private, but the download is large and slow on weak devices, and a small model re-ranks less well. I haven't checked current download sizes.
- **On a server or API:** the typed context text goes to a third party. You'd need a small backend to keep the API key secret, and you'd have to watch costs and rate limits. Free tiers change, so check the current terms first. GitHub Pages can't host this by itself.
- **Not at launch:** use handshape and location filters only. That's free, private and simplest.

My recommendation: start without it and compare. If filters work well enough, the LLM adds little. If you add it later, make it in-browser to keep "free and private". It's your call.

**Logo prompt for GPT**
> Design a simple, modern logo mark and wordmark for a free web app called "Handshape" that helps people learn and look up American Sign Language using their webcam. The mark should be an abstract, stylized hand built from a few clean lines and small dots, as if hand-tracking landmarks were connected into a hand shape. Do not depict a specific ASL sign or letter, and keep the hand anatomically simple and neutral. Style: calm, friendly, high contrast, flat vector, minimal, with rounded geometry. Use at most two colors on a plain background, such as deep navy and warm coral, with strong contrast and no gradients. Wordmark: "Handshape" in a clean, highly legible sans-serif. Deliver a square icon version and a horizontal version with the wordmark, legible at small sizes, with no extra text.

Check the result carefully. AI-generated hands often have wrong fingers or odd joints, and a mistaken hand in an ASL app's logo would be a real problem. I used an abstract hand and told it not to depict a sign for that reason. If it does depict one, have an ASL source check it.

---

**Developer (sent mid-turn):**

[Pasted bounce message: "Your message to ASL_Citizen@microsoft.com has been blocked ... 550 5.4.1 Recipient address rejected: Access denied ..."]

---

**Developer:**

start without it and compare. If filters work well enough, the LLM adds little. If you add it later, make it in-browser to keep "free and private". It's your call. Lets go with your suggestion.

**Agent:**

[Edited pitch.md in three places to record the LLM decision.]

I recorded the LLM decision in [pitch.md](pitch.md) in three places:
- **Technical goals:** no LLM at launch. Lookup uses the sign model plus handshape and location filters, and we compare before deciding.
- **Stretch goals:** the re-ranker is built only if filters fall short, and it runs in the browser.
- **Risks:** the LLM risk is now download size and speed, not cost and privacy.

**Still open in the pitch**
1. **Confirm the Choice section.**
2. **Confirm the Tech stack.**
3. **Decide Learn's priority.** Your goal of checking a sign without a human points to a "check my sign" feature. Do you want it raised from secondary?
4. **Settle the dataset question.** The ASL Citizen email bounced, so PopSign (CC BY 4.0) is the working primary source.
5. **Finalize the logo and title.** Check the "Handshape" name against existing products.

Which of these should we take next?

---

**Developer:**

Let think about how the webcam tracking works, I'm thinking both hand motion tracking and finger tracking.

**Agent:**

[Searched the MediaPipe documentation for Hand Landmarker, Pose Landmarker and Holistic Landmarker.]

Finger tracking and hand motion tracking aren't two separate systems. They come from the same tracker, and the difference is what you do with its output.

**How it works**
1. The webcam gives the browser video frames, around 30 per second.
2. MediaPipe's [Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/web_js) finds up to two hands per frame (`numHands`, default 1) and returns 21 landmarks per hand. These are the wrist, the finger joints and the fingertips, each with x, y and z. x and y are normalized to the image size, and z is measured relative to the wrist.
3. **Finger tracking** is the relationship between those 21 points within one frame. That is handshape.
4. **Hand motion tracking** is how those points change across frames, such as the wrist's path and the direction of travel. The app records them as a timestamped sequence.
5. The sign model reads the sequence, not single frames. A moving sign can't be told apart from one pose.
6. In video mode the tracker only re-detects the hand when it loses track, which saves work.

**The catch: location**
- Many signs depend on where the hand is relative to the face or body. Hand Landmarker alone only gives positions in the image, not relative to the signer.
- To fix that, you'd add body or face reference points. MediaPipe has standalone Pose and Face landmarkers, plus a [Holistic Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker/web_js) that combines face, pose and hands. The docs I saw list its total as 553 landmarks, and an older page says 543.
- More landmarks mean more work per frame. We haven't measured speed on your device, and the first spike should.

**Things that can go wrong**
- Fingers hiding each other, or one hand covering the other, can lose landmarks.
- Fast movement blurs at 30 frames per second.
- Depth (z) is an estimate, so I wouldn't rely on it too much.
- Left and right hands can swap if you mirror the preview carelessly.
- Poor lighting hurts everything.
- The model must be trained on landmarks from the same MediaPipe version and settings as the browser uses. Otherwise live results will differ from training.

**Decisions for you**
1. **Reference points:** hands only at first, or hands plus pose or face for location? I'd start with hands plus a few body points and measure the cost. The pitch's "location" and "larger movements" goals depend on it.
2. **Two hands:** PopSign is mostly one-handed signs. Do you want two-hand tracking from the start, or only when a sign needs it?
3. **Spike:** I'd build the webcam tracker first, drawing the landmarks live and logging frame rate, before any model work. Is that the next step?

---

**Developer:**

[Image: a draft logo, an abstract open hand outline in navy with coral dots at fingertips and along the palm edge. Saved later as reference/handshape-logo-draft.png.]

I'm okay with the TechStack if you think that is good. 3, still prio translate and unknown sign check.

**Agent:**

[Marked the tech stack confirmed in pitch.md. Checked Python version (3.9.6).]

**Tech stack:** I think it's a good fit, and I marked it confirmed in [pitch.md](pitch.md). Two cautions:
- **Python version:** this Mac has Python 3.9.6, which is old. The training libraries, MediaPipe and a TensorFlow or PyTorch build, may need a newer Python. I'd check that before the training step and install a newer one only with your OK.
- **Model runtime:** I'd pick between TensorFlow.js and ONNX Runtime Web during the spike, not now.

**Logo:** it matches the prompt. It's abstract, in two colors, and has no wordmark. My notes, as feedback and not a decision:
- It reads as a generic open palm, a bit like a "stop" sign. The tracking idea comes through only through the coral dots.
- The dots aren't connected, and there are only 8 of them, so it doesn't evoke MediaPipe's 21 landmarks. Connecting some dots with thin lines would make the tracking idea clearer.
- The thumb sits low and the three bottom dots feel arbitrary. The anatomy is passable.
- It has no "Handshape" wordmark yet, and you asked for a horizontal version too. Test it at small sizes.
- The course asks you to credit all assets. Record it in `research.md` as AI-generated, with the tool and the terms of use.

I haven't copied it into the repo. Want me to save it in `reference/` or a branding folder?

**Priorities:** Translate and unknown-sign check stay first, with Learn second. That's already what the pitch says.

**Proposed first checkpoint (the tracking spike)**
Because you didn't answer my two earlier questions, I'd go with my defaults: hands plus a few body points, and two hands allowed.
1. Scaffold Vite + TypeScript and add MediaPipe Tasks Vision.
2. Start and stop the camera, with a mirror toggle that doesn't affect tracking.
3. Draw the landmarks live, and show each hand's detected handedness and a tracking-lost state.
4. Log measured frame rate and latency, and test with hands only against hands plus pose.
5. Run it and show you a screenshot or output before calling it done.

The spike doesn't need the recognition model or the dataset yet. Do you want me to go ahead with it? I'd also commit the project documents to the new repo first, so the original files are separate from my code. Should I do that?

---

**Developer:**

put the png file i send to references. I just need the pitch.md to be done for now what is the spike

**Agent:**

[Copied the logo to reference/handshape-logo-draft.png and checked pitch.md for remaining brackets.]

I saved the logo as [reference/handshape-logo-draft.png](reference/handshape-logo-draft.png).

**What the spike is**
A spike is a small, throwaway-quality build that tests the riskiest technical question before committing to the plan. Here it's the webcam tracker:
- Open the camera in the browser, find your hands with MediaPipe, and draw the landmarks live.
- Show handedness and a "tracking lost" state, and record the frame rate on your Mac.
- Test hands only against hands plus body points.

It answers whether tracking is fast and reliable enough to build on. It doesn't touch the sign model or the dataset. I haven't started it.

**Where pitch.md stands**
- The Pitch section is now about 1,010 words, near the ~1,000 target. The whole file is longer because of the Ideation section.
- The only bracket left is in the Choice section (line 33), "[Developer to confirm]". Read that paragraph, edit it in your own words, then delete the bracket. I didn't confirm it for you.
- The Branding section and the logo's credit line in `research.md` are also still open. The logo is saved but not yet credited as AI-generated.
- The Ideation section is mine, written from our chat. You may want to adjust it so it reflects your own thinking.

Nothing is committed. When you're done with the pitch, I can commit the documents to the new repo as the first commit. Should I?

---

**Developer:**

[IDE note: the user opened pitch.md.]

credit the logo as AI-gen'd I'm good with this pitch. lets make a repo and save it to it

**Agent:**

[Removed the remaining "[Developer to confirm]" bracket and updated the Ideation note in pitch.md. Added the logo credit to research.md. Checked git identity and scanned for secrets (none found). Committed c47de08 and pushed to origin/main.]

Identity is set and the secrets check found nothing, so I'm committing and pushing.

The pitch and logo are committed and pushed to your private repo, [Project5-ASL-Workspace](https://github.com/TristanTengGH2/Project5-ASL-Workspace). The commit is `c47de08`, and the secrets check found nothing.

**Changes**
- **Pitch:** I removed the "[Developer to confirm]" bracket from the Choice section and changed the top note to say it was drafted with me and approved by you. I haven't changed any wording.
- **Logo credit:** [research.md](research.md) now has an Assets entry saying the logo is AI-generated by you with ChatGPT from a prompt we wrote together.
- **Two blanks in that entry are yours to fill in:** the exact model and date, and the tool's terms of use for generated images.

**Not done yet**
- **Other sources:** the dataset and tool credits (PopSign, ASL-LEX, ASL Citizen's requested citation, MediaPipe) aren't in `research.md` yet. I can add them.
- **Transcript:** nothing is saved in `transcripts/` yet. Tell me when you want this session saved there.
- **Weekly snapshot:** the brief wants `commit-log.txt` and a ZIP each week. That comes later.
- **Next step:** the tracking spike hasn't started. Say go when you want it.

---

**Developer:**

add them, go.

**Agent:**

[Added dataset, library and background source tables to research.md. Scaffolded a Vite + TypeScript app in app/ (camera.ts, tracker.ts, overlay.ts, main.ts, style.css, fetch-assets script), installed @mediapipe/tasks-vision 1.2.0, vite 8.3.5 and typescript 7.0.2, and fetched the hand and pose model files. Built it. Ran it in headless Chrome with a fake camera via playwright-core; fixed a duplicate-frame bug in the tracking loop; added run instructions to AGENTS.md; committed 9ff10c6 locally.]

Sources are added to [research.md](research.md). Now the spike: I'll scaffold a small Vite + TypeScript app in `app/`, with capture, tracking, drawing, and status split into separate modules.

Build and type-check pass. Now I'll run it in headless Chrome with a fake camera to check the page loads, the models load, the camera starts and stops, and the stats update. A fake camera has no hands in it, so this can't test real tracking.

Everything works, but the 60 fps figure is wrong. The camera delivers about 30 frames per second, and my loop was re-tracking duplicate frames. I'll fix that and find the 404.

The source credits are in [research.md](research.md), and the tracking spike builds and runs. I haven't tested it with a real hand.

**Sources added to research.md**
- **Datasets:** PopSign, ASL Citizen (including the bounced email and the paper citation to use), ASL-LEX, Kaggle ISLR, and WLASL (marked not used).
- **Libraries:** MediaPipe, Vite and TypeScript.
- **Background:** the lookup and Deaf-community sources.
- **To verify:** the license on MediaPipe's downloaded model file, and the Kaggle and ASL-LEX video terms, are still unconfirmed and marked as such.

**Spike**
- **Where it lives:** `app/`. Camera capture, the tracker, the drawing overlay and the status text are separate modules.
- **What it does:**
  - Start and stop the camera, with the microphone off.
  - Draw hand landmarks, plus optional body points.
  - Show a mirror toggle that only flips the display.
  - Show messages for no camera, permission denied, no hands, one hand, both hands, and tracking lost.
  - Show frames per second and tracking time.
  - Release the camera on stop.
- **Setup:** model files and the WASM runtime are served from the app, with no CDN at runtime. They're git-ignored and fetched by `npm run fetch-assets`.
- **What I tested:** headless Chrome with a fake camera.
  - The page loads, the models load, and the camera starts and stops.
  - Stopping drops the camera's live tracks from 1 to 0.
  - The mirror flip works (the fake camera's text appears flipped).
  - The status read "No hands detected" with no console errors.
  - The type-check and production build pass.
- **What I couldn't test:** whether the landmarks actually follow your hands, and your handedness labels. The fake camera has no hands.
- **Timings are not meaningful yet.** The headless run reported about 12 ms per frame for hands only and about 20 ms with body points. Headless Chrome isn't your normal browser, and I saw 60 frames per second from a camera that should deliver about 30, so ignore those numbers.
- **Bug fixed:** I fixed a bug that tracked duplicate frames.

**Please test it with your real camera**
```
export PATH="$HOME/.local/node-v26.13.0-darwin-arm64/bin:$PATH"
cd "/Users/tyn/VS_Project/Ai-Explorations- Project5/project-5-template/app"
npm install && npm run fetch-assets && npm run dev
```
Open the printed URL and click Start camera. Check:
- Do the landmarks follow both hands?
- What frame rate and tracking time do you get, with and without the body-points box?
- Does mirror preview flip the video and the dots together?
- Which hand does the model call "Left" when you raise your right hand?

Two spike decisions I made: I enabled the GPU delegate in the tracker, and I run pose and hands in separate passes. Tell me if either causes trouble.

The spike is committed locally as `9ff10c6`, but not pushed. Do you want me to push it?

---

**Developer:**

psuh, all i needed done today was the pitch anyways.

**Agent:**

[Pushed 9ff10c6 to origin/main.]

Both commits are pushed to [Project5-ASL-Workspace](https://github.com/TristanTengGH2/Project5-ASL-Workspace), and the local branch matches the remote.

Your pitch is in `pitch.md`, and the sources and logo credit are in `research.md`. I went further than you needed today by adding the tracking spike. It's safe to ignore until you're ready to test it with your camera.

Some things are left for later:
- **Logo credit:** fill in the model, date and terms of use in the `research.md` entry.
- **Transcript:** tell me when you want this session saved there.
- **Dataset permission:** PopSign is the working data source, since the ASL Citizen email bounced.

---

**Developer:**

yes, get the transcript & push

---

## Notes on this transcript

- Tool calls and tool output are summarized in brackets, not reproduced.
- The attached file ASL_Project_Chat_Transcript.txt (the earlier brainstorming chat) is not reproduced in full. It was an attachment to the first Developer message, and it is not stored in this repository.
- The pasted ASL Citizen web page text is summarized in brackets.
- The pasted email bounce message is summarized in brackets.
- The logo image is not embedded; it is saved at reference/handshape-logo-draft.png.
- Agent replies are reproduced from the session. Where the Agent wrote a short lead-in sentence followed by tool calls and then a longer summary, the lead-in and the summary appear together under one Agent label.
