from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from tmmonitor.config import load_settings

Base = declarative_base()


def get_engine():
    settings = load_settings()
    return create_engine(settings.database_url, future=True)


def get_session_factory():
    return sessionmaker(bind=get_engine(), future=True)
