import json
from typing import Dict, Any, Tuple, List

# A human-readable judge prompt (if you wanted to call an LLM to judge).
# Parameters considered while writing this prompt:
# - Compare presence/absence of expected missing_fields by 'name' (primary signal)
# - Compare evidence_span and required_information for partial credit
# - Provide scalar score in [0.0,1.0] and textual reasoning
JUDGE_PROMPT = """
Compare two JSON objects (expected and predicted) with the schema:
{ missing_fields: [...], summary: string, remediation_steps: [...] }.

Return a JSON object with keys:
 - score: float 0.0-1.0 (higher is better)
 - pass: boolean (True if score >= 0.8)
 - details: list of comparisons explaining matches/mismatches for each expected missing_field

Scoring rules (used by the automated judge):
 - Match on missing_field 'name' -> +0.6 per item
 - Partial match on evidence_span or required_information -> +0.2 per item
 - summary / remediation alignment -> up to +0.2 total
Normalize by the maximum possible points.
"""

def _get_names(j: Dict[str, Any]) -> List[str]:
    return [f.get("name", "").lower() for f in j.get("missing_fields", [])]

def judge_compare(predicted: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic judge that returns score, pass, and details."""
    exp_names = _get_names(expected)
    pred_names = _get_names(predicted)

    max_points = len(exp_names) * 1.0 + 0.2  # 1.0 per expected item (0.6+0.2) + 0.2 for summary/remediation.
    points = 0.0
    details = []

    for name in exp_names:
        item_detail = {"name": name, "matched_name": False, "evidence_partial": False, "points": 0.0}
        if name in pred_names:
            item_detail["matched_name"] = True
            item_detail["points"] += 0.6
            # check evidence substring overlap as simple heuristic
            # find expected evidence
            exp_item = next((it for it in expected["missing_fields"] if it["name"].lower() == name), None)
            pred_item = next((it for it in predicted.get("missing_fields", []) if it["name"].lower() == name), None)
            if exp_item and pred_item:
                exp_e = (exp_item.get("evidence_span") or "").lower()
                pred_e = (pred_item.get("evidence_span") or "").lower()
                if exp_e and pred_e and (exp_e in pred_e or pred_e in exp_e):
                    item_detail["evidence_partial"] = True
                    item_detail["points"] += 0.2
        details.append(item_detail)
        points += item_detail["points"]

    # summary/remediation simple check
    summary_bonus = 0.0
    if expected.get("summary") and predicted.get("summary"):
        if expected["summary"].split()[0:3] == predicted["summary"].split()[0:3]:
            summary_bonus = 0.2
        else:
            # small credit if they share any word
            if set(expected["summary"].split()) & set(predicted["summary"].split()):
                summary_bonus = 0.1
    points += summary_bonus

    score = min(1.0, points / max_points) if max_points > 0 else 1.0
    passed = score >= 0.8

    return {"score": score, "pass": passed, "points": points, "max_points": max_points, "details": details}