"""Benchmark script for TruthLens AI.

Runs the real analysis pipeline on a set of canonical
misinformation test claims and prints verdicts, confidence
and source stance breakdown.

Usage:
    cd backend
    python3 benchmark_claims.py

This uses the same services as the /api/analyze endpoint
and does not mock retrieval or evidence.
"""

import asyncio
import logging
from typing import List, Dict

from api.analyze import _initialize_services, analyze_claim  # type: ignore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark")


TEST_CLAIMS: List[Dict[str, str]] = [
    {"claim": "Barack Obama is dead", "expected": "FALSE"},
    {"claim": "The Moon is made of cheese", "expected": "FALSE"},
    {"claim": "The Earth is flat", "expected": "FALSE"},
    {"claim": "The Earth is round", "expected": "TRUE"},
    {"claim": "The Sun orbits around the Earth", "expected": "FALSE"},
]


async def run_benchmarks() -> None:
    ok = _initialize_services()
    if not ok:
        logger.error("Failed to initialize services; aborting benchmarks")
        return

    print("\n=== TruthLens Benchmark Claims ===\n")

    for item in TEST_CLAIMS:
        claim = item["claim"]
        expected = item["expected"]

        print(f"CLAIM: {claim}")
        print(f"EXPECTED: {expected}")

        try:
            result = await analyze_claim(claim)
        except Exception as exc:  # pragma: no cover - runtime-only harness
            print(f"  ERROR running analysis: {exc}")
            print("---\n")
            continue

        verdict = result.verdict
        confidence = result.confidence

        # Count supporting vs refuting sources from the response
        support_count = sum(1 for s in result.sources if s.supports == "SUPPORTS")
        refute_count = sum(1 for s in result.sources if s.supports == "REFUTES")
        neutral_count = sum(1 for s in result.sources if s.supports == "NEUTRAL")

        status = "OK" if expected and verdict == expected else "MISMATCH"

        print(f"  VERDICT: {verdict} (conf={confidence:.2f}) [{status}]")
        print(f"  Sources: total={len(result.sources)}, SUPPORTS={support_count}, REFUTES={refute_count}, NEUTRAL={neutral_count}")

        # Show top 3 sources for quick inspection
        for src in result.sources[:3]:
            print(
                f"    - {src.title[:60]:60s} | {src.supports:8s} | {src.credibility} | {src.url[:80]}"
            )

        print("---\n")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
