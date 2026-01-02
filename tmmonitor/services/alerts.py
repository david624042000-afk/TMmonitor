from __future__ import annotations

import datetime as dt
import json
import smtplib
from email.message import EmailMessage

import requests
from sqlalchemy.orm import Session

from tmmonitor.config import load_settings
from tmmonitor.models import AlertRecord, SimilarityResult


def send_alerts(session: Session, run_id: int) -> int:
    settings = load_settings()
    alerts_sent = 0

    similarities = (
        session.query(SimilarityResult)
        .filter(SimilarityResult.run_id == run_id)
        .all()
    )
    if not similarities:
        return 0

    if settings.alert_email_to:
        sent = _send_email_alerts(similarities, settings)
        if sent:
            session.add(
                AlertRecord(
                    similarity_id=similarities[0].id,
                    channel="email",
                    payload={"recipients": settings.alert_email_to},
                    status="sent",
                    sent_at=dt.datetime.utcnow(),
                )
            )
            alerts_sent += 1

    if settings.slack_webhook_url:
        sent = _send_slack_alerts(similarities, settings)
        if sent:
            session.add(
                AlertRecord(
                    similarity_id=similarities[0].id,
                    channel="slack",
                    payload={"webhook": settings.slack_webhook_url},
                    status="sent",
                    sent_at=dt.datetime.utcnow(),
                )
            )
            alerts_sent += 1

    return alerts_sent


def _send_email_alerts(similarities: list[SimilarityResult], settings) -> bool:
    if not similarities:
        return False
    if not settings.smtp_host or not settings.smtp_from:
        return False

    message = EmailMessage()
    message["Subject"] = "TMmonitor alert: similarity matches"
    message["From"] = settings.smtp_from
    message["To"] = settings.alert_email_to

    body_lines = ["Found similarity matches:"]
    for result in similarities:
        body_lines.append(
            f"- watchlist {result.watchlist_id} vs candidate {result.candidate_id} "
            f"score={result.score:.2f} level={result.level}"
        )
    message.set_content("\n".join(body_lines))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
    return True


def _send_slack_alerts(similarities: list[SimilarityResult], settings) -> bool:
    if not similarities:
        return False

    lines = ["TMmonitor similarity matches:"]
    for result in similarities:
        lines.append(
            f"• watchlist {result.watchlist_id} vs candidate {result.candidate_id} "
            f"score={result.score:.2f} level={result.level}"
        )
    payload = {"text": "\n".join(lines)}
    response = requests.post(settings.slack_webhook_url, data=json.dumps(payload), timeout=10)
    response.raise_for_status()
    return True
