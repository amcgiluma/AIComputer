from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "voice-codex"
WINDOW_TITLE = "Voice Codex"


def xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def xdg_state_home() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))


def xdg_runtime_dir() -> Path:
    return Path(os.environ.get("XDG_RUNTIME_DIR", f"/tmp/{APP_NAME}-{os.getuid()}"))


def config_dir() -> Path:
    return xdg_config_home() / APP_NAME


def state_dir() -> Path:
    return xdg_state_home() / APP_NAME


def runtime_dir() -> Path:
    return xdg_runtime_dir() / APP_NAME


def config_file() -> Path:
    return config_dir() / "config.toml"


def socket_file() -> Path:
    return runtime_dir() / "voice-codex.sock"


def listening_file() -> Path:
    return runtime_dir() / "listening"


def recording_pid_file() -> Path:
    return runtime_dir() / "recording.pid"


def recording_file() -> Path:
    return runtime_dir() / "recording.wav"


def log_dir() -> Path:
    return state_dir() / "logs"


def screenshots_dir() -> Path:
    return state_dir() / "screenshots"
