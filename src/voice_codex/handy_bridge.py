from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path


HANDY_SETTINGS = Path.home() / ".local" / "share" / "com.pais.handy" / "settings_store.json"
HANDY_HISTORY = Path.home() / ".local" / "share" / "com.pais.handy" / "history.db"


def ensure_handy_settings(config: dict) -> str | None:
    if not config.get("ensure_settings", True):
        return None
    if not HANDY_SETTINGS.exists():
        return f"No existe config de Handy en {HANDY_SETTINGS}"

    data = json.loads(HANDY_SETTINGS.read_text(encoding="utf-8"))
    settings = data.get("settings", data)
    changed = False
    desired = {
        "selected_model": config.get("model", "canary-180m-flash"),
        "selected_language": config.get("language", "es"),
        "translate_to_english": bool(config.get("translate_to_english", False)),
    }
    for key, value in desired.items():
        if settings.get(key) != value:
            settings[key] = value
            changed = True

    if not changed:
        return None

    backup = HANDY_SETTINGS.with_suffix(f".json.bak.{int(time.time())}")
    shutil.copy2(HANDY_SETTINGS, backup)
    HANDY_SETTINGS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"Configuracion de Handy actualizada. Backup: {backup}"


def run_toggle(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command.split(), text=True, capture_output=True)


def latest_history_id() -> int:
    if not HANDY_HISTORY.exists():
        return 0
    with sqlite3.connect(HANDY_HISTORY) as db:
        row = db.execute("select coalesce(max(id), 0) from transcription_history").fetchone()
    return int(row[0] or 0)


def latest_transcription_after(last_id: int) -> tuple[int, str] | None:
    if not HANDY_HISTORY.exists():
        return None
    with sqlite3.connect(HANDY_HISTORY) as db:
        row = db.execute(
            """
            select id, transcription_text, post_processed_text
            from transcription_history
            where id > ?
            order by id desc
            limit 1
            """,
            (last_id,),
        ).fetchone()
    if not row:
        return None
    text = (row[2] or row[1] or "").strip()
    return int(row[0]), text
