"""Regression coverage for ProofFrame's live-release output policy."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from proofframe_pipeline import (
    DEFAULT_BRIEF,
    ROOT,
    _fixture_asset,
    build_loop,
    run_proof,
)


class PipelineReleaseTests(unittest.TestCase):
    def test_fixture_preserves_byte_derived_report_for_post_upload_evaluation(
        self,
    ) -> None:
        class Step:
            params = {"_attempt": 0}

        with tempfile.TemporaryDirectory() as temp_dir:
            asset = _fixture_asset(Step(), Path(temp_dir))[0]

        report = asset.metadata["evaluation_report"]
        self.assertEqual(report["score"], 76)
        self.assertEqual(report["measurements"]["contrast_ratio"], 2.33)
        self.assertEqual(report["measurements"]["artifact_sha256"], asset.sha256)

    def test_offline_loop_keeps_repository_output_directory(self) -> None:
        loop, mode = build_loop(DEFAULT_BRIEF)

        self.assertEqual(mode, "fixture")
        self.assertTrue((ROOT / "output").is_dir())
        self.assertIsNotNone(loop)

    @patch("proofframe_pipeline.create_b2_sink")
    @patch("proofframe_pipeline.build_loop")
    def test_live_release_uses_genblaze_allowed_temp_root(
        self,
        build_loop_mock,
        create_sink_mock,
    ) -> None:
        class FakeSink:
            def close(self) -> None:
                return None

        class FakeLoop:
            def run(self, **_kwargs):
                raise RuntimeError("stop after output-directory selection")

        create_sink_mock.return_value = FakeSink()
        build_loop_mock.return_value = (FakeLoop(), "fixture")

        with self.assertRaisesRegex(RuntimeError, "stop after"):
            run_proof(DEFAULT_BRIEF)

        output_dir = build_loop_mock.call_args.kwargs["output_dir"].resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        self.assertTrue(output_dir.is_relative_to(temp_root))


if __name__ == "__main__":
    unittest.main()
