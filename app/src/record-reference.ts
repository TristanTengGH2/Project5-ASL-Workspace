// Dev-only reference recorder: a fluent signer records a sign with the app's own tracker and the
// result is saved as landmark numbers only (see reference-take.ts). It is not part of the
// production build and refuses to run away from localhost.
import { Camera } from "./camera";
import { Overlay } from "./overlay";
import { drawBodyScene, drawHandScene, sceneExtent } from "./reference-draw";
import { buildTake, type RecordedFrame, type Take } from "./reference-take";
import { Tracker, type TrackingFrame } from "./tracker";

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const statusEl = $("status");
const signSelect = $<HTMLSelectElement>("sign");
const signHint = $("sign-hint");
const mirror = $<HTMLInputElement>("mirror");
const cameraButton = $<HTMLButtonElement>("camera");
const recordButton = $<HTMLButtonElement>("record");
const stage = $("stage");
const video = $<HTMLVideoElement>("video");
const review = $("review");
const bodyCanvas = $<HTMLCanvasElement>("review-body");
const handCanvas = $<HTMLCanvasElement>("review-hands");
const trimStart = $<HTMLInputElement>("trim-start");
const trimEnd = $<HTMLInputElement>("trim-end");
const stats = $("stats");
const saveButton = $<HTMLButtonElement>("save");

const COUNTDOWN_SECONDS = 3;
const MAXIMUM_RECORDING_MS = 6000;
const FRAMES_PER_SECOND = 16;

interface CatalogSign { id: string; displayGloss: string; status: string }
const setStatus = (text: string) => { statusEl.textContent = text; };

if (!["localhost", "127.0.0.1"].includes(location.hostname)) {
  setStatus("This tool only runs on localhost.");
  throw new Error("localhost only");
}

const camera = new Camera(video);
const overlay = new Overlay($<HTMLCanvasElement>("overlay"));
let tracker: Tracker | null = null;
let facts: Record<string, { hands: string }> = {};
let signs: CatalogSign[] = [];
let loopId = 0;
let latestPose: TrackingFrame["pose"] = null;
let processed = 0;
let lastVideoTime = -1;
let state: "idle" | "countdown" | "recording" = "idle";
let phaseStarted = 0;
let recorded: RecordedFrame[] = [];
let size: [number, number] = [0, 0];
let take: Take | null = null;
let previewFrame = 0;
let previewTimer = 0;

async function loadSigns(): Promise<void> {
  const base = import.meta.env.BASE_URL;
  const [catalog, factFile] = await Promise.all([
    fetch(`${base}data/sign-catalog.json`).then((response) => response.json()),
    fetch(`${base}data/sign-facts.json`).then((response) => response.json()),
  ]);
  signs = (catalog.signs as CatalogSign[]).filter((sign) => sign.status === "supported");
  facts = factFile.signs;
  signSelect.replaceChildren(...signs.map((sign) => new Option(sign.displayGloss, sign.id)));
  updateHint();
}

function updateHint(): void {
  const hands = facts[signSelect.value]?.hands;
  signHint.textContent = hands === "two" ? "This sign uses two hands: keep both hands and both shoulders in view."
    : hands === "one" ? "This sign uses one hand: keep that hand and both shoulders in view." : "Keep your hands and both shoulders in view.";
}

function loop(): void {
  loopId = requestAnimationFrame(loop);
  if (!tracker || video.readyState < 2 || video.currentTime === lastVideoTime) return;
  lastVideoTime = video.currentTime;
  const now = performance.now();
  processed += 1;
  const tracked = tracker.track(video, now, latestPose === null || processed % 3 === 0);
  if (tracked.pose) latestPose = tracked.pose;
  overlay.render({ ...tracked, pose: latestPose }, video.videoWidth, video.videoHeight);
  if (state === "countdown") {
    const remaining = COUNTDOWN_SECONDS - Math.floor((now - phaseStarted) / 1000);
    if (remaining <= 0) {
      state = "recording";
      phaseStarted = now;
      recorded = [];
      size = [video.videoWidth, video.videoHeight];
      recordButton.textContent = "Stop";
    } else setStatus(`Get ready… ${remaining}`);
  } else if (state === "recording") {
    recorded.push({
      timestampMs: now,
      hands: tracked.hands.flatMap((hand) => {
        const label = hand.modelLabel.toLowerCase();
        return label === "left" || label === "right" ? [{ label, landmarks: hand.landmarks.map(({ x, y, z }) => ({ x, y, z })), score: hand.score }] : [];
      }),
      pose: latestPose?.map(({ x, y, z, visibility }) => ({ x, y, z, visibility })) ?? null,
    });
    setStatus(`Recording… ${((now - phaseStarted) / 1000).toFixed(1)} s. Press Stop when you finish the sign.`);
    if (now - phaseStarted >= MAXIMUM_RECORDING_MS) finishRecording();
  } else {
    const count = tracked.hands.length;
    setStatus(count === 0 ? "No hands detected." : count === 1 ? "One hand tracked." : "Both hands tracked.");
  }
}

function finishRecording(): void {
  state = "idle";
  recordButton.textContent = "Record";
  recordButton.disabled = false;
  startReview(recorded, size[0], size[1]);
}

let reviewSource: { frames: RecordedFrame[]; width: number; height: number } | null = null;

