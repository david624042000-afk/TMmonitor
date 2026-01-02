from __future__ import annotations

import datetime as dt

import typer
from sqlalchemy.orm import Session

from tmmonitor.config import load_settings
from tmmonitor.db import Base, get_engine, get_session_factory
from tmmonitor.models import CandidateItem, SimilarityResult
from tmmonitor.services.alerts import send_alerts
from tmmonitor.services.candidates import fetch_candidates_from_appl, fetch_candidates_from_rights
from tmmonitor.services.matcher import run_similarity
from tmmonitor.services.reports import write_report, write_report_excel
from tmmonitor.services.watchlist import sync_watchlist

app = typer.Typer(help="TMmonitor CLI")


def _parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%d").date()


@app.command("init-db")
def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    typer.echo("Database initialized")


@app.command("sync-watchlist")
def sync_watchlist_command(
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    incremental: bool = typer.Option(True, "--incremental/--no-incremental"),
) -> None:
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
    typer.echo(f"Watchlist created: {created}")


@app.command("fetch-candidates")
def fetch_candidates_command(
    start: str = typer.Option(..., "--start"),
    end: str = typer.Option(..., "--end"),
) -> None:
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if not start_date or not end_date:
        raise typer.BadParameter("start and end are required")

    session_factory = get_session_factory()
    with session_factory() as session:
        created_rights = fetch_candidates_from_rights(session, start_date, end_date)
        created_appl = fetch_candidates_from_appl(session, start_date, end_date)
        session.commit()
    typer.echo(f"Candidates added: rights={created_rights} appl={created_appl}")


@app.command("run-similarity")
def run_similarity_command() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        run = run_similarity(session, run_type="adhoc")
        session.commit()
    typer.echo(f"Similarity run complete: {run.id}")


@app.command("send-alerts")
def send_alerts_command(run_id: int = typer.Option(..., "--run-id")) -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        sent = send_alerts(session, run_id)
        session.commit()
    typer.echo(f"Alerts sent: {sent}")


@app.command("report")
def report_command(
    run_id: int = typer.Option(..., "--run-id"),
    fmt: str = typer.Option("csv", "--format"),
) -> None:
    settings = load_settings()
    session_factory = get_session_factory()
    with session_factory() as session:
        results = (
            session.query(SimilarityResult)
            .filter(SimilarityResult.run_id == run_id)
            .all()
        )
        if fmt.lower() == "excel":
            path = write_report_excel(
                results, settings.report_output_dir, f"report_{run_id}.xlsx"
            )
        else:
            path = write_report(
                results, settings.report_output_dir, f"report_{run_id}.csv"
            )
    typer.echo(f"Report written: {path}")


@app.command("list-candidates")
def list_candidates(limit: int = typer.Option(20, "--limit")) -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        candidates = session.query(CandidateItem).limit(limit).all()
    for candidate in candidates:
        typer.echo(f"{candidate.id} {candidate.appl_no} {candidate.tmark_name}")


if __name__ == "__main__":
    app()
