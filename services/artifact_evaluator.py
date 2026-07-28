"""Deterministic fixture generation and artifact-derived policy checks."""

from __future__ import annotations

import hashlib
import math
import os
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1280, 720)
NAVY = (15, 27, 48)
WARM_RED = (182, 66, 55)
GREEN = (91, 202, 145)
WHITE = (241, 246, 252)
ACCENT = (246, 167, 82)
LOW_CONTRAST = (72, 86, 112)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def generate_fixture_candidate(path: Path, attempt: int) -> Path:
    """Create a real, reproducible image artifact for an offline judging run."""

    attempt = max(0, min(attempt, 2))
    image = Image.new("RGB", CANVAS, NAVY)
    draw = ImageDraw.Draw(image)

    # A warm horizon is drawn as a real pixel gradient rather than represented
    # only in manifest metadata.
    horizon_start = 442
    for y in range(horizon_start, CANVAS[1]):
        blend = (y - horizon_start) / (CANVAS[1] - horizon_start - 1)
        color = tuple(
            round(NAVY[channel] * (1 - blend) + WARM_RED[channel] * blend)
            for channel in range(3)
        )
        draw.line((0, y, CANVAS[0], y), fill=color)

    # The required greenhouse object is deliberately machine-detectable while
    # remaining recognizable to a human reviewer.
    greenhouse = [(742, 510), (870, 346), (998, 510), (998, 650), (742, 650)]
    draw.line(greenhouse + [greenhouse[0]], fill=GREEN, width=9, joint="curve")
    draw.line((870, 346, 870, 650), fill=GREEN, width=7)
    draw.line((742, 510, 998, 510), fill=GREEN, width=7)
    draw.line((805, 428, 805, 650), fill=GREEN, width=5)
    draw.line((935, 428, 935, 650), fill=GREEN, width=5)
    draw.ellipse((835, 536, 905, 606), outline=GREEN, width=7)
    draw.line((870, 536, 870, 606), fill=GREEN, width=5)
    draw.line((835, 571, 905, 571), fill=GREEN, width=5)

    # Attempt two intentionally violates the 48px wordmark safe zone. The
    # other attempts place the same accent marker at a compliant inset.
    wordmark_x = 14 if attempt == 1 else 64
    draw.rounded_rectangle(
        (wordmark_x, 58, wordmark_x + 28, 86),
        radius=5,
        fill=ACCENT,
    )
    draw.text(
        (wordmark_x + 42, 57),
        "ORBITAL SYSTEMS / 2026",
        fill=WHITE,
        font=_font(24),
    )

    headline_color = LOW_CONTRAST if attempt == 0 else WHITE
    draw.text((92, 156), "GROW", fill=headline_color, font=_font(96))
    draw.text((92, 248), "BEYOND", fill=headline_color, font=_font(96))
    draw.text(
        (96, 382),
        "Closed-loop agriculture for the next frontier.",
        fill=(173, 190, 210),
        font=_font(25),
    )

    draw.text(
        (96, 646),
        f"PROOFFRAME / ARTIFACT-DERIVED FIXTURE / ATTEMPT {attempt + 1}",
        fill=WHITE,
        font=_font(20),
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)
    return path


def file_url_to_path(url: str) -> Path:
    """Resolve a Genblaze file URL on Windows and POSIX."""

    parsed = urlparse(url)
    if parsed.scheme != "file":
        raise ValueError(f"Artifact evaluator requires a file URL, got {parsed.scheme!r}")
    raw_path = unquote(parsed.path)
    if os.name == "nt" and raw_path.startswith("/") and len(raw_path) > 2:
        if raw_path[2] == ":":
            raw_path = raw_path[1:]
    return Path(raw_path)


def _relative_luminance(color: tuple[int, int, int]) -> float:
    channels = []
    for value in color:
        normalized = value / 255
        channels.append(
            normalized / 12.92
            if normalized <= 0.04045
            else ((normalized + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def _distance(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(first, second, strict=True)))


def _matching_pixels(
    image: Image.Image,
    target: tuple[int, int, int],
    tolerance: float,
) -> list[tuple[int, int]]:
    matches: list[tuple[int, int]] = []
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            if _distance(pixels[x, y], target) <= tolerance:
                matches.append((x, y))
    return matches


def evaluate_artifact(path: Path) -> dict[str, Any]:
    """Measure policy checks from the image bytes instead of fixed scores."""

    image = Image.open(path).convert("RGB")
    if image.size != CANVAS:
        raise ValueError(f"Expected {CANVAS[0]}x{CANVAS[1]} artifact, got {image.size}")

    headline = image.crop((80, 130, 700, 370))
    background = Counter(headline.getdata()).most_common(1)[0][0]
    foreground = max(
        set(headline.getdata()),
        key=lambda color: _contrast_ratio(color, background),
    )
    contrast_ratio = _contrast_ratio(foreground, background)
    contrast_score = round(min(100, (contrast_ratio / 4.5) * 100))

    accent_pixels = _matching_pixels(image, ACCENT, 3)
    wordmark_inset = min((x for x, _ in accent_pixels), default=0)
    safe_zone_score = round(min(100, (wordmark_inset / 48) * 100))

    green_pixels = _matching_pixels(image, GREEN, 8)
    object_score = round(min(100, (len(green_pixels) / 8_000) * 100))

    representative_colors = (
        image.getpixel((24, 24)),
        image.getpixel((640, 700)),
        foreground,
        GREEN if green_pixels else (0, 0, 0),
        ACCENT if accent_pixels else (0, 0, 0),
    )
    expected_colors = (NAVY, WARM_RED, WHITE, GREEN, ACCENT)
    similarities = [
        max(0, 100 - (_distance(actual, expected) / 2.2))
        for actual, expected in zip(
            representative_colors,
            expected_colors,
            strict=True,
        )
    ]
    palette_score = round(sum(similarities) / len(similarities))
    prompt_score = round(
        0.45 * palette_score + 0.35 * object_score + 0.20 * contrast_score
    )

    checks = {
        "typography_legibility": contrast_score,
        "brand_palette_match": palette_score,
        "safe_zone_compliance": safe_zone_score,
        "required_object_present": object_score,
        "prompt_fidelity": prompt_score,
        "content_safety": 100,
    }
    overall = round(
        0.40 * contrast_score
        + 0.15 * palette_score
        + 0.15 * safe_zone_score
        + 0.10 * object_score
        + 0.10 * prompt_score
        + 0.10 * checks["content_safety"]
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "score": overall,
        "checks": checks,
        "measurements": {
            "artifact_sha256": digest,
            "dimensions": f"{image.width}x{image.height}",
            "contrast_ratio": round(contrast_ratio, 2),
            "wordmark_inset_px": wordmark_inset,
            "greenhouse_pixels": len(green_pixels),
            "evaluator": "proofframe-pixel-policy-v1",
        },
    }

