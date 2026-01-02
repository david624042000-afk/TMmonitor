from __future__ import annotations

import csv
import os
from typing import Iterable

from tmmonitor.models import SimilarityResult

HEADERS = [
    "watchlist_id",
    "candidate_id",
    "score",
    "level",
    "text_score",
    "image_score",
    "reasons",
]


def write_report(results: Iterable[SimilarityResult], output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        for result in results:
            writer.writerow(_row(result))

    return path


def write_report_excel(results: Iterable[SimilarityResult], output_dir: str, filename: str) -> str:
    import pandas as pd

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    rows = [_row(result) for result in results]
    frame = pd.DataFrame(rows, columns=HEADERS)
    frame.to_excel(path, index=False)
    return path


def _row(result: SimilarityResult) -> list[str]:
    return [
        str(result.watchlist_id),
        str(result.candidate_id),
        f"{result.score:.3f}",
        result.level,
        f"{result.text_score:.3f}",
        "" if result.image_score is None else f"{result.image_score:.3f}",
        ";".join(result.reasons.get("items", [])),
    ]
