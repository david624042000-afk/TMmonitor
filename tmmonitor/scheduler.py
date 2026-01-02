from __future__ import annotations

import datetime as dt

from apscheduler.schedulers.blocking import BlockingScheduler

from tmmonitor.config import load_settings
from tmmonitor.db import get_session_factory
from tmmonitor.services.candidates import fetch_candidates_from_appl, fetch_candidates_from_rights
from tmmonitor.services.matcher import run_similarity
from tmmonitor.services.watchlist import sync_watchlist


def run_scheduler() -> None:
    settings = load_settings()
    scheduler = BlockingScheduler()

    def daily_job() -> None:
        today = dt.date.today()
        start = today - dt.timedelta(days=7)
        session_factory = get_session_factory()
        with session_factory() as session:
            sync_watchlist(session, None, today, settings.agent_keyword)
            fetch_candidates_from_rights(session, start, today)
            fetch_candidates_from_appl(session, start, today)
            run_similarity(session, run_type="scheduled")
            session.commit()

    scheduler.add_job(daily_job, "cron", hour=2, minute=0)
    scheduler.start()


if __name__ == "__main__":
    run_scheduler()
