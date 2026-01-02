from tmmonitor.config import SimilarityThresholds, SimilarityWeights
from tmmonitor.services.similarity.engine import compute_similarity


def test_similarity_levels_high():
    weights = SimilarityWeights(shape=0.4, phonetic=0.3, semantic=0.3)
    thresholds = SimilarityThresholds(high=0.85, medium=0.75, low=0.65)
    result = compute_similarity(
        "旺旺",
        "旺旺",
        None,
        None,
        weights,
        thresholds,
        enable_image=False,
        enable_semantic=False,
        semantic_model="",
    )
    assert result.level == "high"
    assert result.score >= thresholds.high
