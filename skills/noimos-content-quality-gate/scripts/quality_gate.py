#!/usr/bin/env python3
"""Block unsupported, generic, off-brand, or unapproved AI content."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


GENERIC_PHRASES = [
    "重要です",
    "様々な",
    "多岐にわた",
    "革新的",
    "画期的",
    "ゲームチェンジャー",
    "今こそ",
    "未来を切り拓",
    "ビジネスを変革",
    "シームレス",
    "効果的に活用",
]
PLACEHOLDER_PATTERNS = [r"\bTODO\b", r"\bTBD\b", r"\[ここに", r"\[INSERT", r"〇〇"]
NUMERIC_CLAIM = re.compile(
    r"(?<!CLAIM:)(?:\d[\d,.]*\s*(?:%|％|円|万円|億円|ドル|倍|件|人|日|時間|分|社|位))"
)
CLAIM_TAG = re.compile(r"\[CLAIM:([A-Za-z0-9_-]+)\]")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--claims", required=True)
    parser.add_argument("--brand", required=True)
    parser.add_argument("--approval", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    content = Path(args.content).read_text(encoding="utf-8")
    claim_payload = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    claims = claim_payload.get("claims", claim_payload if isinstance(claim_payload, list) else [])
    brand = json.loads(Path(args.brand).read_text(encoding="utf-8"))
    approval = json.loads(Path(args.approval).read_text(encoding="utf-8"))
    claim_map = {str(item.get("id")): item for item in claims}
    blockers = []
    warnings = []
    evidence = []

    tagged_ids = CLAIM_TAG.findall(content)
    missing_records = sorted({claim_id for claim_id in tagged_ids if claim_id not in claim_map})
    if missing_records:
        blockers.append({"code": "claim_record_missing", "detail": missing_records})

    invalid_records = []
    for claim_id in sorted(set(tagged_ids)):
        item = claim_map.get(claim_id)
        if not item:
            continue
        required = ["claim", "source_url", "publisher", "retrieved_at", "evidence_type", "verified"]
        missing = [key for key in required if item.get(key) in (None, "", [])]
        if missing or item.get("verified") is not True:
            invalid_records.append({"id": claim_id, "missing": missing, "verified": item.get("verified")})
    if invalid_records:
        blockers.append({"code": "claim_record_invalid", "detail": invalid_records})

    lines = content.splitlines()
    untagged_numeric = []
    for index, line in enumerate(lines, start=1):
        if NUMERIC_CLAIM.search(line) and not CLAIM_TAG.search(line):
            untagged_numeric.append({"line": index, "text": line[:180]})
    if untagged_numeric:
        blockers.append({"code": "untagged_numeric_claim", "detail": untagged_numeric})

    generic_hits = {
        phrase: len(re.findall(re.escape(phrase), content, re.I))
        for phrase in GENERIC_PHRASES
        if re.search(re.escape(phrase), content, re.I)
    }
    if sum(generic_hits.values()) > max(2, len(content) // 1500):
        blockers.append({"code": "generic_phrase_density", "detail": generic_hits})
    elif generic_hits:
        warnings.append({"code": "generic_phrases", "detail": generic_hits})

    placeholders = [pattern for pattern in PLACEHOLDER_PATTERNS if re.search(pattern, content, re.I)]
    if placeholders:
        blockers.append({"code": "placeholders", "detail": placeholders})

    prohibited = [
        phrase for phrase in brand.get("prohibited_claims", [])
        if phrase and phrase.lower() in content.lower()
    ]
    if prohibited:
        blockers.append({"code": "prohibited_claims", "detail": prohibited})

    audience_terms = [term for term in brand.get("audience_terms", []) if term]
    if audience_terms and not any(term.lower() in content.lower() for term in audience_terms):
        blockers.append({"code": "audience_not_explicit", "detail": audience_terms})

    cta_terms = [term for term in brand.get("cta_terms", []) if term]
    if cta_terms and not any(term.lower() in content.lower() for term in cta_terms):
        blockers.append({"code": "approved_cta_missing", "detail": cta_terms})

    concrete_markers = len(re.findall(r"(手順|比較|条件|注意|失敗|例|チェック|判断|まず|次に)", content))
    if concrete_markers < 4:
        blockers.append({"code": "insufficient_specificity", "detail": concrete_markers})

    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    duplicates = [p for p in set(paragraphs) if len(p) >= 60 and paragraphs.count(p) > 1]
    if duplicates:
        blockers.append({"code": "duplicate_paragraphs", "detail": [p[:140] for p in duplicates]})

    approval_mode = approval.get("mode", "human")
    if approval_mode == "ai_only":
        required_ai_checks = [
            "claim_evidence",
            "brand_alignment",
            "specificity",
            "risk_screen",
            "render_qa",
        ]
        ai_checks = approval.get("checks", {})
        missing_ai_checks = [name for name in required_ai_checks if ai_checks.get(name) is not True]
        approved = (
            approval.get("status") == "ai_approved"
            and bool(approval.get("pipeline"))
            and bool(approval.get("reviewed_at"))
            and not missing_ai_checks
        )
        if not approved:
            blockers.append(
                {
                    "code": "ai_approval_incomplete",
                    "detail": {"missing_checks": missing_ai_checks, "approval": approval},
                }
            )
    else:
        approved = (
            approval.get("status") == "approved"
            and bool(approval.get("reviewer"))
            and bool(approval.get("reviewed_at"))
        )
        if not approved:
            blockers.append({"code": "human_approval_missing", "detail": approval})

    referenced_claims = sorted(set(tagged_ids))
    unused_claims = sorted(set(claim_map) - set(referenced_claims))
    if unused_claims:
        warnings.append({"code": "unused_claim_records", "detail": unused_claims})
    evidence.append(
        {
            "registered_claims_used": len(referenced_claims),
            "claim_records": len(claim_map),
            "numeric_claim_lines": len(untagged_numeric) + len(referenced_claims),
            "approval_mode": approval_mode,
            "approval_complete": approved,
        }
    )

    status = "BLOCK" if blockers else "PASS_WITH_WARNINGS" if warnings else "PASS"
    report = {
        "tool": "noimos-content-quality-gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "evidence": evidence,
        "approval_mode": approval_mode,
        "reviewer": approval.get("reviewer"),
        "pipeline": approval.get("pipeline"),
        "publication_performed": False,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "blockers": len(blockers), "warnings": len(warnings)}, ensure_ascii=False))
    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
