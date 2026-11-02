// Camera capture: owns the MediaStream and its lifecycle.

export type CameraError = "permission-denied" | "no-camera" | "failed";

export class Camera {
  private stream: MediaStream | null = null;

  constructor(private video: HTMLVideoElement) {}

  get running(): boolean {
    return this.stream !== null;
  }

  /** Starts the camera. Resolves to null on success, or a reason code. */
  async start(): Promise<CameraError | null> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
        audio: false, // microphone stays off
      });
    } catch (err) {
      const name = (err as DOMException).name;
      if (name === "NotAllowedError" || name === "SecurityError") return "permission-denied";
      if (name === "NotFoundError" || name === "OverconstrainedError") return "no-camera";
      return "failed";
    }
    this.video.srcObject = this.stream;
    await this.video.play();
    return null;
  }

  /** Releases the camera hardware. */
  stop(): void {
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.video.srcObject = null;
  }
}
