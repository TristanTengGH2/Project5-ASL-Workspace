// "How to sign" reference. Shows one representative PopSign hand-landmark animation per
// supported sign (no video, no face) plus verified facts from ASL-LEX. See spec.md
// ("How to sign" reference) for scope and attribution.

import { drawBodyScene, drawHandScene, FINGERS, sceneExtent, type ReferenceMotion } from "./reference-draw";

interface SignReference extends ReferenceMotion { gloss: string; provenance?: "popsign" | "recorded" }
interface ReferenceFile { frames: number; attribution: string; recordedAttribution?: string; signs: Record<string, SignReference> }
interface SignFacts {
  hands: "one" | "two" | "varies";
  signType: string | null;
  majorLocation: string | null;
  minorLocation: string | null;
  movement: string | null;
  repeated: string | null;
  handshape: string | null;
  nonDominantHandshape: string | null;
}
interface FactsFile {
  source: { name: string; citation: string; license: string; note: string };
  signs: Record<string, SignFacts>;
}

const FRAMES_PER_SECOND = 16;

// Plain-language labels for the ASL-LEX codes the app shows.
const LOCATION_WORDS: Record<string, string> = {
  Head: "head", Body: "body", Neutral: "in front of the body", Hand: "the other hand", Arm: "arm",
  Eye: "near the eye", Forehead: "forehead", CheekNose: "cheek or nose", Chin: "chin", Mouth: "mouth",
  HeadAway: "beside the head", TorsoTop: "upper chest", Other: "elsewhere",
};
const MOVEMENT_WORDS: Record<string, string> = {
  Straight: "straight", Curved: "curved", Circular: "circular", None: "no path movement", Other: "other",
};

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const titleCase = (text: string) => `${text[0].toUpperCase()}${text.slice(1)}`;
const handshapeLabel = (code: string) => code.replaceAll("_", " ");

export class SignGuide {
  private dialog = $<HTMLDialogElement>("sign-guide");
  private list = $("guide-list");
  private title = $("guide-sign");
  private body = $<HTMLCanvasElement>("guide-canvas");
  private closeup = $<HTMLCanvasElement>("guide-closeup");
  private steps = ["guide-step-start", "guide-step-middle", "guide-step-end"].map((id) => $<HTMLCanvasElement>(id));
  private playButton = $<HTMLButtonElement>("guide-play");
  private scrubber = $<HTMLInputElement>("guide-frame");
  private facts = $("guide-facts");
  private caption = $("guide-caption");
  private attribution = $("guide-attribution");
  private data: ReferenceFile | null = null;
  private factData: FactsFile | null = null;
  private selected = "";
  private frame = 0;
  private playing = false;
  private lastTick = 0;
  private animationId = 0;
  private reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

  constructor(private mirrored: () => boolean) {
    $("guide-close").addEventListener("click", () => this.dialog.close());
    this.dialog.addEventListener("close", () => this.pause());
    this.playButton.addEventListener("click", () => (this.playing ? this.pause() : this.play()));
    this.scrubber.addEventListener("input", () => {
      this.pause();
      this.frame = Number(this.scrubber.value);
      this.draw();
    });
    $("guide-legend").replaceChildren(...FINGERS.map((finger) => {
      const item = document.createElement("span");
      item.textContent = finger.name;
      item.style.color = finger.color;
      return item;
    }));
  }

  async open(signId?: string): Promise<void> {
    if (!this.data) {
      try {
        const base = import.meta.env.BASE_URL;
        const [references, facts] = await Promise.all([
          fetch(`${base}data/sign-references.json`).then((response) => response.json() as Promise<ReferenceFile>),
          fetch(`${base}data/sign-facts.json`).then((response) => response.json() as Promise<FactsFile>),
        ]);
        this.data = references;
        this.factData = facts;
      } catch (error) {
        this.caption.textContent = `The sign references could not be loaded (${(error as Error).message}).`;
        this.dialog.showModal();
        return;
      }
      this.buildList();
    }
    this.dialog.showModal();
    this.select(signId && this.data.signs[signId] ? signId : this.selected || Object.keys(this.data.signs)[0]);
  }

