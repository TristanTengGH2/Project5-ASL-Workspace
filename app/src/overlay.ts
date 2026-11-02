// Draws tracking results on a canvas that matches the video's pixel size.
// Mirroring is handled by CSS on the parent, so drawing always uses raw coordinates.

import { DrawingUtils, HandLandmarker, PoseLandmarker } from "@mediapipe/tasks-vision";
import type { TrackingFrame } from "./tracker";

export class Overlay {
  private ctx: CanvasRenderingContext2D;
  private draw: DrawingUtils;

  constructor(private canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext("2d")!;
    this.draw = new DrawingUtils(this.ctx);
  }

  render(frame: TrackingFrame | null, videoWidth: number, videoHeight: number): void {
    if (this.canvas.width !== videoWidth) this.canvas.width = videoWidth;
    if (this.canvas.height !== videoHeight) this.canvas.height = videoHeight;
    this.ctx.clearRect(0, 0, videoWidth, videoHeight);
    if (!frame) return;

    if (frame.pose) {
      this.draw.drawConnectors(frame.pose, PoseLandmarker.POSE_CONNECTIONS, { color: "#4a5a6a", lineWidth: 2 });
      this.draw.drawLandmarks(frame.pose, { color: "#4a5a6a", radius: 3 });
    }
    for (const hand of frame.hands) {
      this.draw.drawConnectors(hand.landmarks, HandLandmarker.HAND_CONNECTIONS, { color: "#152c42", lineWidth: 4 });
      this.draw.drawLandmarks(hand.landmarks, { color: "#e8756a", radius: 5 });
    }
  }
}
