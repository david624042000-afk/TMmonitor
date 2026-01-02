from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tmmonitor.db import Base


class SyncState(Base):
    __tablename__ = "sync_state"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False
    )


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appl_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    appl_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    tmark_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    goods_groups: Mapped[str | None] = mapped_column(Text, nullable=True)
    goods_classes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    image_urls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tmark_sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False
    )


class CandidateItem(Base):
    __tablename__ = "candidate_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(20), index=True)
    appl_no: Mapped[str] = mapped_column(String(20), index=True)
    appl_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    reg_notice_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    tmark_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    goods_groups: Mapped[str | None] = mapped_column(Text, nullable=True)
    goods_classes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    image_urls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tmark_sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False
    )

    similarities: Mapped[list[SimilarityResult]] = relationship(
        "SimilarityResult", back_populates="candidate"
    )


class RunRecord(Base):
    __tablename__ = "run_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_type: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False
    )

    similarities: Mapped[list[SimilarityResult]] = relationship(
        "SimilarityResult", back_populates="run"
    )


class SimilarityResult(Base):
    __tablename__ = "similarity_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run_records.id"))
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlist_items.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_items.id"))
    score: Mapped[float] = mapped_column(Float)
    level: Mapped[str] = mapped_column(String(10))
    reasons: Mapped[dict] = mapped_column(JSON)
    text_score: Mapped[float] = mapped_column(Float)
    image_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    prefilter_matched: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False
    )

    run: Mapped[RunRecord] = relationship("RunRecord", back_populates="similarities")
    candidate: Mapped[CandidateItem] = relationship(
        "CandidateItem", back_populates="similarities"
    )


class AlertRecord(Base):
    __tablename__ = "alert_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    similarity_id: Mapped[int] = mapped_column(ForeignKey("similarity_results.id"))
    channel: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
    sent_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
