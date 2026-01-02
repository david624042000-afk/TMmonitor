from __future__ import annotations

from tmmonitor.utils.normalization import normalize_goods_groups


def has_goods_group_intersection(groups_a: list[str | None], groups_b: list[str | None]) -> bool:
    set_a = normalize_goods_groups(groups_a)
    set_b = normalize_goods_groups(groups_b)
    return bool(set_a and set_b and set_a.intersection(set_b))
