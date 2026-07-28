"""Regression tests for ProofFrame's artifact-derived fixture policy."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from artifact_evaluator import evaluate_artifact, generate_fixture_candidate


class ArtifactEvaluatorTest(unittest.TestCase):
    def test_fixture_attempts_fail_for_real_measured_reasons_then_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports = []
            for attempt in range(3):
                path = generate_fixture_candidate(root / f"{attempt}.png", attempt)
                reports.append(evaluate_artifact(path))

        first, second, third = reports
        self.assertLess(first["checks"]["typography_legibility"], 90)
        self.assertGreaterEqual(first["checks"]["safe_zone_compliance"], 90)
        self.assertGreaterEqual(second["checks"]["typography_legibility"], 90)
        self.assertLess(second["checks"]["safe_zone_compliance"], 90)
        self.assertGreaterEqual(min(third["checks"].values()), 90)
        self.assertGreater(third["score"], first["score"])
        self.assertGreater(third["score"], second["score"])
        self.assertNotEqual(
            first["measurements"]["artifact_sha256"],
            third["measurements"]["artifact_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
