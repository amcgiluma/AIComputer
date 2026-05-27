from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from . import paths
from .config import load_config


def main() -> int:
    config = load_config()
    checks: list[tuple[str, bool, str]] = []

    for command in ("codex", "handy", "hyprctl", "grim", "slurp", "tesseract", "espeak-ng", "pw-record"):
        found = shutil.which(command)
        checks.append((command, bool(found), found or "no encontrado"))

    stt = config.get("stt", {})
    whisper_bin = Path(str(stt.get("whisper_executable") or "")).expanduser()
    whisper_model = Path(str(stt.get("whisper_model") or "")).expanduser()
    whisper_ok = whisper_bin.exists() and whisper_model.exists()
    whisper_note = f"{whisper_bin} / {whisper_model}" if whisper_ok else "binario o modelo no encontrado"
    checks.append(("whisper.cpp", whisper_ok, whisper_note))

    configured_piper = str(config.get("tts", {}).get("piper_executable") or "")
    piper_bin = configured_piper if configured_piper and Path(configured_piper).exists() else None
    piper_bin = piper_bin or shutil.which("piper-tts") or shutil.which("piper")
    piper_ok = False
    piper_note = "no encontrado"
    if piper_bin:
        model = Path(str(config.get("tts", {}).get("piper_model") or "")).expanduser()
        info = subprocess.run(["pacman", "-Qo", str(piper_bin)], text=True, capture_output=True)
        if configured_piper and model.exists():
            piper_ok = True
            piper_note = f"{piper_bin} con voz {model}"
        elif " is owned by piper " in info.stdout and "piper-tts" not in str(piper_bin):
            piper_note = f"{piper_bin} es la app de ratones Piper, no Piper TTS"
        else:
            piper_ok = True
            piper_note = piper_bin
    checks.append(("piper-tts", piper_ok, piper_note))

    handy_settings = Path.home() / ".local/share/com.pais.handy/settings_store.json"
    checks.append(("handy-settings", handy_settings.exists(), str(handy_settings)))
    checks.append(("voice-codex-config", paths.config_file().exists(), str(paths.config_file())))
    checks.append(("hypr-binding", hypr_binding_installed(), "~/.config/hypr/bindings.conf"))

    print("Voice Codex doctor\n")
    for name, ok, detail in checks:
        mark = "OK" if ok else "WARN"
        print(f"[{mark}] {name}: {detail}")

    print("\nConfig efectiva:")
    print(f"- Codex: {config['codex'].get('model')} / reasoning={config['codex'].get('model_reasoning_effort')}")
    print(f"- STT: {config.get('stt', {}).get('engine')} / lang={config.get('stt', {}).get('language')}")
    print(f"- Handy fallback: {config['handy'].get('model')} / lang={config['handy'].get('language')}")
    print(f"- TTS: {config['tts'].get('engine')}")
    print(f"- Socket: {paths.socket_file()}")
    print(f"- Logs: {paths.log_dir() / 'voice-codex.log'}")

    return 0 if all(ok for name, ok, _detail in checks if name != "piper-tts") else 1


def hypr_binding_installed() -> bool:
    binding = Path.home() / ".config/hypr/bindings.conf"
    if not binding.exists():
        return False
    return "Voice Codex" in binding.read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
