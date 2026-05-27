from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path


def transcribe_recording(config: dict, audio_path: Path) -> str | None:
    stt = config.get("stt", {})
    engine = stt.get("engine", "whisper_cpp")
    if engine != "whisper_cpp":
        return None
    if not audio_path.exists() or audio_path.stat().st_size < 4096:
        return None

    executable = Path(str(stt.get("whisper_executable", ""))).expanduser()
    model = Path(str(stt.get("whisper_model", ""))).expanduser()
    language = str(stt.get("language", "es"))
    if not executable.exists() or not model.exists():
        return None

    cmd = [
        str(executable),
        "-m",
        str(model),
        "-f",
        str(audio_path),
        "-l",
        language,
        "-nt",
        "-np",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        return None
    text = result.stdout.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    transcript = " ".join(lines).strip()
    if _is_noise_transcript(transcript):
        return None
    return transcript or None


def _is_noise_transcript(text: str) -> bool:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char)).strip()
    stripped = normalized.strip("[](){} .,!?:;\"'")
    noise_markers = {
        "musica",
        "music",
        "aplausos",
        "applause",
        "risas",
        "laughter",
        "silencio",
        "silence",
    }
    words = stripped.split()
    return bool(stripped) and len(words) <= 3 and any(marker in words for marker in noise_markers)
