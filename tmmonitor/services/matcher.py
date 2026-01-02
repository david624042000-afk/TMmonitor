from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from tmmonitor.config import load_settings
from tmmonitor.models import CandidateItem, RunRecord, SimilarityResult, WatchlistItem
from tmmonitor.services.prefilter import has_goods_group_intersection
from tmmonitor.services.similarity.engine import compute_similarity


def run_similarity(session: Session, run_type: str = "adhoc") -> RunRecord:
    settings = load_settings()
    run = RunRecord(run_type=run_type, status="running", created_at=dt.datetime.utcnow())
    session.add(run)
    session.flush()

    watchlist_items = session.query(WatchlistItem).all()
    candidates = session.query(CandidateItem).all()

    for watch in watchlist_items:
        watch_groups = (watch.goods_groups or "").split(";")
        watch_image = _first_image(watch.image_urls)

        for candidate in candidates:
            candidate_groups = (candidate.goods_groups or "").split(";")
            if not has_goods_group_intersection(watch_groups, candidate_groups):
                continue

            candidate_image = _first_image(candidate.image_urls)
            similarity = compute_similarity(
                watch.tmark_name,
                candidate.tmark_name,
                watch_image,
                candidate_image,
                settings.similarity_weights,
                settings.similarity_thresholds,
                settings.enable_image_similarity,
                settings.enable_semantic,
                settings.semantic_model_name,
            )

            if similarity.level == "none":
                continue

            session.add(
                SimilarityResult(
                    run_id=run.id,
                    watchlist_id=watch.id,
                    candidate_id=candidate.id,
                    score=similarity.score,
                    level=similarity.level,
                    reasons={"items": similarity.reasons},
                    text_score=similarity.text_score,
                    image_score=similarity.image_score,
                    prefilter_matched=True,
                )
            )

    run.status = "completed"
    return run


def _first_image(payload: dict | None) -> str | None:
    if not payload:
        return None
    urls = payload.get("urls")
    if not urls:
        return None
    return urls[0]
