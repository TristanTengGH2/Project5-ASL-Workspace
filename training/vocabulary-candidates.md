# Vocabulary candidate review v1

This is a provisional 25-sign review list for Phase 2, not signing instruction
and not an approved supported vocabulary. Selection hypotheses must be checked
against original PopSign videos, archive counts, extracted-landmark quality,
and an ASL-qualified reviewer before entries become `candidate` or `supported`
in the project catalog.

PopSign v1.0 deliberately emphasizes one-handed smartphone signing. This list
therefore tests handshape, orientation, movement, and broad body-relative
location, but it cannot demonstrate the project's later two-hand or non-manual
facial-expression goals.

| Source slug | Selection hypothesis | Main channel to test | Review risk |
|---|---|---|---|
| `after` | Broad directional motion in neutral/chest space | Movement | Fast motion produced missing landmarks in the first sample |
| `airplane` | Distinct handshape plus travel | Handshape/movement | Confirm intended variant |
| `apple` | Compact motion near the side of the face | Face-relative location | Face occlusion may lower hand detection |
| `black` | Lateral motion near the forehead | Forehead-relative location | Compare with other forehead signs |
| `cat` | Face-side articulation | Handshape/location | Compare with other cheek-area signs |
| `drink` | Clear hand-to-mouth path | Mouth-relative location | Near-face tracking quality |
| `elephant` | Longer movement beginning near the face | Movement/location | Motion may leave the comfortable frame |
| `eye` | Small, localized eye-area sign | Fine location | Pointing-like unsupported gestures may be similar |
| `finish` | Strong orientation change | Palm orientation | Fast turn may blur |
| `flower` | Repeated nose-side location | Location/repetition | Compare with other face signs |
| `food` | Repeated movement toward the mouth | Repetition/location | Compare with `drink` after extraction |
| `hair` | Head-relative location | Location | Hair/background can occlude fingers |
| `hear` | Ear-relative location | Location/handshape | Low hand detection in some sampled clips |
| `hello` | Forehead-to-neutral movement | Movement/location | May resemble ordinary waving |
| `home` | Multi-location face path | Temporal location | Near-face tracking quality |
| `man` | Larger face-to-torso path | Body-relative movement | Verify complete path remains framed |
| `milk` | Repeated handshape change | Handshape/repetition | Static frames may resemble a fist |
| `no` | Small finger articulation | Fine handshape/movement | Demands reliable fingertip tracking |
| `pen` | Fine handshape and compact motion | Fine handshape | Small differences may be lost at webcam resolution |
| `please` | Circular chest-relative motion | Movement/location | Verify one-handed PopSign variant |
| `puppy` | Lower signing-space location | Body-relative location | Hips or hand may be outside webcam framing |
| `thankyou` | Chin-to-neutral directional path | Movement/location | Compare with other chin-origin signs |
| `think` | Forehead-relative endpoint | Handshape/location | Static pointing-like gestures may be similar |
| `water` | Chin-side handshape | Handshape/location | Requires stable finger configuration |
| `yes` | Repeated wrist/fist movement | Repetition/orientation | Static frames may resemble a fist |

## Evidence still required

- Count train, validation, and test archive members for every candidate.
- Confirm distinct signer IDs remain separated by the official splits.
- Inspect at least three signer examples per candidate with skeleton overlays.
- Record dominant-hand normalization and variants rather than assuming one
  English gloss maps to one universal ASL form.
- Remove pairs the v1 landmark features cannot distinguish responsibly.
