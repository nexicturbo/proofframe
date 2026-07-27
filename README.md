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
object paths, and manifest hashes.

## Local development

```bash
npm install
npm run dev
```

The app runs at `http://localhost:3000`.

## Validation

```bash
npm test
```

## Architecture

- `app/` — public ProofFrame control-room UI
- `services/proofframe_pipeline.py` — Genblaze AgentLoop and evaluator workflow
- `services/b2_release.py` — content-addressed Backblaze B2 release sink
- `.openai/hosting.json` — Sites deployment metadata

The public UI is deployed as a Cloudflare Worker-compatible vinext app. Runtime
media credentials are supplied through the deployment environment and are never
committed.
