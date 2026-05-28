from __future__ import annotations

import subprocess
import tempfile
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

    prepared_audio = _prepare_audio(stt, audio_path)
    try:
        text = _run_whisper(stt, executable, model, prepared_audio, language)
    finally:
        if prepared_audio != audio_path:
            prepared_audio.unlink(missing_ok=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    transcript = " ".join(lines).strip()
    if _is_noise_transcript(transcript):
        return None
    return transcript or None


def _prepare_audio(stt: dict, audio_path: Path) -> Path:
    if not stt.get("normalize_audio", True):
        return audio_path

    ffmpeg = str(stt.get("ffmpeg_executable", "ffmpeg"))
    audio_filter = str(stt.get("audio_filter", "highpass=f=90,lowpass=f=7600,dynaudnorm=f=150:g=15:p=0.95"))
    with tempfile.NamedTemporaryFile(prefix="voice-codex-", suffix=".wav", delete=False) as fh:
        normalized_path = Path(fh.name)

    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(audio_path),
        "-af",
        audio_filter,
        "-ar",
        "16000",
        "-ac",
        "1",
        str(normalized_path),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0 or not normalized_path.exists() or normalized_path.stat().st_size < 4096:
        normalized_path.unlink(missing_ok=True)
        return audio_path
    return normalized_path


def _run_whisper(stt: dict, executable: Path, model: Path, audio_path: Path, language: str) -> str:
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
    if stt.get("suppress_non_speech_tokens", True):
        cmd.append("-sns")
    vad_model = Path(str(stt.get("vad_model", ""))).expanduser()
    if stt.get("vad_enabled", True) and vad_model.exists():
        cmd.extend(["--vad", "-vm", str(vad_model), "-vt", str(stt.get("vad_threshold", 0.35))])
    initial_prompt = str(stt.get("initial_prompt", "")).strip()
    if initial_prompt:
        cmd.extend(["--prompt", initial_prompt])

    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


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
