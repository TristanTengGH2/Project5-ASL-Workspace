// ASL-LEX facts per supported sign (hands, location, movement, handshape) and the look-alike rule
// built on them. Pure data code with one fetch, shared by the tutorial and the results panel.

export interface SignFacts {
  hands: "one" | "two" | "varies";
  signType: string | null;
  majorLocation: string | null;
  minorLocation: string | null;
  movement: string | null;
  repeated: string | null;
  handshape: string | null;
  nonDominantHandshape: string | null;
}
export interface FactsFile {
  source: { name: string; citation: string; license: string; note: string };
  signs: Record<string, SignFacts>;
}

let cached: Promise<FactsFile> | null = null;

export function loadSignFacts(): Promise<FactsFile> {
  cached ??= fetch(`${import.meta.env.BASE_URL}data/sign-facts.json`).then((response) => {
    if (!response.ok) throw new Error(`sign facts HTTP ${response.status}`);
    return response.json() as Promise<FactsFile>;
  });
  return cached;
}

// Two signs look alike to this app when ASL-LEX codes them the same on every field below. The
// recognizer sees only the signing hand's shape, position and movement, so it cannot reliably
// separate signs that match here (book and boat were confused 3 times in 5 test clips).
const MATCHING_FIELDS = ["hands", "majorLocation", "minorLocation", "movement", "repeated", "handshape", "nonDominantHandshape"] as const;

export function lookAlike(a: SignFacts | undefined, b: SignFacts | undefined): boolean {
  if (!a || !b || a.hands === "varies") return false;
  // A field ASL-LEX leaves out (its forms disagree) can never count as a match.
  return MATCHING_FIELDS.every((field) => a[field] !== null && a[field] === b[field]);
}

export function lookAlikesOf(id: string, signs: Record<string, SignFacts>): string[] {
  return Object.keys(signs).filter((other) => other !== id && lookAlike(signs[id], signs[other]));
}

/** A sentence for the results panel when two shown candidates look alike; otherwise null. */
export function lookAlikeMessage(candidates: Array<{ id: string; label: string }>, signs: Record<string, SignFacts>): string | null {
  for (let first = 0; first < candidates.length; first += 1) {
    for (let second = first + 1; second < candidates.length; second += 1) {
      if (lookAlike(signs[candidates[first].id], signs[candidates[second].id])) {
        return `${candidates[first].label} and ${candidates[second].label} look alike to this app: ASL-LEX codes them the same way and the one-hand examples it learned from are nearly identical, so it cannot reliably tell them apart. Compare them in How to sign.`;
      }
    }
  }
  return null;
}
