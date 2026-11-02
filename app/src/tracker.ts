// Landmark tracking: wraps MediaPipe so the rest of the app never touches it directly.
// Tracking only reports where hands/body points are; it does not recognize signs.

import {
  FilesetResolver,
  HandLandmarker,
  PoseLandmarker,
  type NormalizedLandmark,
} from "@mediapipe/tasks-vision";

export interface HandFrame {
  /** 21 landmarks, normalized to the unmirrored video frame. */
  landmarks: NormalizedLandmark[];
  /** Label as reported by the model (its left/right convention assumes a selfie-mirrored image). */
  modelLabel: string;
  score: number;
}

export interface TrackingFrame {
  hands: HandFrame[];
  pose: NormalizedLandmark[] | null;
  /** Time spent in the tracker for this frame. */
  ms: number;
}

export class Tracker {
  private hands!: HandLandmarker;
  private pose!: PoseLandmarker;

  static async create(): Promise<Tracker> {
    const t = new Tracker();
    const vision = await FilesetResolver.forVisionTasks("/wasm");
    t.hands = await HandLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: "/models/hand_landmarker.task", delegate: "GPU" },
      runningMode: "VIDEO",
      numHands: 2,
    });
    t.pose = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: "/models/pose_landmarker_lite.task", delegate: "GPU" },
      runningMode: "VIDEO",
      numPoses: 1,
    });
    return t;
  }

  /** Tracks one video frame. `timestampMs` must increase between calls. */
  track(video: HTMLVideoElement, timestampMs: number, withPose: boolean): TrackingFrame {
    const start = performance.now();
    const h = this.hands.detectForVideo(video, timestampMs);
    const hands: HandFrame[] = h.landmarks.map((landmarks, i) => ({
      landmarks,
      modelLabel: h.handedness[i]?.[0]?.categoryName ?? "unknown",
      score: h.handedness[i]?.[0]?.score ?? 0,
    }));
    const pose = withPose
      ? (this.pose.detectForVideo(video, timestampMs).landmarks[0] ?? null)
      : null;
    return { hands, pose, ms: performance.now() - start };
  }
}
