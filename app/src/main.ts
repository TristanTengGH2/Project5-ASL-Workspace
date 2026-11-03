import { Camera } from "./camera";
import { Tracker } from "./tracker";
import { Overlay } from "./overlay";
import type { TrackingFrame } from "./tracker";

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const video = $<HTMLVideoElement>("video");
const stage = $("stage");
const toggleBtn = $<HTMLButtonElement>("toggle-camera");
const mirror = $<HTMLInputElement>("mirror");
const usePose = $<HTMLInputElement>("use-pose");
const showLabels = $<HTMLInputElement>("show-labels");
const statusEl = $("status");

const camera = new Camera(video);
const overlay = new Overlay($<HTMLCanvasElement>("overlay"));
let tracker: Tracker | null = null;
let loopId = 0;

// Rolling stats over the last second of processed frames.
let recent: { t: number; ms: number }[] = [];
// Hands are "lost" (not just absent) if they were seen within this window.
const LOST_WINDOW_MS = 2000;
let lastHandsSeen = -Infinity;
// Skip display frames that carry no new camera frame (screens refresh faster than cameras).
let lastVideoTime = -1;

function setStatus(text: string): void {
  statusEl.textContent = text;
}

function handsState(frame: TrackingFrame, now: number): string {
  const n = frame.hands.length;
  if (n === 2) return "Both hands tracked.";
  if (n === 1) return "One hand tracked (partial tracking: show both hands if the sign uses two).";
  return now - lastHandsSeen < LOST_WINDOW_MS ? "Tracking lost: hands left the frame or are hidden." : "No hands detected.";
}

function loop(): void {
  loopId = requestAnimationFrame(loop);
  if (!tracker || video.readyState < 2 || video.currentTime === lastVideoTime) return;
  lastVideoTime = video.currentTime;
  const now = performance.now();
  const frame = tracker.track(video, now, usePose.checked);
  if (frame.hands.length) lastHandsSeen = now;

  recent.push({ t: now, ms: frame.ms });
  recent = recent.filter((r) => now - r.t < 1000);
  $("fps").textContent = String(recent.length);
  $("latency").textContent = (recent.reduce((s, r) => s + r.ms, 0) / recent.length).toFixed(1);
  $("hands").textContent =
    frame.hands.map((h) => `${h.modelLabel} (${h.score.toFixed(2)})`).join(", ") || "none";

  overlay.render(frame, video.videoWidth, video.videoHeight, {
    showLabels: showLabels.checked,
    mirrored: mirror.checked,
  });
  setStatus(handsState(frame, now));
}

async function startCamera(): Promise<void> {
  toggleBtn.disabled = true;
  setStatus("Loading tracking models…");
  try {
    tracker ??= await Tracker.create();
  } catch (err) {
    setStatus(`Tracking models failed to load: ${(err as Error).message}`);
    toggleBtn.disabled = false;
    return;
  }
  setStatus("Starting camera…");
  const error = await camera.start();
  toggleBtn.disabled = false;
  if (error) {
    setStatus(
      error === "permission-denied"
        ? "Camera permission denied. Allow camera access in your browser settings and try again."
        : error === "no-camera"
          ? "No camera found."
          : "The camera could not be started.",
    );
    return;
  }
  toggleBtn.textContent = "Stop camera";
  document.body.classList.add("camera-running");
  lastHandsSeen = -Infinity;
  lastVideoTime = -1;
  loop();
}

function stopCamera(): void {
  cancelAnimationFrame(loopId);
  camera.stop();
  overlay.render(null, video.videoWidth, video.videoHeight);
  recent = [];
  toggleBtn.textContent = "Start camera";
  document.body.classList.remove("camera-running");
  setStatus("Camera is off.");
}

toggleBtn.addEventListener("click", () => (camera.running ? stopCamera() : void startCamera()));
mirror.addEventListener("change", () => stage.classList.toggle("mirrored", mirror.checked));
stage.classList.toggle("mirrored", mirror.checked);
// Release the camera if the user leaves the page.
addEventListener("pagehide", () => camera.stop());
