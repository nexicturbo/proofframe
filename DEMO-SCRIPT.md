# ProofFrame demo script (about 2:30)

## 0:00–0:20 — The problem

“Generative media is easy to create, but production teams still cannot answer
three basic questions: Why was this version chosen? Which rules did it pass?
And can we verify the exact bytes later? ProofFrame is the reliability control
plane for that gap.”

## 0:20–0:50 — Define the proof

Show the creative brief and `brand-launch-v4.json`.

“Instead of asking for an image and hoping it looks right, I define the evidence
required for release: contrast, palette distance, required object, safe zones,
prompt fidelity, and safety.”

Click **Run proof**.

## 0:50–1:25 — Generate, evaluate, refine

Cycle through Frames 01, 02, and 03.

“Genblaze runs the agent loop. The first candidate scores 74 and fails
contrast. That feedback becomes part of the next prompt. The second scores 86
but clips the logo safe zone. The third reaches 96 and passes all six checks.
Nothing is hidden: failed candidates remain available for review.”

## 1:25–1:55 — Lineage

Scroll to the lineage rail and evaluator report.

“Each attempt is a parent-linked Genblaze run. The final decision is explainable
because the evaluator report, feedback, model parameters, cost, and latency stay
attached to the lineage.”

## 1:55–2:20 — Backblaze B2 evidence

Open the release manifest.

“ProofFrame stores generated assets and canonical manifests on Backblaze B2
using content-addressed keys. The final SHA-256 points to the exact released
bytes, while every rejected candidate remains auditable. If a file changes,
verification fails.”

## 2:20–2:30 — Close

“ProofFrame turns one-shot generation into a production release system:
generate until it passes, and prove every pixel.”
