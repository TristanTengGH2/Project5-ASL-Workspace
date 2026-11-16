import type { TrackingFrame } from "./tracker";
import { frameFeatures, prepareSequence, prepareSequenceDetailed, shouldersReady, type FeatureFrame, type SequenceDiagnostics } from "./preprocessing";

export type CaptureState = "idle" | "waiting" | "countdown" | "capturing" | "processing";

export class CaptureController {
  state: CaptureState = "idle";
  private readySince = 0;
  private countdownStarted = 0;
  private captureStarted = 0;
  private lastPreview = 0;
  private frames: FeatureFrame[] = [];

  constructor(
    private onStatus: (message: string) => void,
    private onSequence: (sequence: Float32Array, diagnostics: SequenceDiagnostics) => Promise<void>,
    private onIdle: () => void,
    private onPreview: (sequence: Float32Array) => void = () => undefined,
  ) {}

  get active(): boolean { return this.state !== "idle"; }

  start(): void {
    this.state = "waiting";
    this.readySince = 0;
    this.frames = [];
    this.onStatus("Get ready: keep your upper body and signing hand visible.");
  }

  cancel(): void {
    this.state = "idle";
    this.frames = [];
    this.onIdle();
  }

  consume(frame: TrackingFrame, timestampMs: number): void {
    if (this.state === "idle" || this.state === "processing") return;
    const ready = frame.hands.length > 0 && shouldersReady(frame.pose);
    if (this.state === "waiting") {
      if (!ready) {
        this.readySince = 0;
        this.onStatus(frame.hands.length ? "Move back until your shoulders are visible." : "Show at least one hand to begin.");
        return;
      }
      this.readySince ||= timestampMs;
      if (timestampMs - this.readySince >= 500) {
        this.state = "countdown";
        this.countdownStarted = timestampMs;
      }
      return;
    }
    if (this.state === "countdown") {
      if (!ready) {
        this.state = "waiting";
        this.readySince = 0;
        return;
      }
      const remaining = Math.max(1, 3 - Math.floor((timestampMs - this.countdownStarted) / 1000));
      this.onStatus(`Scan begins in ${remaining}…`);
      if (timestampMs - this.countdownStarted >= 3000) {
        this.state = "capturing";
        this.captureStarted = timestampMs;
        this.lastPreview = timestampMs;
        this.frames = [];
        this.onStatus("Signing now… capture stops automatically.");
      }
      return;
    }
    this.frames.push({ timestampMs, features: frameFeatures(frame) });
    const elapsed = timestampMs - this.captureStarted;
    this.onStatus(`Signing now… ${(elapsed / 1000).toFixed(1)} / 3.0 seconds.`);
    if (elapsed >= 700 && timestampMs - this.lastPreview >= 500) {
      this.lastPreview = timestampMs;
      try { this.onPreview(prepareSequence(this.frames)); }
      catch { /* Wait for a usable dominant-hand interval. */ }
    }
    if (elapsed < 3000) return;
    this.state = "processing";
    this.onStatus("Finding possible matches…");
    try {
      const prepared = prepareSequenceDetailed(this.frames);
      void this.onSequence(prepared.tensor, prepared.diagnostics).finally(() => {
        this.state = "idle";
        this.onIdle();
      });
    } catch (error) {
      this.onStatus(`${(error as Error).message} Try again for clarity.`);
      this.state = "idle";
      this.onIdle();
    }
  }
}
