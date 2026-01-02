"""Run TMmonitor workflows from Spyder without CLI."""
from __future__ import annotations

import datetime as dt

from tmmonitor.config import load_settings
from tmmonitor.db import Base, get_engine, get_session_factory
from tmmonitor.models import SimilarityResult
from tmmonitor.services.alerts import send_alerts
from tmmonitor.services.candidates import fetch_candidates_from_appl, fetch_candidates_from_rights
from tmmonitor.services.matcher import run_similarity
from tmmonitor.services.reports import write_report, write_report_excel
from tmmonitor.services.watchlist import sync_watchlist


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(get_engine())


def sync_watchlist_spyder(
    start: str | None = None,
    end: str | None = None,
    incremental: bool = True,
) -> int:
    """Sync watchlist from TIPO using agent keyword."""
    settings = load_settings()
    session_factory = get_session_factory()
    with session_factory() as session:
        created = sync_watchlist(
            session,
            _parse_date(start),
            _parse_date(end),
            settings.agent_keyword,
            incremental=incremental,
        )
        session.commit()
    return created


def fetch_candidates_spyder(start: str, end: str) -> tuple[int, int]:
    """Fetch candidate cases from rights and application endpoints."""
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if not start_date or not end_date:
        raise ValueError("start and end are required")

    session_factory = get_session_factory()
    with session_factory() as session:
        created_rights = fetch_candidates_from_rights(session, start_date, end_date)
        created_appl = fetch_candidates_from_appl(session, start_date, end_date)
        session.commit()
    return created_rights, created_appl


def run_similarity_spyder(run_type: str = "adhoc") -> int:
    """Run similarity matching and return run id."""
    session_factory = get_session_factory()
    with session_factory() as session:
        run = run_similarity(session, run_type=run_type)
        session.commit()
    return run.id


def write_report_spyder(run_id: int, fmt: str = "csv") -> str:
    """Write report for a run id in CSV or Excel format."""
    settings = load_settings()
    session_factory = get_session_factory()
    with session_factory() as session:
        results = (
            session.query(SimilarityResult)
            .filter(SimilarityResult.run_id == run_id)
            .all()
        )

    if fmt.lower() == "excel":
        return write_report_excel(results, settings.report_output_dir, f"report_{run_id}.xlsx")
    return write_report(results, settings.report_output_dir, f"report_{run_id}.csv")


def send_alerts_spyder(run_id: int) -> int:
    """Send alerts for a run id."""
    session_factory = get_session_factory()
    with session_factory() as session:
        sent = send_alerts(session, run_id)
        session.commit()
    return sent


def _parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%d").date()


if __name__ == "__main__":
    init_db()
