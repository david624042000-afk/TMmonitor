from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from tmmonitor.clients.tipo import TIPOClient
from tmmonitor.models import CandidateItem
from tmmonitor.services.records import extract_goods_groups, extract_image_urls
from tmmonitor.utils.normalization import normalize_text


def fetch_candidates_from_appl(
    session: Session,
    start_date: dt.date,
    end_date: dt.date,
) -> int:
    client = TIPOClient()
    params = {
        "applbdate": start_date.strftime("%Y%m%d"),
        "appledate": end_date.strftime("%Y%m%d"),
    }

    created = 0
    for item in client.fetch_tmark_appl(params):
        appl_no = item.get("appl-no")
        if not appl_no:
            continue

        exists = session.execute(
            select(CandidateItem).where(
                CandidateItem.appl_no == appl_no,
                CandidateItem.source == "appl",
            )
        ).scalar_one_or_none()
        if exists:
            continue

        goodsclasses = item.get("goodsclasses") or []
        image_urls = extract_image_urls(item.get("tmark-image-url") or [])

        candidate = CandidateItem(
            source="appl",
            appl_no=appl_no,
            appl_date=_to_date(item.get("appl-date")),
            tmark_name=normalize_text(item.get("tmark-name")),
            goods_groups=";".join(extract_goods_groups(goodsclasses)),
            goods_classes=goodsclasses or None,
            image_urls={"urls": image_urls} if image_urls else None,
            tmark_sign=item.get("tmark-sign"),
        )
        session.add(candidate)
        created += 1

    return created


def fetch_candidates_from_rights(
    session: Session,
    start_date: dt.date,
    end_date: dt.date,
) -> int:
    client = TIPOClient()
    params = {
        "regnoticebdate": start_date.strftime("%Y%m%d"),
        "regnoticeedate": end_date.strftime("%Y%m%d"),
    }

    created = 0
    for item in client.fetch_tmark_rights(params):
        appl_no = item.get("appl-no")
        if not appl_no:
            continue

        exists = session.execute(
            select(CandidateItem).where(
                CandidateItem.appl_no == appl_no,
                CandidateItem.source == "rights",
            )
        ).scalar_one_or_none()
        if exists:
            continue

        goodsclasses = item.get("goodsclasses") or []
        image_urls = extract_image_urls(item.get("tmark-image-url") or [])

        candidate = CandidateItem(
            source="rights",
            appl_no=appl_no,
            appl_date=_to_date(item.get("appl-date")),
            reg_notice_date=_to_date(item.get("reg-notice-date")),
            tmark_name=normalize_text(item.get("tmark-name")),
            goods_groups=";".join(extract_goods_groups(goodsclasses)),
            goods_classes=goodsclasses or None,
            image_urls={"urls": image_urls} if image_urls else None,
            tmark_sign=item.get("tmark-sign"),
        )
        session.add(candidate)
        created += 1

    return created


def _to_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
