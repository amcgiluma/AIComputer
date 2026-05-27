from __future__ import annotations

from datetime import datetime
from pathlib import Path

from . import paths


class AuditLog:
    def __init__(self, enabled: bool = True, log_path: Path | None = None) -> None:
        self.enabled = enabled
        self.log_path = log_path or paths.log_dir() / "voice-codex.log"
        if self.enabled:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, title: str, body: str = "") -> None:
        if not self.enabled:
            return
        stamp = datetime.now().isoformat(timespec="seconds")
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n## {stamp} {title}\n")
            if body:
                fh.write(body.rstrip() + "\n")
