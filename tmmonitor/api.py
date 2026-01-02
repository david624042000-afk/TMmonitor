from __future__ import annotations

import datetime as dt

from fastapi import FastAPI, HTTPException

from tmmonitor.config import load_settings
from tmmonitor.db import Base, get_engine, get_session_factory
from tmmonitor.services.alerts import send_alerts
from tmmonitor.services.candidates import fetch_candidates_from_appl, fetch_candidates_from_rights
from tmmonitor.services.matcher import run_similarity
from tmmonitor.services.watchlist import sync_watchlist

app = FastAPI(title="TMmonitor")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(get_engine())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/watchlist/sync")
def api_sync_watchlist(start: str | None = None, end: str | None = None) -> dict:
    settings = load_settings()
    session_factory = get_session_factory()
    with session_factory() as session:
        created = sync_watchlist(
            session,
            _parse_date(start),
            _parse_date(end),
            settings.agent_keyword,
        )
        session.commit()
    return {"created": created}


@app.post("/candidates/fetch")
def api_fetch_candidates(start: str, end: str) -> dict:
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="start and end required")

    session_factory = get_session_factory()
    with session_factory() as session:
        created_rights = fetch_candidates_from_rights(session, start_date, end_date)
        created_appl = fetch_candidates_from_appl(session, start_date, end_date)
        session.commit()
    return {"rights": created_rights, "appl": created_appl}


@app.post("/similarity/run")
def api_run_similarity() -> dict:
    session_factory = get_session_factory()
    with session_factory() as session:
        run = run_similarity(session, run_type="api")
        session.commit()
    return {"run_id": run.id}


@app.post("/alerts/send")
def api_send_alerts(run_id: int) -> dict:
    session_factory = get_session_factory()
    with session_factory() as session:
        sent = send_alerts(session, run_id)
        session.commit()
    return {"sent": sent}


def _parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%d").date()
