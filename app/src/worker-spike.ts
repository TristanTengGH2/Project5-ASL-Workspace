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
let animationId = 0;
let busy = false;
let nextId = 1;
let lastVideoTime = -1;
let recent: Array<{ time: number; ms: number }> = [];

function setStatus(message: string): void {
  status.textContent = message;
}

function draw(result: HandResult): void {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (const landmarks of result.landmarks) {
    drawing.drawConnectors(landmarks, HandLandmarker.HAND_CONNECTIONS, { color: "#f7c948", lineWidth: 4 });
    drawing.drawLandmarks(landmarks, { color: "#e8756a", radius: 5 });
  }

  const now = performance.now();
  recent.push({ time: now, ms: result.ms });
  recent = recent.filter((item) => now - item.time < 1000);
  get("fps").textContent = String(recent.length);
  get("latency").textContent = (recent.reduce((sum, item) => sum + item.ms, 0) / recent.length).toFixed(1);
  get("hands").textContent =
    result.handedness.map((hand) => `${hand.label} (${hand.score.toFixed(2)})`).join(", ") || "none";
  setStatus(result.landmarks.length ? "Hand tracking active." : "Worker active; no hands detected.");
}

function loop(): void {
  animationId = requestAnimationFrame(loop);
  if (!worker || busy || video.readyState < 2 || video.currentTime === lastVideoTime) return;
  busy = true;
  lastVideoTime = video.currentTime;
  const id = nextId++;
  void createImageBitmap(video)
    .then((bitmap) => worker?.postMessage({ type: "track", id, bitmap, timestampMs: video.currentTime * 1000 }, [bitmap]))
    .catch((error: unknown) => {
      busy = false;
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
      busy = false;
      draw(event.data.result);
    } else if (event.data.type === "error") {
      busy = false;
      setStatus(`Worker failed: ${event.data.message}`);
    }
  };

  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  video.srcObject = stream;
  await video.play();
  toggle.disabled = false;
  toggle.textContent = "Stop test";
  setStatus("Worker active; waiting for a camera frame…");
  loop();
}

function stop(): void {
  cancelAnimationFrame(animationId);
  stream?.getTracks().forEach((track) => track.stop());
  stream = null;
  video.srcObject = null;
  worker?.terminate();
  worker = null;
  busy = false;
  recent = [];
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
