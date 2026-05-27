from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from . import ipc, paths
from .config import load_config


def main() -> int:
    paths.runtime_dir().mkdir(parents=True, exist_ok=True)
    config = load_config()
    ensure_app()
    focus_app()

    if paths.listening_file().exists():
        if config.get("stt", {}).get("engine") == "whisper_cpp":
            stop_pipewire_recording()
        else:
            ensure_handy_running()
            run_handy_toggle()
        paths.listening_file().unlink(missing_ok=True)
        ipc.send("stop")
        return 0

    paths.listening_file().write_text(str(time.time()), encoding="utf-8")
    ipc.send("start")
    if config.get("stt", {}).get("engine") == "whisper_cpp":
        start_pipewire_recording(config)
    else:
        ensure_handy_running()
        run_handy_toggle()
    return 0


def ensure_app() -> None:
    if ipc.send("ping"):
        return
    paths.socket_file().unlink(missing_ok=True)
    script = project_root() / "scripts" / "voice-codex"
    subprocess.Popen(
        [str(script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.time() + 4
    while time.time() < deadline:
        if paths.socket_file().exists() and ipc.send("ping"):
            return
        time.sleep(0.15)


def focus_app() -> None:
    subprocess.run(
        ["hyprctl", "dispatch", "focuswindow", "title:^(Voice Codex)$"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure_handy_running() -> None:
    if subprocess.run(["pgrep", "-x", "handy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        return
    subprocess.Popen(
        ["handy", "--start-hidden"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(1.5)


def run_handy_toggle() -> None:
    subprocess.run(["handy", "--toggle-transcription"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_pipewire_recording(config: dict) -> None:
    paths.recording_file().unlink(missing_ok=True)
    source = str(config.get("stt", {}).get("source", "@DEFAULT_AUDIO_SOURCE@"))
    command = str(config.get("stt", {}).get("record_command", "pw-record"))
    proc = subprocess.Popen(
        [
            command,
            "--target",
            source,
            "--rate",
            "16000",
            "--channels",
            "1",
            "--format",
            "s16",
            str(paths.recording_file()),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    paths.recording_pid_file().write_text(str(proc.pid), encoding="utf-8")


def stop_pipewire_recording() -> None:
    try:
        pid = int(paths.recording_pid_file().read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return
    subprocess.run(["kill", "-TERM", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 2
    while time.time() < deadline:
        if subprocess.run(["kill", "-0", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            break
        time.sleep(0.1)
    paths.recording_pid_file().unlink(missing_ok=True)


def project_root():
    return Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    sys.exit(main())
