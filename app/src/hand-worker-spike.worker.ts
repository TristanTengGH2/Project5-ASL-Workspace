import { FilesetResolver, HandLandmarker, type NormalizedLandmark } from "@mediapipe/tasks-vision";

type Request =
  | { type: "initialize" }
  | { type: "track"; id: number; bitmap: ImageBitmap; timestampMs: number };

type HandResult = {
  landmarks: NormalizedLandmark[][];
  handedness: Array<{ label: string; score: number }>;
  ms: number;
};

type Response =
  | { type: "ready" }
  | { type: "result"; id: number; result: HandResult }
  | { type: "error"; id?: number; message: string };

let landmarker: HandLandmarker;

function send(response: Response): void {
  postMessage(response);
}

async function initialize(): Promise<void> {
  const wasmBase = new URL("/wasm", self.location.origin).href.replace(/\/$/, "");
  const fileset = await FilesetResolver.forVisionTasks(wasmBase, true);

  // MediaPipe's current module-worker sample gives the loader a query string.
  // This keeps Vite from treating the public runtime as a source import.
  fileset.wasmLoaderPath = `${fileset.wasmLoaderPath}?worker-module=1`;

  const modelResponse = await fetch("/models/hand_landmarker.task");
  if (!modelResponse.ok) throw new Error(`Hand model request failed (${modelResponse.status}).`);
  const modelBuffer = await modelResponse.arrayBuffer();

  landmarker = await HandLandmarker.createFromOptions(fileset, {
    baseOptions: { modelAssetBuffer: new Uint8Array(modelBuffer), delegate: "GPU" },
    runningMode: "VIDEO",
    numHands: 2,
  });
}

function track(bitmap: ImageBitmap, timestampMs: number): HandResult {
  const start = performance.now();
  try {
    const result = landmarker.detectForVideo(bitmap, timestampMs);
    return {
      landmarks: result.landmarks,
      handedness: result.handedness.map((categories) => ({
        label: categories[0]?.categoryName ?? "unknown",
        score: categories[0]?.score ?? 0,
      })),
      ms: performance.now() - start,
    };
  } finally {
    bitmap.close();
  }
}

addEventListener("message", (event: MessageEvent<Request>) => {
  const request = event.data;
  if (request.type === "initialize") {
    void initialize()
      .then(() => send({ type: "ready" }))
      .catch((error: unknown) =>
        send({ type: "error", message: error instanceof Error ? error.message : String(error) }),
      );
    return;
  }

  try {
    send({ type: "result", id: request.id, result: track(request.bitmap, request.timestampMs) });
  } catch (error) {
    send({
      type: "error",
      id: request.id,
      message: error instanceof Error ? error.message : String(error),
    });
  }
});
