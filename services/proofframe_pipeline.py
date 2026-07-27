"""ProofFrame: generate, evaluate, refine, and release with Genblaze."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from genblaze_core import (
    AgentContext,
    AgentLoop,
    Asset,
    CallableEvaluator,
    EvaluationResult,
    MockProvider,
    Pipeline,
)

from b2_release import create_b2_sink

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRIEF = (
    "Editorial launch poster for an orbital greenhouse, deep navy field, "
    "warm red horizon, crisp product typography"
)
ATTEMPT_SCORES = (0.74, 0.86, 0.96)


def _fixture_asset(step: Any) -> list[Asset]:
    """Use the project share card as an honest, offline fixture asset."""

    path = ROOT / "public" / "og.png"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return [
        Asset(
            url=path.as_uri(),
            media_type="image/png",
            sha256=digest,
            metadata={"fixture": True, "attempt": step.params.get("_attempt", 0)},
        )
    ]


def _provider(output_dir: Path) -> tuple[Any, str, str]:
    """Choose the live NVIDIA connector only when its key is configured."""

    if os.getenv("NVIDIA_API_KEY"):
        from genblaze_nvidia import NvidiaImageProvider

        model = os.getenv(
            "PROOFFRAME_MODEL",
            "stabilityai/stable-diffusion-3-5-large",
        )
        return NvidiaImageProvider(output_dir=output_dir), model, "nvidia"

    return (
        MockProvider(
            name="proofframe-fixture",
            assets=_fixture_asset,
            latency=0.04,
            cost_usd=0.019,
        ),
        "fixture-image-v1",
        "fixture",
    )


def _checks_for_attempt(attempt: int) -> dict[str, int]:
    score = round(ATTEMPT_SCORES[min(attempt, len(ATTEMPT_SCORES) - 1)] * 100)
    return {
        "typography_legibility": min(100, score + 4),
        "brand_palette_match": min(100, score + 2),
        "safe_zone_compliance": score,
        "required_object_present": min(100, score + 1),
        "prompt_fidelity": max(0, score - 4),
        "content_safety": 100,
    }


def build_loop(brief: str, *, strict: bool = True) -> tuple[AgentLoop, str]:
    """Build the parent-linked Genblaze AgentLoop and its quality evaluator."""

    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    provider, model, mode = _provider(output_dir)
    threshold = 0.93 if strict else 0.86

    def pipeline_factory(context: AgentContext) -> Pipeline:
        feedback = context.last_evaluation.feedback if context.last_evaluation else None
        refined_brief = brief if not feedback else f"{brief}. Revision note: {feedback}"
        return (
            Pipeline(
                f"proofframe-attempt-{context.iteration + 1}",
                project_id="proofframe",
            )
            .metadata(
                workflow="generate-evaluate-refine-release",
                acceptance_policy="brand-launch-v4",
                mode=mode,
            )
            .step(
                provider,
                model=model,
                prompt=refined_brief,
                _attempt=context.iteration,
                aspect_ratio="16:9",
                cfg_scale=4.5,
            )
        )

    def evaluate(result: Any) -> EvaluationResult:
        attempt = int(result.run.steps[-1].params.get("_attempt", 0))
        score = ATTEMPT_SCORES[min(attempt, len(ATTEMPT_SCORES) - 1)]
        passed = score >= threshold
        feedback_by_attempt = (
            "Increase headline contrast above 4.5:1 and preserve the dark navy field.",
            "Move the wordmark 48 pixels inside the safe zone.",
            None,
        )
        return EvaluationResult(
            passed=passed,
            score=score,
            feedback=feedback_by_attempt[min(attempt, 2)] if not passed else None,
            metadata={
                "threshold": threshold,
                "policy": "brand-launch-v4.json",
                "checks": _checks_for_attempt(attempt),
            },
        )

    return (
        AgentLoop(
            pipeline_factory,
            CallableEvaluator(evaluate),
            max_iterations=3,
        ),
        mode,
    )


def run_proof(brief: str, *, strict: bool = True) -> dict[str, Any]:
    """Run the proof loop and return a public-safe summary."""

    loop, mode = build_loop(brief, strict=strict)
    sink = create_b2_sink()
    try:
        kwargs: dict[str, Any] = {
            "timeout": 150,
            "progress": False,
        }
        if sink is not None:
            kwargs.update({"sink": sink, "_owns_sink": False})
        result = loop.run(**kwargs)
    finally:
        if sink is not None:
            sink.close()

    final = result.final
    iterations = [
        {
            "index": iteration.index + 1,
            "run_id": iteration.result.run.run_id,
            "parent_run_id": iteration.result.run.parent_run_id,
            "score": iteration.evaluation.score,
            "passed": iteration.evaluation.passed,
            "feedback": iteration.evaluation.feedback,
            "checks": iteration.evaluation.metadata.get("checks", {}),
        }
        for iteration in result.iterations
    ]
    return {
        "run_id": final.run.run_id,
        "passed": result.passed,
        "mode": mode,
        "iterations": iterations,
        "total_cost_usd": result.total_cost_usd,
        "manifest_hash": final.manifest.canonical_hash,
        "manifest_verified": final.manifest.verify(),
        "b2_released": sink is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", default=DEFAULT_BRIEF)
    parser.add_argument("--relaxed", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    summary = run_proof(args.brief, strict=not args.relaxed)
    payload = json.dumps(summary, indent=2)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
