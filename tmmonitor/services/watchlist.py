from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from tmmonitor.clients.tipo import TIPOClient
from tmmonitor.models import SyncState, WatchlistItem
from tmmonitor.services.records import extract_goods_groups, extract_image_urls, extract_agents
from tmmonitor.utils.normalization import normalize_text


def _get_last_run(session: Session) -> dt.date | None:
    record = session.get(SyncState, "watchlist_last_run")
    if not record:
        return None
    return dt.date.fromisoformat(record.value)


def _set_last_run(session: Session, value: dt.date) -> None:
    record = session.get(SyncState, "watchlist_last_run")
    if record:
        record.value = value.isoformat()
    else:
        session.add(SyncState(key="watchlist_last_run", value=value.isoformat()))


def sync_watchlist(
    session: Session,
    start_date: dt.date | None,
    end_date: dt.date | None,
    agent_keyword: str,
    incremental: bool = True,
) -> int:
    client = TIPOClient()
    params: dict = {"agentname": agent_keyword}

    last_run = _get_last_run(session) if incremental else None
    if start_date:
        params["applbdate"] = start_date.strftime("%Y%m%d")
    elif last_run:
        params["applbdate"] = last_run.strftime("%Y%m%d")

    if end_date:
        params["appledate"] = end_date.strftime("%Y%m%d")

    created = 0
    for item in client.fetch_tmark_appl(params):
        appl_no = item.get("appl-no")
        if not appl_no:
            continue

        exists = session.execute(
            select(WatchlistItem).where(WatchlistItem.appl_no == appl_no)
        ).scalar_one_or_none()
        if exists:
            continue

        goodsclasses = item.get("goodsclasses") or []
        parties = item.get("parties") or {}
        image_urls = extract_image_urls(item.get("tmark-image-url") or [])

        watch = WatchlistItem(
            appl_no=appl_no,
            appl_date=_to_date(item.get("appl-date")),
            tmark_name=normalize_text(item.get("tmark-name")),
            agent_name=";".join(extract_agents(parties)),
            goods_groups=";".join(extract_goods_groups(goodsclasses)),
            goods_classes=goodsclasses or None,
            image_urls={"urls": image_urls} if image_urls else None,
            tmark_sign=item.get("tmark-sign"),
        )
        session.add(watch)
        created += 1

    if end_date:
        _set_last_run(session, end_date)
    elif start_date:
        _set_last_run(session, dt.date.today())

    return created


def _to_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y/%m/%d").date()
