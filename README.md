# ProofFrame

Generate until it passes. Prove every pixel.

ProofFrame is a control plane for production generative media. It turns a
creative brief and a machine-readable acceptance policy into an auditable
Genblaze run:

1. Generate a candidate.
2. Evaluate it against explicit quality and brand checks.
3. Feed structured failures back into the next prompt.
4. Promote only the passing artifact.
5. Store candidates, evaluator reports, and a canonical manifest in Backblaze
   B2 using content-addressed object keys.

The web dashboard makes the complete lineage reviewable: candidate scores,
rejection reasons, runtime and cost, parent-linked retries, policy results,
object paths, and manifest hashes. The offline judging path generates three
distinct PNGs and derives every policy score from the resulting bytes: WCAG
contrast, wordmark inset, palette similarity, greenhouse pixels, dimensions,
and SHA-256. No fixture score is hard-coded.

## Local development

```bash
npm install
npm run dev
```

The app runs at `http://localhost:3000`.

## Validation

```bash
npm ci
npm test

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m unittest discover -s services -p "test_*.py"
python services/proofframe_pipeline.py
```

The Python command runs the complete three-attempt Genblaze loop in clearly
labeled fixture mode when provider and B2 credentials are absent. Attempt one
fails a measured 2.33:1 contrast ratio, attempt two fails a measured 14px safe
zone, and attempt three passes all six checks. It verifies the parent-linked
manifest chain and reports `b2_released: false` rather than pretending that an
upload occurred.

## Live Backblaze B2 release

The reference run `d9918cc2-f90e-429f-b163-f2c23ae3388a` completed the same
three-attempt loop with the B2 sink enabled. It uploaded the three
content-addressed PNGs and their parent-linked canonical manifests to the
private evidence bucket `proofframe-genblaze-turbonexic-2026` in
`us-east-005`. The final asset is stored at:

```text
proofframe/assets/d1/fa/d1fa1ce0176d5acb9829d894d7a51e82a58b4f69c9ad17aaf7d64712a5f80d21.png
```

The final canonical manifest is stored at:

```text
proofframe/manifests/d9918cc2-f90e-429f-b163-f2c23ae3388a.json
```

The public dashboard exposes the release summary, exact object keys, SHA-256
values, and byte-identical review mirrors without exposing B2 credentials.

## Architecture

- `app/` — public ProofFrame control-room UI
- `services/proofframe_pipeline.py` — Genblaze AgentLoop and evaluator workflow
- `services/artifact_evaluator.py` — deterministic fixtures and pixel policy
- `services/b2_release.py` — content-addressed Backblaze B2 release sink
- `.openai/hosting.json` — Sites deployment metadata

The public UI is deployed as a Cloudflare Worker-compatible vinext app. The
Python worker receives optional NVIDIA and Backblaze B2 credentials through its
runtime environment; credentials are never committed. Without those values,
the worker and dashboard remain usable in visibly labeled fixture mode. The
checked-in reference manifest records a real B2 release while keeping the
private bucket and scoped application key out of the client bundle.
