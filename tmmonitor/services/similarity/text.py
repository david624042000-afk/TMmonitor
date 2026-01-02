from __future__ import annotations

import importlib.util
from dataclasses import dataclass

try:
    from rapidfuzz import fuzz
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    import difflib

    class _FallbackFuzz:
        @staticmethod
        def ratio(a: str, b: str) -> float:
            return difflib.SequenceMatcher(a=a, b=b).ratio() * 100

    fuzz = _FallbackFuzz()

from tmmonitor.utils.normalization import normalize_text


@dataclass(frozen=True)
class TextSimilarityDetail:
    shape_score: float
    phonetic_score: float
    semantic_score: float
    reasons: list[str]


def _to_simplified(value: str) -> str:
    if not value:
        return value
    if importlib.util.find_spec("opencc") is None:
        return value
    from opencc import OpenCC

    converter = OpenCC("t2s")
    return converter.convert(value)


def _to_pinyin(value: str) -> str:
    if not value:
        return value
    if importlib.util.find_spec("pypinyin") is None:
        return value
    from pypinyin import Style, pinyin

    pieces = pinyin(value, style=Style.NORMAL, heteronym=False)
    return "".join(part[0] for part in pieces)


def _semantic_score(a: str, b: str, model_name: str, enable_semantic: bool) -> float:
    if not a or not b:
        return 0.0
    if not enable_semantic:
        return 0.0
    if importlib.util.find_spec("sentence_transformers") is not None:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        model = SentenceTransformer(model_name)
        embeddings = model.encode([a, b])
        score = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
        return max(min(score, 1.0), 0.0)

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([a, b])
    score = float(cosine_similarity(vectors[0], vectors[1])[0][0])
    return max(min(score, 1.0), 0.0)


def compare_text(
    a: str | None,
    b: str | None,
    enable_semantic: bool,
    model_name: str,
) -> TextSimilarityDetail:
    normalized_a = _to_simplified(normalize_text(a))
    normalized_b = _to_simplified(normalize_text(b))

    shape_score = fuzz.ratio(normalized_a, normalized_b) / 100.0

    pinyin_a = _to_pinyin(normalized_a)
    pinyin_b = _to_pinyin(normalized_b)
    phonetic_score = fuzz.ratio(pinyin_a, pinyin_b) / 100.0

    semantic_score = _semantic_score(normalized_a, normalized_b, model_name, enable_semantic)

    reasons: list[str] = []
    if shape_score >= 0.8:
        reasons.append("字形相似度高")
    if phonetic_score >= 0.8:
        reasons.append("拼音相似度高")
    if semantic_score >= 0.75:
        reasons.append("語意相似度高")

    return TextSimilarityDetail(
        shape_score=shape_score,
        phonetic_score=phonetic_score,
        semantic_score=semantic_score,
        reasons=reasons,
    )
