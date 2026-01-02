from __future__ import annotations

from dataclasses import dataclass

from tmmonitor.config import SimilarityThresholds, SimilarityWeights
from tmmonitor.services.similarity.image import compare_images
from tmmonitor.services.similarity.text import compare_text


@dataclass(frozen=True)
class SimilarityResultDetail:
    score: float
    level: str
    text_score: float
    image_score: float
    reasons: list[str]


def _level(score: float, thresholds: SimilarityThresholds) -> str:
    if score >= thresholds.high:
        return "high"
    if score >= thresholds.medium:
        return "medium"
    if score >= thresholds.low:
        return "low"
    return "none"


def compute_similarity(
    name_a: str | None,
    name_b: str | None,
    image_url_a: str | None,
    image_url_b: str | None,
    weights: SimilarityWeights,
    thresholds: SimilarityThresholds,
    enable_image: bool,
    enable_semantic: bool,
    semantic_model: str,
) -> SimilarityResultDetail:
    text_detail = compare_text(name_a, name_b, enable_semantic, semantic_model)
    active_semantic_weight = weights.semantic if enable_semantic else 0.0
    weight_sum = weights.shape + weights.phonetic + active_semantic_weight
    raw_text_score = (
        text_detail.shape_score * weights.shape
        + text_detail.phonetic_score * weights.phonetic
        + text_detail.semantic_score * active_semantic_weight
    )
    text_score = raw_text_score / weight_sum if weight_sum > 0 else 0.0

    image_score = 0.0
    reasons = list(text_detail.reasons)
    if enable_image:
        image_detail = compare_images(image_url_a, image_url_b)
        image_score = image_detail.score
        reasons.extend(image_detail.reasons)

    combined_score = max(text_score, image_score)
    level = _level(combined_score, thresholds)

    if level != "none":
        reasons.append(f"整體分級: {level}")

    return SimilarityResultDetail(
        score=combined_score,
        level=level,
        text_score=text_score,
        image_score=image_score,
        reasons=reasons,
    )
