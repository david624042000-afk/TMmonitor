from __future__ import annotations

import re
from typing import Iterable

SPLIT_PATTERN = re.compile(r"[、,，;；\n\r\t ]+")


def normalize_goods_groups(groups: Iterable[str | None]) -> set[str]:
    values: set[str] = set()
    for group in groups:
        if not group:
            continue
        for part in SPLIT_PATTERN.split(group):
            cleaned = part.strip()
            if cleaned:
                values.add(cleaned)
    return values


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()
