# SQLite-backed cache (§4.6, §2.2 cross-cutting). Keyed by canonical config hash.
# Stores converged state vectors, qNet, APD90, RA flag, diagnostics, code version.
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS cache (
  key TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  code_version TEXT NOT NULL,
  created_utc TEXT NOT NULL
);
"""


class StateCache:
    def __init__(self, path: Path, code_version: str = "0.1.0"):
        self.path = path
        self.code_version = code_version
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path))
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def get(self, key: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload, code_version FROM cache WHERE key=?", (key,)
        ).fetchone()
        if row is None:
            return None
        payload, version = row
        if version != self.code_version:
            # cache corruption / schema drift -> ignore stale rows and recompute (§24)
            return None
        return json.loads(payload)

    def put(self, key: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO cache (key, payload, code_version, created_utc) VALUES (?,?,?,?)",
            (key, json.dumps(payload), self.code_version, _now()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _now() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()
