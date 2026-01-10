from __future__ import annotations

# ==============================
# Context Pack Merge
# ==============================
"""
Deterministic merge of user-provided answers into a ContextPack.
"""

from typing import Dict, Any, List

from core.contracts.context_pack_schema import ContextPack, UserProvidedInfo
from core.contracts.question_schema import QuestionSet, UserAnswers
from core.knowledge.context_pack import compute_context_pack_hash


def merge_answers_into_context_pack(
    context_pack: ContextPack,
    question_set: QuestionSet,
    answers: UserAnswers,
) -> ContextPack:
    ordered_answers = _ordered_answers(answers.answers)
    user_info = UserProvidedInfo(
        question_set_id=question_set.id,
        created_from=question_set.provenance.created_from,
        evidence_refs=sorted(question_set.provenance.evidence_refs),
        answers=ordered_answers,
    )
    assumptions = list(context_pack.assumptions or [])
    marker = f"user_answers_merged:{question_set.id}"
    if marker not in assumptions:
        assumptions.append(marker)
    updated = context_pack.model_copy(update={"user_provided": user_info, "assumptions": assumptions})
    pack_hash = compute_context_pack_hash(updated)
    return updated.model_copy(update={"pack_hash": pack_hash})


def _ordered_answers(values: Dict[str, Any]) -> Dict[str, Any]:
    return {key: values[key] for key in sorted(values)}
