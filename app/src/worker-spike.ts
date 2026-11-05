import { DrawingUtils, HandLandmarker, type NormalizedLandmark } from "@mediapipe/tasks-vision";

type HandResult = {
  landmarks: NormalizedLandmark[][];
  handedness: Array<{ label: string; score: number }>;
  ms: number;
};

type WorkerResponse =
  | { type: "ready" }
  | { type: "result"; id: number; result: HandResult }
  | { type: "error"; id?: number; message: string };

const get = <T extends HTMLElement>(id: string): T => document.getElementById(id) as T;
const video = get<HTMLVideoElement>("video");
const canvas = get<HTMLCanvasElement>("canvas");
const context = canvas.getContext("2d")!;
const drawing = new DrawingUtils(context);
const toggle = get<HTMLButtonElement>("toggle");
const status = get("status");

let worker: Worker | null = null;
let stream: MediaStream | null = null;
let videoCallbackId = 0;
let busy = false;
let nextId = 1;
let skippedFrames = 0;
let completedFrames = 0;
let pendingTiming: {
  id: number;
  frameTime: number;
  submittedAt: number;
  bitmapReadyAt?: number;
  hasCaptureTime: boolean;
} | null = null;

type TimingSample = {
  time: number;
  inferenceMs: number;
  frameToResultMs: number;
  submitToResultMs: number;
  bitmapMs: number;
};

let samples: TimingSample[] = [];

function setStatus(message: string): void {
  status.textContent = message;
}

function average(values: number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function percentile(values: number[], fraction: number): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil(sorted.length * fraction) - 1)];
}

function showTiming(sample: TimingSample, hasCaptureTime: boolean): void {
  samples.push(sample);
  samples = samples.filter((item) => sample.time - item.time < 30_000);
  const recentResults = samples.filter((item) => sample.time - item.time < 1000);
  const frameTimes = samples.map((item) => item.frameToResultMs);
  const consideredFrames = completedFrames + skippedFrames;
  const skippedPercent = consideredFrames ? (skippedFrames / consideredFrames) * 100 : 0;

  get("fps").textContent = String(recentResults.length);
  get("latency").textContent = average(samples.map((item) => item.inferenceMs)).toFixed(1);
  get("frame-latency").textContent = average(frameTimes).toFixed(1);
  get("frame-p95").textContent = percentile(frameTimes, 0.95).toFixed(1);
  get("round-trip").textContent = average(samples.map((item) => item.submitToResultMs)).toFixed(1);
  get("bitmap-time").textContent = average(samples.map((item) => item.bitmapMs)).toFixed(1);
  get("skipped").textContent = `${skippedFrames} (${skippedPercent.toFixed(1)}%)`;
  get("timing-source").textContent = hasCaptureTime
    ? "Rolling 30-second timing window; frame latency starts at the camera capture timestamp."
    : "Rolling 30-second timing window; capture timestamp unavailable, so frame latency starts at browser receipt.";
}

function draw(result: HandResult, timing: TimingSample, hasCaptureTime: boolean): void {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (const landmarks of result.landmarks) {
    drawing.drawConnectors(landmarks, HandLandmarker.HAND_CONNECTIONS, { color: "#f7c948", lineWidth: 4 });
    drawing.drawLandmarks(landmarks, { color: "#e8756a", radius: 5 });
  }

  showTiming(timing, hasCaptureTime);
  get("hands").textContent =
    result.handedness.map((hand) => `${hand.label} (${hand.score.toFixed(2)})`).join(", ") || "none";
  setStatus(result.landmarks.length ? "Hand tracking active." : "Worker active; no hands detected.");
}

function processVideoFrame(now: number, metadata: VideoFrameCallbackMetadata): void {
  if (stream) videoCallbackId = video.requestVideoFrameCallback(processVideoFrame);
  if (!worker || video.readyState < 2) return;
  if (busy) {
    skippedFrames += 1;
    return;
  }

  busy = true;
  const id = nextId++;
  const submittedAt = performance.now();
  pendingTiming = {
    id,
    frameTime: metadata.captureTime ?? metadata.receiveTime ?? now,
    submittedAt,
    hasCaptureTime: metadata.captureTime !== undefined,
  };
  void createImageBitmap(video)
    .then((bitmap) => {
      if (!worker || pendingTiming?.id !== id) {
        bitmap.close();
        busy = false;
        return;
      }
      pendingTiming.bitmapReadyAt = performance.now();
      // MediaPipe requires strictly increasing timestamps. Camera metadata is
      // retained for latency measurement only because it may arrive a tick late.
      worker.postMessage({ type: "track", id, bitmap, timestampMs: submittedAt }, [bitmap]);
    })
    .catch((error: unknown) => {
      busy = false;
      pendingTiming = null;
      setStatus(`Frame transfer failed: ${error instanceof Error ? error.message : String(error)}`);
    });
}

async function start(): Promise<void> {
  toggle.disabled = true;
  setStatus("Loading hand tracker in worker…");
  worker = new Worker(new URL("./hand-worker-spike.worker.ts", import.meta.url), { type: "module" });

  await new Promise<void>((resolve, reject) => {
    const onMessage = (event: MessageEvent<WorkerResponse>): void => {
      if (event.data.type === "ready") resolve();
      else if (event.data.type === "error") reject(new Error(event.data.message));
    };
    worker!.addEventListener("message", onMessage, { once: false });
    worker!.addEventListener("error", (event) => reject(new Error(event.message)), { once: true });
    worker!.postMessage({ type: "initialize" });
  });

  worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
    if (event.data.type === "result") {
      const receivedAt = performance.now();
      const timing = pendingTiming?.id === event.data.id ? pendingTiming : null;
      busy = false;
      pendingTiming = null;
      completedFrames += 1;
      const submittedAt = timing?.submittedAt ?? receivedAt;
      const bitmapReadyAt = timing?.bitmapReadyAt ?? submittedAt;
      draw(
        event.data.result,
        {
          time: receivedAt,
          inferenceMs: event.data.result.ms,
          frameToResultMs: Math.max(0, receivedAt - (timing?.frameTime ?? submittedAt)),
          submitToResultMs: Math.max(0, receivedAt - submittedAt),
          bitmapMs: Math.max(0, bitmapReadyAt - submittedAt),
        },
        timing?.hasCaptureTime ?? false,
      );
    } else if (event.data.type === "error") {
      busy = false;
      pendingTiming = null;
      setStatus(`Worker failed: ${event.data.message}`);
    }
  };

  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  video.srcObject = stream;
  await video.play();
  toggle.disabled = false;
  toggle.textContent = "Stop test";
  setStatus("Worker active; waiting for a camera frame…");
  videoCallbackId = video.requestVideoFrameCallback(processVideoFrame);
}

function stop(): void {
  if (videoCallbackId) video.cancelVideoFrameCallback(videoCallbackId);
  stream?.getTracks().forEach((track) => track.stop());
  stream = null;
  video.srcObject = null;
  worker?.terminate();
  worker = null;
  busy = false;
  videoCallbackId = 0;
  skippedFrames = 0;
  completedFrames = 0;
  pendingTiming = null;
  samples = [];
  context.clearRect(0, 0, canvas.width, canvas.height);
  toggle.textContent = "Start test";
  setStatus("Worker is off.");
}

toggle.addEventListener("click", () => {
  if (stream) stop();
  else void start().catch((error: unknown) => {
    worker?.terminate();
    worker = null;
    toggle.disabled = false;
    setStatus(`Test failed: ${error instanceof Error ? error.message : String(error)}`);
  });
});

addEventListener("pagehide", stop);
