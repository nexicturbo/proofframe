# ProofFrame

**Generate until it passes. Prove every pixel.**

## Inspiration

Generative media is easy to create and hard to trust in production. Teams still
review outputs in chat threads, lose the prompt history behind a final asset,
and cannot prove which candidate passed which brand or safety rule. ProofFrame
treats generation as a controlled release process rather than a one-shot
prompt.

## What it does

ProofFrame accepts a creative brief plus an explicit acceptance policy. A
Genblaze `AgentLoop` generates a candidate, evaluates it, feeds structured
failures into the next prompt, and retries until the artifact passes or the
iteration budget is exhausted.

Every attempt remains visible. The dashboard compares candidates, rejection
reasons, per-check scores, latency, and cost. The accepted asset, evaluator
report, and canonical Genblaze manifest are committed to Backblaze B2 with
content-addressed keys. Reviewers can verify the final SHA-256 and walk the
parent-linked lineage back to the original run.

## How we built it

- **Genblaze Core** — pipeline execution, `AgentLoop`, structured evaluator,
  parent-linked runs, and canonical manifest verification
- **Genblaze NVIDIA connector** — live image generation through NVIDIA NIM
  when a runtime key is present
- **Genblaze S3 connector** — `S3StorageBackend.for_backblaze` and
  `ObjectStorageSink`
- **Backblaze B2** — durable evidence storage with content-addressed object
  paths for assets and manifests
- **ProofFrame UI** — a responsive TypeScript control room deployed as a
  Cloudflare Worker-compatible app

The repository includes an honest fixture mode for local demos without
credentials. Fixture runs are labeled and never claim a B2 upload. Live mode is
enabled only when the NVIDIA and B2 runtime credentials are present.

## Challenges

The main challenge was preserving useful evidence across retries. A final image
alone is not enough: the failed candidates, evaluator feedback, parent run IDs,
and policy version must survive as one inspectable chain. ProofFrame keeps those
artifacts together while promoting only the passing output to the release path.

We also separated generated-media provenance from deployment concerns. Secrets
never enter the repository, and the public dashboard remains demonstrable even
when a reviewer does not have provider credentials.

## Accomplishments

- A quality-gated generation loop that actually refines and retries
- Six explicit policy checks instead of an opaque “looks good” score
- Parent-linked Genblaze manifests for every candidate
- SHA-256 verification and content-addressed B2 object layout
- A public control room that makes the system understandable in under a minute
- A deterministic offline fixture path that is clearly distinguished from live
  provider and B2 execution

## What we learned

Provenance becomes much more useful when it participates in the workflow rather
than being attached at the end. The evaluator feedback is both a quality signal
and the reason the next manifest exists. Backblaze B2 is a natural fit because
immutable, content-addressed artifacts turn the lineage into durable evidence
instead of transient application state.

## What's next

- Add organization policy packs and signed approvals
- Run multiple providers in parallel and select the best passing candidate
- Add perceptual hashing for near-duplicate detection
- Expose a CI gate for generated campaign assets
- Add webhook notifications when a release is promoted or verification fails

## Links

- Source: https://github.com/nexicturbo/proofframe
- Live app: https://proofframe-control.nexicturbo.chatgpt.site
- Demo video: https://drive.google.com/file/d/1zeL22feKA4hRFm0riEujAn7SmyHQk4Gf/view?usp=sharing
