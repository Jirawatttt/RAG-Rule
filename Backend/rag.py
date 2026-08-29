"""Database-backed retrieval and matching for the rights RAG flow."""

from __future__ import annotations

import re
from math import sqrt
from dataclasses import dataclass
from typing import Any

import database
import llm
from models import Benefit, UserProfile


def _value(profile: UserProfile, field: str) -> Any:
    # The HTTP form calls this field "disability" while UserProfile keeps a
    # boolean named has_disability_card.  Normalise it at the RAG boundary.
    if field == "disability":
        if profile.has_disability_card is None:
            return None
        return "yes" if profile.has_disability_card else "no"
    value = getattr(profile, field, None)
    return value.value if hasattr(value, "value") else value


def _matches(value: Any, operator: str, expected: Any) -> bool:
    if operator == "eq": return value == expected
    if operator == "gte": return value >= expected
    if operator == "between": return expected[0] <= value <= expected[1]
    if operator == "in": return value in expected
    if operator == "not_in": return value not in expected
    return False


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\wก-๙]+", text.lower()))


def _profile_query(profile: UserProfile) -> str:
    values = []
    if profile.age is not None: values.append(f"อายุ {profile.age} ปี")
    if profile.nationality is not None: values.append("สัญชาติไทย" if profile.nationality.value == "thai" else "ไม่ใช่สัญชาติไทย")
    if profile.social_security is not None: values.append(f"ประกันสังคม {profile.social_security.value}")
    if profile.employment is not None: values.append(f"สถานะงาน {profile.employment.value}")
    if profile.children is not None: values.append(f"สถานะบุตร {profile.children.value}")
    return ", ".join(values)


def _cosine(left: list[float], right: list[float]) -> float:
    denominator = sqrt(sum(x * x for x in left)) * sqrt(sum(x * x for x in right))
    return sum(x * y for x, y in zip(left, right)) / denominator if denominator else 0.0


async def _rank_documents(profile: UserProfile, documents: list[database.BenefitDocument]) -> list[str]:
    """Vector retrieval with a deterministic fallback when the API is unavailable."""
    query = _profile_query(profile)
    query_tokens = _tokens(query)
    try:
        query_embedding = await llm.embed_text(query)
        scores = []
        for document in documents:
            embedding = document.embedding
            if embedding is None:
                embedding = await llm.embed_text(document.content)
                await database.save_document_embedding(document.id, embedding)
            scores.append((document, _cosine(query_embedding, embedding)))
        ranked = [document for document, _ in sorted(scores, key=lambda item: item[1], reverse=True)]
    except Exception:
        # The structured DB match still works if a key is absent or temporarily
        # rate-limited; only semantic retrieval falls back to keyword ranking.
        ranked = sorted(documents, key=lambda d: len(query_tokens & _tokens(d.content)), reverse=True)
    return [d.content for d in ranked[:3]]


async def match_profile(profile: UserProfile) -> list[Benefit]:
    """Metadata filter → retrieve evidence → create UI-compatible benefit cards."""
    catalogue = await database.load_rag_catalogue()
    benefits: list[Benefit] = []

    for item in catalogue:
        matched, missing, rejected = [], [], False
        for condition in item.conditions:
            if condition.operator == "manual" or not condition.field_name:
                missing.append(condition.label)
                continue
            value = _value(profile, condition.field_name)
            if value is None:
                missing.append(condition.label)
            elif _matches(value, condition.operator, condition.expected_value):
                matched.append(condition.label)
            else:
                rejected = True
                break

        # Metadata pre-filter: never retrieve documents for a known mismatch.
        if rejected or not matched:
            continue

        evidence = await _rank_documents(profile, item.documents)
        benefits.append(Benefit(
            name=item.name,
            matched_conditions=matched,
            missing_conditions=missing,
            docs=item.docs,
            contact=item.contact,
            link=item.link,
            detail="\n".join(evidence),
        ))
    return benefits
