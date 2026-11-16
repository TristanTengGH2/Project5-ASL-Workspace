import { Camera } from "./camera";
import { CaptureController } from "./capture-controller";
import { Overlay } from "./overlay";
import type { SequenceDiagnostics } from "./preprocessing";
import { Recognizer, type RankedCandidate } from "./recognizer";
import { Tracker, type TrackingFrame } from "./tracker";

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const video = $<HTMLVideoElement>("video");
const stage = $("stage");
const toggleBtn = $<HTMLButtonElement>("toggle-camera");
const scanBtn = $<HTMLButtonElement>("scan-sign");
const mirror = $<HTMLInputElement>("mirror");
const usePose = $<HTMLInputElement>("use-pose");
const showLabels = $<HTMLInputElement>("show-labels");
const statusEl = $("status");
const resultsEl = $("results");
const candidateList = $("candidate-list");
const scanFeedback = $("scan-feedback");
const scanPhase = $("scan-phase");
const liveMatch = $("live-match");
const diagnosticBtn = $<HTMLButtonElement>("download-diagnostic");

const camera = new Camera(video);
const overlay = new Overlay($<HTMLCanvasElement>("overlay"));
let tracker: Tracker | null = null;
let recognizer: Recognizer | null = null;
let loopId = 0;
let latestPose: TrackingFrame["pose"] = null;
let processedFrames = 0;
let recent: { t: number; ms: number }[] = [];
const LOST_WINDOW_MS = 2000;
let lastHandsSeen = -Infinity;
let lastVideoTime = -1;
let previewBusy = false;
let latestDiagnostic: {
  createdAt: string;
  contractVersion: number;
  tensorShape: [number, number];
  diagnostics: SequenceDiagnostics;
  tensor: number[];
  browserRanking: RankedCandidate[];
} | null = null;

function setStatus(text: string): void { statusEl.textContent = text; }

function setScanStatus(text: string): void {
  setStatus(text);
  scanPhase.textContent = text;
  scanFeedback.hidden = false;
}

function handsState(frame: TrackingFrame, now: number): string {
  if (frame.hands.length === 2) return "Both hands tracked.";
  if (frame.hands.length === 1) return "One hand tracked (show both if the sign uses two).";
  return now - lastHandsSeen < LOST_WINDOW_MS ? "Tracking lost: hands left the frame or are hidden." : "No hands detected.";
}

function resetScanControl(): void {
  scanBtn.textContent = "Scan a sign";
  scanBtn.disabled = !camera.running;
}

function showCandidates(candidates: RankedCandidate[]): void {
  candidateList.replaceChildren(...candidates.slice(0, 3).map((candidate) => {
    const item = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = candidate.label;
    const score = document.createElement("strong");
    score.textContent = `${(candidate.score * 100).toFixed(1)}%`;
    item.append(label, score);
    return item;
  }));
  resultsEl.hidden = false;
}

const capture = new CaptureController(
  setScanStatus,
  async (sequence, diagnostics) => {
    try {
      const candidates = await recognizer!.rank(sequence);
      latestDiagnostic = {
        createdAt: new Date().toISOString(),
        contractVersion: 2,
        tensorShape: [48, 167],
        diagnostics,
        tensor: Array.from(sequence),
        browserRanking: candidates,
      };
      diagnosticBtn.disabled = false;
      showCandidates(candidates);
      setStatus("Not sure—compare these possible matches, or try again for clarity.");
      scanPhase.textContent = "Final possible match";
      liveMatch.textContent = candidates[0].label;
      liveMatch.hidden = false;
    } catch (error) {
      setScanStatus(`Recognition failed: ${(error as Error).message}`);
    }
  },
  resetScanControl,
  (sequence) => {
    if (previewBusy) return;
    previewBusy = true;
    void recognizer!.rank(sequence).then((candidates) => {
      if (capture.state !== "capturing") return;
      liveMatch.textContent = `Possible match: ${candidates[0].label}`;
      liveMatch.hidden = false;
    }).finally(() => { previewBusy = false; });
  },
);

