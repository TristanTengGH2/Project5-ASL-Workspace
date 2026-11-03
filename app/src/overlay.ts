// Draws tracking results on a canvas that matches the video's pixel size.
// Mirroring is handled by CSS on the parent, so drawing always uses raw coordinates.

import { DrawingUtils, HandLandmarker, PoseLandmarker } from "@mediapipe/tasks-vision";
import type { TrackingFrame } from "./tracker";
import { HAND_LANDMARK_NAMES, POSE_ANCHOR_NAMES } from "./landmarks";

interface OverlayOptions {
  showLabels: boolean;
  mirrored: boolean;
}

export class Overlay {
  private ctx: CanvasRenderingContext2D;
  private draw: DrawingUtils;

  constructor(private canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext("2d")!;
    this.draw = new DrawingUtils(this.ctx);
  }

  render(
    frame: TrackingFrame | null,
    videoWidth: number,
    videoHeight: number,
    options: OverlayOptions = { showLabels: false, mirrored: false },
  ): void {
    if (this.canvas.width !== videoWidth) this.canvas.width = videoWidth;
    if (this.canvas.height !== videoHeight) this.canvas.height = videoHeight;
    this.ctx.clearRect(0, 0, videoWidth, videoHeight);
    if (!frame) return;

    if (frame.pose) {
      this.draw.drawConnectors(frame.pose, PoseLandmarker.POSE_CONNECTIONS, { color: "#4a5a6a", lineWidth: 2 });
      this.draw.drawLandmarks(frame.pose, { color: "#4a5a6a", radius: 3 });
      if (options.showLabels) {
        for (const [index, name] of POSE_ANCHOR_NAMES) {
          const landmark = frame.pose[index];
          if (landmark) this.drawLabel(name, landmark.x * videoWidth, landmark.y * videoHeight, options.mirrored);
        }
      }
    }
    for (const hand of frame.hands) {
      this.draw.drawConnectors(hand.landmarks, HandLandmarker.HAND_CONNECTIONS, { color: "#152c42", lineWidth: 4 });
      this.draw.drawLandmarks(hand.landmarks, { color: "#e8756a", radius: 5 });
      this.drawHandBox(
        hand.landmarks,
        videoWidth,
        videoHeight,
        hand.modelLabel,
        options.mirrored,
      );
      if (options.showLabels) {
        hand.landmarks.forEach((landmark, index) => {
          const name = HAND_LANDMARK_NAMES[index];
          if (name) this.drawLabel(name, landmark.x * videoWidth, landmark.y * videoHeight, options.mirrored);
        });
      }
    }
  }

  private drawHandBox(
    landmarks: TrackingFrame["hands"][number]["landmarks"],
    width: number,
    height: number,
    handedness: string,
    mirrored: boolean,
  ): void {
    if (!landmarks.length) return;
    const xs = landmarks.map((landmark) => landmark.x * width);
    const ys = landmarks.map((landmark) => landmark.y * height);
    const padding = Math.max(8, Math.min(width, height) * 0.025);
    const left = Math.max(0, Math.min(...xs) - padding);
    const top = Math.max(0, Math.min(...ys) - padding);
    const right = Math.min(width, Math.max(...xs) + padding);
    const bottom = Math.min(height, Math.max(...ys) + padding);

    this.ctx.save();
    this.ctx.strokeStyle = "#f7c948";
    this.ctx.lineWidth = 3;
    this.ctx.setLineDash([10, 6]);
    this.ctx.strokeRect(left, top, right - left, bottom - top);
    this.ctx.restore();

    this.drawBoxLabel(handedness, mirrored ? right : left, top, mirrored);
  }

  private drawBoxLabel(text: string, x: number, y: number, mirrored: boolean): void {
    const label = text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
    this.ctx.save();
    this.ctx.translate(x, y);
    if (mirrored) this.ctx.scale(-1, 1);
    this.ctx.font = "600 16px system-ui, sans-serif";
    this.ctx.textBaseline = "top";
    const width = this.ctx.measureText(label).width;
    this.ctx.fillStyle = "#f7c948";
    this.ctx.fillRect(0, 0, width + 16, 26);
    this.ctx.fillStyle = "#0b1722";
    this.ctx.fillText(label, 8, 3);
    this.ctx.restore();
  }

  private drawLabel(text: string, x: number, y: number, mirrored: boolean): void {
    this.ctx.save();
    this.ctx.translate(x + 7, y - 7);
    if (mirrored) this.ctx.scale(-1, 1);
    this.ctx.font = "12px system-ui, sans-serif";
    this.ctx.textBaseline = "bottom";
    const width = this.ctx.measureText(text).width;
    this.ctx.fillStyle = "rgba(11, 23, 34, 0.82)";
    this.ctx.fillRect(-3, -16, width + 6, 18);
    this.ctx.fillStyle = "#ffffff";
    this.ctx.fillText(text, 0, 0);
    this.ctx.restore();
  }
}
