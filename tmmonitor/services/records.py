from __future__ import annotations

from typing import Any


def extract_goods_groups(goodsclasses: list[dict]) -> list[str]:
    groups: list[str] = []
    for entry in goodsclasses or []:
        value = entry.get("goods-group")
        if value:
            groups.append(value)
    return groups


def extract_image_urls(image_entries: list[dict]) -> list[str]:
    urls: list[str] = []
    for entry in image_entries or []:
        for key, value in entry.items():
            if key.startswith("image-data-") and value:
                urls.append(value)
    return urls


def extract_agents(parties: dict) -> list[str]:
    agents = parties.get("agents") or []
    names: list[str] = []
    for agent in agents:
        name = agent.get("chinese-name")
        if name:
            names.append(name)
    return names


def extract_applicants(parties: dict) -> list[str]:
    applicants = parties.get("applicants") or []
    names: list[str] = []
    for applicant in applicants:
        name = applicant.get("chinese-name")
        if name:
            names.append(name)
    return names


def normalize_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)