function loop(): void {
  loopId = requestAnimationFrame(loop);
  if (!tracker || video.readyState < 2 || video.currentTime === lastVideoTime) return;
  lastVideoTime = video.currentTime;
  const now = performance.now();
  processedFrames += 1;
  const poseRequested = usePose.checked || capture.active;
  const runPose = poseRequested && (latestPose === null || processedFrames % 3 === 0);
  const tracked = tracker.track(video, now, runPose);
  if (tracked.pose) latestPose = tracked.pose;
  if (tracked.hands.length) lastHandsSeen = now;

  recent.push({ t: now, ms: tracked.ms });
  recent = recent.filter((result) => now - result.t < 1000);
  $("fps").textContent = String(recent.length);
  $("latency").textContent = (recent.reduce((sum, result) => sum + result.ms, 0) / recent.length).toFixed(1);
  $("hands").textContent = tracked.hands.map((hand) => `${hand.modelLabel} (${hand.score.toFixed(2)})`).join(", ") || "none";

  const frameWithPose = { ...tracked, pose: latestPose };
  overlay.render({ ...tracked, pose: usePose.checked ? latestPose : null }, video.videoWidth, video.videoHeight, {
    showLabels: showLabels.checked,
    mirrored: mirror.checked,
  });
  if (capture.active) capture.consume(frameWithPose, now);
  else setStatus(handsState(tracked, now));
}

async function startCamera(): Promise<void> {
  toggleBtn.disabled = true;
  setStatus("Loading tracking models…");
  try { tracker ??= await Tracker.create(); }
  catch (error) {
    setStatus(`Tracking models failed to load: ${(error as Error).message}`);
    toggleBtn.disabled = false;
    return;
  }
  setStatus("Starting camera…");
  const error = await camera.start();
  toggleBtn.disabled = false;
  if (error) {
    setStatus(error === "permission-denied" ? "Camera permission denied. Allow access and try again." : error === "no-camera" ? "No camera found." : "The camera could not be started.");
    return;
  }
  toggleBtn.textContent = "Stop camera";
  scanBtn.disabled = false;
  document.body.classList.add("camera-running");
  lastHandsSeen = -Infinity;
  lastVideoTime = -1;
  processedFrames = 0;
  latestPose = null;
  loop();
}

function stopCamera(): void {
  cancelAnimationFrame(loopId);
  capture.cancel();
  scanFeedback.hidden = true;
  latestDiagnostic = null;
  diagnosticBtn.disabled = true;
  camera.stop();
  overlay.render(null, video.videoWidth, video.videoHeight);
  recent = [];
  latestPose = null;
  toggleBtn.textContent = "Start camera";
  scanBtn.disabled = true;
  document.body.classList.remove("camera-running");
  setStatus("Camera is off.");
}

async function startScan(): Promise<void> {
  if (capture.active) {
    capture.cancel();
    scanFeedback.hidden = true;
    setStatus("Scan cancelled.");
    return;
  }
  scanBtn.disabled = true;
  setStatus("Loading recognition model…");
  try { recognizer ??= await Recognizer.create(); }
  catch (error) {
    setStatus(`Recognition model failed to load: ${(error as Error).message}`);
    resetScanControl();
    return;
  }
  resultsEl.hidden = true;
  candidateList.replaceChildren();
  latestDiagnostic = null;
  diagnosticBtn.disabled = true;
  liveMatch.hidden = true;
  liveMatch.textContent = "";
  scanFeedback.hidden = false;
  scanBtn.disabled = false;
  scanBtn.textContent = "Cancel scan";
  capture.start();
}

toggleBtn.addEventListener("click", () => camera.running ? stopCamera() : void startCamera());
scanBtn.addEventListener("click", () => void startScan());
diagnosticBtn.hidden = !["localhost", "127.0.0.1"].includes(location.hostname);
diagnosticBtn.addEventListener("click", () => {
  if (!latestDiagnostic) return;
  const blob = new Blob([`${JSON.stringify(latestDiagnostic, null, 2)}\n`], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `handshape-scan-${latestDiagnostic.createdAt.replaceAll(":", "-")}.json`;
  link.click();
  URL.revokeObjectURL(url);
});
mirror.addEventListener("change", () => stage.classList.toggle("mirrored", mirror.checked));
stage.classList.toggle("mirrored", mirror.checked);
addEventListener("pagehide", () => camera.stop());
