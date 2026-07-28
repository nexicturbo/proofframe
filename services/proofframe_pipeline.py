"""ProofFrame: generate, evaluate, refine, and release with Genblaze."""

from __future__ import annotations

import argparse
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

from artifact_evaluator import (
    evaluate_artifact,
    file_url_to_path,
    generate_fixture_candidate,
)
from b2_release import create_b2_sink

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRIEF = (
    "Editorial launch poster for an orbital greenhouse, deep navy field, "
    "warm red horizon, crisp product typography"
)


def _fixture_asset(step: Any, output_dir: Path) -> list[Asset]:
    """Generate a distinct, measurable artifact for each offline attempt."""

    attempt = int(step.params.get("_attempt", 0))
    path = generate_fixture_candidate(
        output_dir / f"fixture-candidate-{attempt + 1}.png",
        attempt,
    )
    report = evaluate_artifact(path)
    return [
        Asset(
            url=path.as_uri(),
            media_type="image/png",
            sha256=report["measurements"]["artifact_sha256"],
            metadata={
                "fixture": True,
                "attempt": attempt,
                "evaluator": report["measurements"]["evaluator"],
            },
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
            assets=lambda step: _fixture_asset(step, output_dir),
            latency=0.04,
            cost_usd=0.019,
        ),
        "fixture-image-v1",
        "fixture",
    )


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
        asset = result.run.steps[-1].assets[0]
        report = evaluate_artifact(file_url_to_path(asset.url))
        checks = report["checks"]
        score = report["score"] / 100
        required_floor = 90 if strict else 80
        passed = score >= threshold and min(checks.values()) >= required_floor
        failures: list[str] = []
        if checks["typography_legibility"] < required_floor:
            failures.append("Increase headline contrast above 4.5:1.")
        if checks["safe_zone_compliance"] < required_floor:
            failures.append("Move the wordmark at least 48 pixels inside the safe zone.")
        if checks["required_object_present"] < required_floor:
            failures.append("Make the greenhouse structure more visually explicit.")
        feedback = " ".join(failures) if failures else None
        return EvaluationResult(
            passed=passed,
            score=score,
            feedback=feedback if not passed else None,
            metadata={
                "threshold": threshold,
                "policy": "brand-launch-v4.json",
                "checks": checks,
                "measurements": report["measurements"],
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
            "measurements": iteration.evaluation.metadata.get("measurements", {}),
        }
        for iteration in result.iterations
    ]
    return {
        "run_id": final.run.run_id,
        "passed": result.passed,
        "mode": mode,
        "iterations": iterations,
        "total_cost_usd": round(result.total_cost_usd, 6),
        "manifest_hash": final.manifest.canonical_hash,
        "manifest_verified": final.manifest.verify(),
        "b2_released": sink is not None,
        "release": {
            "storage": "Backblaze B2",
            "status": "uploaded" if sink is not None else "fixture_not_uploaded",
            "key_strategy": "content-addressable",
        },
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
