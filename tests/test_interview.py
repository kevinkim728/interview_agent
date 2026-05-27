import pytest
import json
import os
from dotenv import load_dotenv

from interview_analyzer import analyze_interview

load_dotenv()

TRANSCRIPTS_PATH = os.path.join(os.path.dirname(__file__), "transcripts.jsonl")

PASS_OUTCOMES = {"Yes", "Strong Yes", "Maybe"}
FAIL_OUTCOMES = {"No", "Strong No"}


def load_transcripts():
    records = []
    with open(TRANSCRIPTS_PATH) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def get_first(records, expected_outcome):
    return next(r for r in records if r["expected_outcome"] == expected_outcome)


# ==================== TEST 1: EDGE CASES ====================

@pytest.mark.asyncio
async def test_edge_cases():
    edge_cases = [
        "",
        "Hello.",
        "INTERVIEWER: Hello! Welcome to the interview.\nCANDIDATE: Hi.\nINTERVIEWER: Thanks for coming. Goodbye!\nCANDIDATE: Bye.",
    ]
    for i, transcript in enumerate(edge_cases):
        result = await analyze_interview(transcript)
        print(f"Edge case {i + 1}: recommendation={result.recommendation} scores=({result.communication_score}, {result.engagement_score}, {result.specificity_score}, {result.qualification_score})")
        assert result.recommendation == "INSUFFICIENT_DATA", (
            f"Expected INSUFFICIENT_DATA for short transcript, got {result.recommendation!r}"
        )
        assert result.communication_score == 0.0
        assert result.engagement_score == 0.0
        assert result.specificity_score == 0.0
        assert result.qualification_score == 0.0


# ==================== TEST 2: PASS RATE ====================

@pytest.mark.asyncio
async def test_pass_rate():
    records = load_transcripts()
    mismatches = []

    all_results = []
    for record in records:
        result = await analyze_interview(record["transcript"])
        recommendation = result.recommendation

        if record["expected_outcome"] == "pass":
            matched = recommendation in PASS_OUTCOMES
        elif record["expected_outcome"] == "fail":
            matched = recommendation in FAIL_OUTCOMES
        else:
            matched = recommendation == "INSUFFICIENT_DATA"

        status = "✓" if matched else "✗"
        print(f"[{status}] id={record['id']} expected={record['expected_outcome']} got={recommendation}")
        all_results.append({"record": record, "result": result, "matched": matched})

        if not matched:
            mismatches.append({
                "id": record["id"],
                "persona": record["persona"],
                "expected": record["expected_outcome"],
                "got": recommendation,
            })

    mismatch_rate = len(mismatches) / len(records)
    print(f"\nMismatch rate: {mismatch_rate:.0%} ({len(mismatches)}/{len(records)})")

    output_path = os.path.join(os.path.dirname(__file__), "pass_rate_results.txt")
    with open(output_path, "w") as f:
        f.write("PASS RATE RESULTS\n")
        f.write("=================\n")
        f.write(f"Total: {len(records)} | Mismatches: {len(mismatches)} | Mismatch rate: {mismatch_rate:.0%}\n\n")

        for entry in all_results:
            record = entry["record"]
            result = entry["result"]
            status = "✓" if entry["matched"] else "✗"
            avg = (result.communication_score + result.engagement_score + result.specificity_score + result.qualification_score) / 4

            f.write(f"{'='*60}\n")
            f.write(f"[{status}] id={record['id']} expected={record['expected_outcome']}\n")
            f.write(f"Persona: {record['persona']}\n\n")
            f.write(f"RECOMMENDATION: {result.recommendation}\n")
            f.write(f"SCORES:\n")
            f.write(f"  communication:  {result.communication_score:.2f}\n")
            f.write(f"  engagement:     {result.engagement_score:.2f}\n")
            f.write(f"  specificity:    {result.specificity_score:.2f}\n")
            f.write(f"  qualification:  {result.qualification_score:.2f}\n")
            f.write(f"  average:        {avg:.2f}\n\n")
            f.write(f"HIGHLIGHTS:\n")
            for h in result.highlights:
                f.write(f"  • {h}\n")
            f.write(f"\nCONCERNS:\n")
            for c in result.concerns:
                f.write(f"  ⚠ {c}\n")
            f.write(f"\nRED FLAGS:\n")
            for rf in result.red_flags:
                f.write(f"  ✗ {rf}\n")
            f.write(f"\nSCORE BREAKDOWN:\n{result.score_breakdown}\n")
            f.write(f"\nSUMMARY:\n{result.summary}\n\n")

        if mismatches:
            f.write(f"\n{'='*60}\n")
            f.write("MISMATCHES\n")
            f.write("----------\n")
            for m in mismatches:
                f.write(f"id={m['id']} expected={m['expected']} got={m['got']}\n")
                f.write(f"  {m['persona']}\n\n")

    assert mismatch_rate <= 0.20, (
        f"Mismatch rate {mismatch_rate:.0%} exceeds 20% threshold. "
        f"Consider adjusting ANALYZER_PROMPT."
    )


# ==================== TEST 3: SCORE CONSISTENCY ====================

@pytest.mark.asyncio
async def test_score_consistency():
    records = load_transcripts()
    transcript = get_first(records, "pass")["transcript"]
    runs = []

    for i in range(5):
        result = await analyze_interview(transcript)
        runs.append(result)
        print(f"Run {i + 1}: communication={result.communication_score:.2f} engagement={result.engagement_score:.2f} "
              f"specificity={result.specificity_score:.2f} qualification={result.qualification_score:.2f}")

    for field in ["communication_score", "engagement_score", "specificity_score", "qualification_score"]:
        values = [getattr(r, field) for r in runs]
        spread = max(values) - min(values)
        print(f"{field} spread: {spread:.2f}")
        assert spread < 0.3, f"{field} spread of {spread:.2f} is too high — prompt may need tightening"


# ==================== TEST 4: SCORE-RECOMMENDATION ALIGNMENT ====================

@pytest.mark.asyncio
async def test_score_recommendation_alignment():
    records = load_transcripts()
    high_scoring = get_first(records, "pass")["transcript"]
    low_scoring = get_first(records, "fail")["transcript"]

    high_result = await analyze_interview(high_scoring)
    low_result = await analyze_interview(low_scoring)

    high_scores = [high_result.communication_score, high_result.engagement_score,
                   high_result.specificity_score, high_result.qualification_score]
    low_scores = [low_result.communication_score, low_result.engagement_score,
                  low_result.specificity_score, low_result.qualification_score]

    print(f"High candidate — scores: {high_scores} recommendation: {high_result.recommendation}")
    print(f"Low candidate  — scores: {low_scores} recommendation: {low_result.recommendation}")

    assert all(s >= 0.7 for s in high_scores), (
        f"Expected all scores >= 0.7 for strong candidate, got {high_scores}"
    )
    assert high_result.recommendation in ("Yes", "Strong Yes"), (
        f"Expected Yes/Strong Yes for strong candidate, got {high_result.recommendation!r}"
    )

    assert low_result.qualification_score <= 0.4, (
        f"Expected qualification_score <= 0.4 for weak candidate, got {low_result.qualification_score}"
    )
    assert low_result.recommendation not in ("Yes", "Strong Yes"), (
        f"Expected recommendation to not be a pass for weak candidate, got {low_result.recommendation!r}"
    )
