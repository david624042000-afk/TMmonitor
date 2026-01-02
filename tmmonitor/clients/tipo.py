from __future__ import annotations

import time
from typing import Iterator, Optional

import requests

from tmmonitor.config import load_settings


class TIPOClient:
    def __init__(self) -> None:
        self.settings = load_settings()
        if not self.settings.tipo_tk:
            raise ValueError("TIPO_TK is required")

    def _request(self, endpoint: str, params: dict) -> dict:
        url = f"{self.settings.tipo_base_url}/{endpoint}"
        params = {**params, "tk": self.settings.tipo_tk, "format": "json"}
        last_error: Optional[Exception] = None

        for attempt in range(1, self.settings.request_max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.settings.request_timeout_s)
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                sleep_for = self.settings.request_backoff_s * attempt
                time.sleep(sleep_for)

        raise RuntimeError(f"TIPO API request failed after retries: {last_error}")

    def fetch_tmark_appl(self, params: dict) -> Iterator[dict]:
        return self._paged_fetch("TmarkAppl", "tmarkappl", params)

    def fetch_tmark_rights(self, params: dict) -> Iterator[dict]:
        return self._paged_fetch("TmarkRights", "tmarkrights", params)

    def _paged_fetch(self, endpoint: str, root_key: str, params: dict) -> Iterator[dict]:
        skip = 0
        top = self.settings.page_size
        while True:
            payload = self._request(endpoint, {**params, "top": top, "skip": skip})
            container = payload.get(root_key) or {}
            items = container.get("tmarkcontent") or []
            if not items:
                break
            for item in items:
                yield item
            skip += top