function startReview(frames: RecordedFrame[], width: number, height: number): void {
  reviewSource = { frames, width, height };
  trimStart.max = trimEnd.max = String(frames.length - 1);
  trimStart.value = "0";
  trimEnd.value = String(frames.length - 1);
  review.hidden = false;
  rebuildTake();
}

function rebuildTake(): void {
  if (!reviewSource) return;
  clearInterval(previewTimer);
  take = null;
  saveButton.disabled = true;
  const start = Number(trimStart.value);
  const end = Number(trimEnd.value);
  try {
    take = buildTake(reviewSource.frames, reviewSource.width, reviewSource.height, [start, Math.max(start, end)]);
  } catch (error) {
    stats.textContent = (error as Error).message;
    setStatus("This take cannot be saved yet.");
    return;
  }
  const wantsTwo = facts[signSelect.value]?.hands === "two";
  const otherNote = take.otherFrames ? `other hand tracked in ${Math.round(take.stats.otherRate * 100)}% of frames` : `other hand not saved (tracked in ${Math.round(take.stats.otherRate * 100)}%)`;
  stats.textContent = `${take.stats.trimmedFrames} frames over ${(take.stats.durationMs / 1000).toFixed(1)} s; signing hand (${take.stats.dominantLabel}) tracked in ${Math.round(take.stats.dominantRate * 100)}% of frames; ${otherNote}.`;
  if (wantsTwo && !take.otherFrames) {
    setStatus("This sign uses two hands but the other hand was not tracked enough. Retake with both hands clearly in view.");
    return;
  }
  saveButton.disabled = false;
  setStatus("Check the preview, trim the start and end so only the sign remains, then save.");
  const motion = { frames: take.frames, ...(take.otherFrames ? { otherFrames: take.otherFrames } : {}) };
  const extent = sceneExtent(motion);
  previewFrame = 0;
  previewTimer = window.setInterval(() => {
    previewFrame = (previewFrame + 1) % take!.frames.length;
    drawBodyScene(bodyCanvas, motion, previewFrame, mirror.checked);
    drawHandScene(handCanvas, motion, previewFrame, mirror.checked, extent);
  }, 1000 / FRAMES_PER_SECOND);
}

function saveTake(): void {
  if (!take) return;
  const sign = signs.find((candidate) => candidate.id === signSelect.value)!;
  const payload = {
    schemaVersion: 1,
    signId: sign.id,
    gloss: sign.displayGloss,
    recordedAt: new Date().toISOString().slice(0, 10),
    frames: take.frames,
    otherFrames: take.otherFrames,
    stats: { ...take.stats, dominantRate: Math.round(take.stats.dominantRate * 100) / 100, otherRate: Math.round(take.stats.otherRate * 100) / 100 },
  };
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([`${JSON.stringify(payload)}\n`], { type: "application/json" }));
  link.download = `reference-take-${sign.displayGloss}-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
  setStatus(`Saved ${link.download}. Merge it with training/merge_reference_takes.py.`);
}

async function startCamera(): Promise<void> {
  cameraButton.disabled = true;
  setStatus("Loading tracking models…");
  try { tracker ??= await Tracker.create(); } catch (error) { setStatus(`Tracking models failed to load: ${(error as Error).message}`); cameraButton.disabled = false; return; }
  const problem = await camera.start();
  cameraButton.disabled = false;
  if (problem) { setStatus(problem === "permission-denied" ? "Camera permission denied." : "The camera could not be started."); return; }
  cameraButton.textContent = "Stop camera";
  recordButton.disabled = false;
  lastVideoTime = -1;
  processed = 0;
  latestPose = null;
  loop();
}

function stopCamera(): void {
  cancelAnimationFrame(loopId);
  camera.stop();
  overlay.render(null, video.videoWidth, video.videoHeight);
  state = "idle";
  cameraButton.textContent = "Start camera";
  recordButton.disabled = true;
  recordButton.textContent = "Record";
  setStatus("Camera is off.");
}

cameraButton.addEventListener("click", () => (camera.running ? stopCamera() : void startCamera()));
recordButton.addEventListener("click", () => {
  if (state === "recording") { finishRecording(); return; }
  if (state !== "idle") return;
  review.hidden = true;
  clearInterval(previewTimer);
  state = "countdown";
  phaseStarted = performance.now();
});
$("retake").addEventListener("click", () => { review.hidden = true; clearInterval(previewTimer); setStatus("Press Record when you are ready."); });
saveButton.addEventListener("click", saveTake);
trimStart.addEventListener("input", rebuildTake);
trimEnd.addEventListener("input", rebuildTake);
signSelect.addEventListener("change", () => { updateHint(); if (reviewSource) rebuildTake(); });
mirror.addEventListener("change", () => stage.classList.toggle("mirrored", mirror.checked));
stage.classList.toggle("mirrored", mirror.checked);
addEventListener("pagehide", () => camera.stop());

await loadSigns();
setStatus("Choose a sign and start the camera.");
// Test hook (localhost only): lets automation review a synthetic recording without a camera.
(window as unknown as { referenceRecorder: unknown }).referenceRecorder = {
  review: (frames: RecordedFrame[], width: number, height: number) => startReview(frames, width, height),
  currentTake: () => take,
};
