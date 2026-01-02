from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _get_bool(name: str, default: bool = False) -> bool:
    value = _get_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


def _get_float(name: str, default: float) -> float:
    value = _get_env(name)
    if value is None:
        return default
    return float(value)


def _get_int(name: str, default: int) -> int:
    value = _get_env(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class SimilarityWeights:
    shape: float
    phonetic: float
    semantic: float


@dataclass(frozen=True)
class SimilarityThresholds:
    high: float
    medium: float
    low: float


@dataclass(frozen=True)
class Settings:
    tipo_base_url: str
    tipo_tk: Optional[str]
    database_url: str
    agent_keyword: str
    default_days_window: int
    page_size: int
    request_timeout_s: int
    request_max_retries: int
    request_backoff_s: float
    similarity_weights: SimilarityWeights
    similarity_thresholds: SimilarityThresholds
    enable_semantic: bool
    enable_image_similarity: bool
    enable_image_prefilter: bool
    semantic_model_name: str
    smtp_host: Optional[str]
    smtp_port: int
    smtp_user: Optional[str]
    smtp_password: Optional[str]
    smtp_from: Optional[str]
    alert_email_to: Optional[str]
    slack_webhook_url: Optional[str]
    report_output_dir: str


def load_settings() -> Settings:
    return Settings(
        tipo_base_url=_get_env(
            "TIPO_BASE_URL",
            "https://tagp.tipo.gov.tw/api/OpenDataApi/OpenData/API",
        ),
        tipo_tk=_get_env("TIPO_TK"),
        database_url=_get_env("DATABASE_URL", "sqlite:///tmmonitor.db"),
        agent_keyword=_get_env("WATCHLIST_AGENT_KEYWORD", "許世正"),
        default_days_window=_get_int("DEFAULT_DAYS_WINDOW", 365),
        page_size=_get_int("TIPO_PAGE_SIZE", 100),
        request_timeout_s=_get_int("TIPO_TIMEOUT_S", 30),
        request_max_retries=_get_int("TIPO_MAX_RETRIES", 5),
        request_backoff_s=_get_float("TIPO_BACKOFF_S", 1.5),
        similarity_weights=SimilarityWeights(
            shape=_get_float("SIM_WEIGHT_SHAPE", 0.4),
            phonetic=_get_float("SIM_WEIGHT_PHONETIC", 0.3),
            semantic=_get_float("SIM_WEIGHT_SEMANTIC", 0.3),
        ),
        similarity_thresholds=SimilarityThresholds(
            high=_get_float("SIM_THRESHOLD_HIGH", 0.85),
            medium=_get_float("SIM_THRESHOLD_MEDIUM", 0.75),
            low=_get_float("SIM_THRESHOLD_LOW", 0.65),
        ),
        enable_semantic=_get_bool("SIM_ENABLE_SEMANTIC", True),
        enable_image_similarity=_get_bool("SIM_ENABLE_IMAGE", True),
        enable_image_prefilter=_get_bool("SIM_ENABLE_IMAGE_PREFILTER", True),
        semantic_model_name=_get_env(
            "SIM_SEMANTIC_MODEL",
            "distiluse-base-multilingual-cased-v2",
        )
        or "distiluse-base-multilingual-cased-v2",
        smtp_host=_get_env("SMTP_HOST"),
        smtp_port=_get_int("SMTP_PORT", 587),
        smtp_user=_get_env("SMTP_USER"),
        smtp_password=_get_env("SMTP_PASSWORD"),
        smtp_from=_get_env("SMTP_FROM"),
        alert_email_to=_get_env("ALERT_EMAIL_TO"),
        slack_webhook_url=_get_env("SLACK_WEBHOOK_URL"),
        report_output_dir=_get_env("REPORT_OUTPUT_DIR", "reports"),
    )
