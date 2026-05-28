from __future__ import annotations

import copy
import tomllib
from pathlib import Path
from typing import Any

from . import paths

PIPER_BASE = Path.home() / ".local" / "share" / "voice-codex" / "piper-tts"
DEFAULT_PIPER_EXECUTABLE = PIPER_BASE / "bin" / "piper" / "piper"
DEFAULT_PIPER_MODEL = PIPER_BASE / "voices" / "es_ES-davefx-medium.onnx"

DEFAULT_CONFIG: dict[str, Any] = {
    "codex": {
        "model_label": "gpt 5.4 Mini Low",
        "model": "gpt-5.4-mini",
        "model_reasoning_effort": "low",
        "workdir": str(Path.home()),
        "sandbox": "danger-full-access",
        "approval_policy": "never",
        "bypass_approvals_and_sandbox": True,
        "resume_strategy": "new-with-history",
    },
    "handy": {
        "model": "canary-180m-flash",
        "language": "es",
        "toggle_command": "handy --toggle-transcription",
        "start_hidden_command": "handy --start-hidden",
        "post_process": False,
        "translate_to_english": False,
        "ensure_settings": True,
        "transcription_settle_ms": 1800,
    },
    "stt": {
        "engine": "whisper_cpp",
        "fallback_engine": "handy",
        "record_command": "pw-record",
        "source": "@DEFAULT_AUDIO_SOURCE@",
        "whisper_executable": str(Path.home() / ".local" / "share" / "voice-codex" / "whisper.cpp" / "build" / "bin" / "whisper-cli"),
        "whisper_model": str(Path.home() / ".local" / "share" / "voice-codex" / "whisper.cpp" / "models" / "ggml-base.bin"),
        "language": "es",
        "normalize_audio": True,
        "ffmpeg_executable": "ffmpeg",
        "audio_filter": "highpass=f=90,lowpass=f=7600,afftdn=nf=-25,dynaudnorm=f=150:g=15:p=0.95",
        "suppress_non_speech_tokens": True,
        "initial_prompt": "Transcribe solamente voz hablada en espanol.",
        "transcription_settle_ms": 250,
        "vad_enabled": True,
        "vad_model": str(Path.home() / ".local" / "share" / "voice-codex" / "whisper.cpp" / "models" / "ggml-silero-v6.2.0.bin"),
        "vad_threshold": 0.35,
    },
    "tts": {
        "engine": "piper",
        "fallback_engine": "espeak-ng",
        "voice": "es",
        "rate": 165,
        "read_codex_response": True,
        "read_action_summary": True,
        "piper_executable": str(DEFAULT_PIPER_EXECUTABLE),
        "piper_model": str(DEFAULT_PIPER_MODEL),
        "piper_length_scale": 1.0,
    },
    "screen": {
        "mode": "ai_decides",
        "allow_fullscreen_capture": True,
        "allow_region_capture": True,
        "attach_images_to_codex": True,
        "ocr_enabled": True,
    },
    "behavior": {
        "language": "es",
        "tone": "directo",
        "autonomy": "high",
        "ask_before_destructive_actions": True,
        "prefer_doing_over_explaining": True,
        "explain_actions_after_execution": True,
        "max_spoken_response_seconds": 90,
        "use_omarchy_skill_by_default": True,
        "use_arch_skill_by_default": True,
        "use_cachyos_skill_if_installed": True,
    },
    "permissions": {
        "default": "full",
        "allow_shell": True,
        "allow_gui": True,
        "allow_file_edits": True,
        "allow_system_config": True,
        "allow_package_install": True,
        "allow_browser_control": True,
        "allow_screen_capture": "ai_decides",
    },
    "audit": {
        "enabled": True,
        "log_prompts": True,
        "log_codex_output": True,
        "log_commands": True,
    },
    "memory": {
        "enabled": True,
        "dir": str(Path.home() / ".codex" / "memories" / "voice-codex"),
        "max_bytes": 20000,
    },
    "ui": {
        "window_title": "Voice Codex",
        "auto_focus_on_record": False,
        "show_window_on_start": False,
        "indicator": "notification",
        "notification_icon": "assistant",
        "notification_timeout_ms": 1800,
    },
}


def load_config(path: Path | None = None) -> dict[str, Any]:
    path = path or paths.config_file()
    ensure_config(path)
    with path.open("rb") as fh:
        loaded = tomllib.load(fh)
    return deep_merge(copy.deepcopy(DEFAULT_CONFIG), loaded)


def ensure_config(path: Path | None = None) -> None:
    path = path or paths.config_file()
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_toml(DEFAULT_CONFIG), encoding="utf-8")


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def to_toml(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for section, values in data.items():
        lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} = {format_toml_value(value)}")
        lines.append("")
    return "\n".join(lines)


def format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