  private buildList(): void {
    this.list.replaceChildren(...Object.entries(this.data!.signs).map(([id, sign]) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = sign.gloss;
      button.dataset.signId = id;
      button.addEventListener("click", () => this.select(id));
      item.append(button);
      return item;
    }));
  }

  private select(signId: string): void {
    this.selected = signId;
    const sign = this.data!.signs[signId];
    this.title.textContent = titleCase(sign.gloss);
    this.body.setAttribute("aria-label", `Animated hand position for the sign ${sign.gloss}`);
    this.closeup.setAttribute("aria-label", `Close-up of the hand shape for the sign ${sign.gloss}`);
    this.renderFacts(this.factData!.signs[signId], Boolean(sign.otherFrames));
    const origin = sign.provenance === "recorded" ? this.data!.recordedAttribution ?? "Recorded for this app; only hand landmarks are kept." : this.data!.attribution;
    this.attribution.textContent = `${origin} Sign details: ${this.factData!.source.name} (${this.factData!.source.citation}), ${this.factData!.source.license}. ${this.factData!.source.note}`;
    this.list.querySelectorAll("button").forEach((button) => {
      button.setAttribute("aria-current", String(button.dataset.signId === signId));
    });
    this.scrubber.max = String(this.data!.frames - 1);
    this.frame = this.reducedMotion.matches ? Math.floor(this.data!.frames / 2) : 0;
    this.scrubber.value = String(this.frame);
    if (this.reducedMotion.matches) { this.pause(); this.draw(); } else this.play();
  }

  /** Verified facts first; the animation caption states what the animation does not show. */
  private renderFacts(facts: SignFacts | undefined, showsOtherHand: boolean): void {
    const rows: Array<[string, string]> = [];
    if (facts) {
      const hands = { one: "One hand", two: "Two hands", varies: "Forms differ: some use one hand, some two" }[facts.hands];
      rows.push(["Hands", hands]);
      if (facts.majorLocation) {
        const place = LOCATION_WORDS[facts.majorLocation] ?? facts.majorLocation.toLowerCase();
        const detail = facts.minorLocation && facts.minorLocation !== facts.majorLocation ? LOCATION_WORDS[facts.minorLocation] ?? facts.minorLocation.toLowerCase() : "";
        rows.push(["Starts at", detail && detail !== place ? `${place} (${detail})` : place]);
      }
      if (facts.movement) {
        const repeats = facts.repeated === "1" ? ", repeated" : facts.repeated === "0" ? ", not repeated" : "";
        rows.push(["Movement", `${MOVEMENT_WORDS[facts.movement] ?? facts.movement.toLowerCase()}${repeats}`]);
      }
      if (facts.handshape) {
        const other = facts.hands === "two" && facts.nonDominantHandshape && facts.nonDominantHandshape !== "NA" ? `; other hand: ${handshapeLabel(facts.nonDominantHandshape)}` : "";
        rows.push(["Handshape", `${handshapeLabel(facts.handshape)}${other}`]);
      }
    }
    this.facts.replaceChildren(...rows.flatMap(([term, value]) => {
      const dt = document.createElement("dt");
      dt.textContent = term;
      const dd = document.createElement("dd");
      dd.textContent = titleCase(value);
      return [dt, dd];
    }));
    const twoHanded = facts?.hands !== "one";
    this.caption.textContent = showsOtherHand
      ? "The solid hand is the signing hand. The faded hand is the other hand."
      : twoHanded
      ? "This sign uses two hands. The example was recorded with one hand, so only the signing hand is drawn and the other hand is not shown. Sign it with both hands; the app reads your signing hand."
      : "This animation shows the signing hand as tracked in one PopSign example.";
  }

  private play(): void {
    this.playing = true;
    this.playButton.textContent = "Pause";
    this.lastTick = performance.now();
    cancelAnimationFrame(this.animationId);
    const step = (now: number) => {
      if (!this.playing) return;
      if (now - this.lastTick >= 1000 / FRAMES_PER_SECOND) {
        this.lastTick = now;
        this.frame = (this.frame + 1) % this.data!.frames;
        this.scrubber.value = String(this.frame);
        this.draw();
      }
      this.animationId = requestAnimationFrame(step);
    };
    this.animationId = requestAnimationFrame(step);
  }

  private pause(): void {
    this.playing = false;
    cancelAnimationFrame(this.animationId);
    this.playButton.textContent = "Play";
    if (this.data && this.selected) this.draw();
  }

  private draw(): void {
    const motion = this.data!.signs[this.selected];
    drawBodyScene(this.body, motion, this.frame, this.mirrored());
    const extent = sceneExtent(motion);
    drawHandScene(this.closeup, motion, this.frame, this.mirrored(), extent);
    const last = motion.frames.length - 1;
    [0, Math.floor(last / 2), last].forEach((index, position) => drawHandScene(this.steps[position], motion, index, this.mirrored(), extent));
  }
}
