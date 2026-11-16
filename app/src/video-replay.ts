// Dev-only harness: replays a video file through the same browser tracker, preprocessing and
// model the live app uses, so accuracy can be measured without a webcam. It is not part of
// the production build (see vite.config.ts inputs). Driven by scripts/replay-videos.mjs.
import { Tracker, type TrackingFrame } from "./tracker";
import { Recognizer, type RankedCandidate } from "./recognizer";
import { frameFeatures, prepareSequenceDetailed, type FeatureFrame, type SequenceDiagnostics } from "./preprocessing";

export interface ReplayResult {
  url: string;
  error?: string;
  trackedFrames: number;
  meanTrackerMs: number;
  videoSize: [number, number];
  ranking?: RankedCandidate[];
  diagnostics?: SequenceDiagnostics;
}

declare global {
  interface Window { replayClip: (url: string, fps: number) => Promise<ReplayResult>; replayReady: boolean }
}

const status = document.getElementById("status")!;
// Headless Chrome has no GPU, so the replay uses the CPU delegate (live app default is GPU).
const tracker = await Tracker.create("CPU");
// MediaPipe needs strictly increasing timestamps across every clip.
let trackerClockMs = 1000;
const recognizer = await Recognizer.create();

/** Feeds blank frames so the tracker's frame-to-frame state does not leak between clips. */
function resetTracker(): void {
  const blank = document.createElement("canvas");
  blank.width = 256;
  blank.height = 256;
  for (let index = 0; index < 4; index += 1) {
    trackerClockMs += 33;
    tracker.track(blank as unknown as HTMLVideoElement, trackerClockMs, true);
  }
}

/**
 * Steps through the clip one source frame at a time. Real-time playback would drop frames
 * whenever tracking is slower than the video, so results would depend on the machine; stepping
 * is deterministic. It processes every frame, which is a little more than the live app does.
 */
async function replayClip(url: string, fps: number): Promise<ReplayResult> {
  resetTracker();
  const video = document.createElement("video");
  video.muted = true;
  video.playsInline = true;
  video.crossOrigin = "anonymous";
  video.preload = "auto";
  video.src = url;
  const result: ReplayResult = { url, trackedFrames: 0, meanTrackerMs: 0, videoSize: [0, 0] };
  try {
    await new Promise<void>((resolve, reject) => {
      video.onloadeddata = () => resolve();
      video.onerror = () => reject(new Error("video failed to load"));
    });
    result.videoSize = [video.videoWidth, video.videoHeight];
    const frames: FeatureFrame[] = [];
    let latestPose: TrackingFrame["pose"] = null;
    let trackerMs = 0;
    const frameCount = Math.floor(video.duration * fps);
    for (let index = 0; index < frameCount; index += 1) {
      const seeked = new Promise<void>((resolve) => { video.onseeked = () => resolve(); });
      video.currentTime = (index + 0.5) / fps;
      await seeked;
      trackerClockMs += 33;
      // Same cadence rule as main.ts: pose on the first frame, then every third frame.
      const tracked = tracker.track(video, trackerClockMs, latestPose === null || index % 3 === 2);
      if (tracked.pose) latestPose = tracked.pose;
      trackerMs += tracked.ms;
      frames.push({ timestampMs: (index / fps) * 1000, features: frameFeatures({ ...tracked, pose: latestPose }) });
    }
    result.trackedFrames = frames.length;
    result.meanTrackerMs = frames.length ? trackerMs / frames.length : 0;
    const prepared = prepareSequenceDetailed(frames);
    result.diagnostics = prepared.diagnostics;
    result.ranking = await recognizer.rank(prepared.tensor);
  } catch (error) {
    result.error = (error as Error).message;
  } finally {
    video.removeAttribute("src");
    video.load();
  }
  return result;
}

window.replayClip = replayClip;
window.replayReady = true;
status.textContent = "Replay harness ready.";
