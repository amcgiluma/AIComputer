from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path


class Speaker:
    def __init__(self, config: dict) -> None:
        self.config = config

    def speak(self, text: str) -> str | None:
        if not self.config.get("read_codex_response", True):
            return None
        engine = self.config.get("engine", "espeak-ng")
        if engine == "espeak-ng":
            return self._speak_espeak(text)
        if engine == "piper":
            warning = self._speak_piper(text)
            if warning and self.config.get("fallback_engine") == "espeak-ng":
                fallback_warning = self._speak_espeak(text)
                return warning if not fallback_warning else f"{warning}\nFallback espeak-ng: {fallback_warning}"
            return warning
        return f"TTS desactivado o motor no soportado: {engine}"

    def _speak_espeak(self, text: str) -> str | None:
        exe = shutil.which("espeak-ng")
        if not exe:
            return "espeak-ng no esta instalado. Instala con: sudo pacman -S espeak-ng"
        voice = str(self.config.get("voice", "es"))
        rate = str(self.config.get("rate", 165))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav:
            wav_path = Path(wav.name)
        synth = subprocess.run([exe, "-v", voice, "-s", rate, "-w", str(wav_path), text], capture_output=True, text=True)
        if synth.returncode != 0:
            wav_path.unlink(missing_ok=True)
            return synth.stderr.strip() or "espeak-ng fallo al generar audio"
        warning = play_wav(wav_path)
        if warning:
            return warning
        return None

    def _speak_piper(self, text: str) -> str | None:
        exe = self.config.get("piper_executable") or shutil.which("piper-tts") or shutil.which("piper")
        if not exe:
            return "Piper TTS no esta instalado. El paquete 'piper' de Arch es una app de ratones, no TTS."
        exe_path = Path(str(exe)).expanduser()

        model = self.config.get("piper_model")
        if not model:
            return "Piper TTS requiere configurar tts.piper_model con la ruta a un modelo .onnx"
        model_path = Path(str(model)).expanduser()
        if not model_path.exists():
            return f"No existe el modelo Piper TTS: {model_path}"

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav:
            wav_path = Path(wav.name)

        try:
            cmd = [
                str(exe_path),
                "--model",
                str(model_path),
                "--output_file",
                str(wav_path),
            ]
            if self.config.get("piper_length_scale") is not None:
                cmd.extend(["--length_scale", str(self.config.get("piper_length_scale"))])
            synth = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
            )
            if synth.returncode != 0:
                wav_path.unlink(missing_ok=True)
                return synth.stderr.strip() or "Piper TTS fallo al sintetizar audio"
            return play_wav(wav_path)
        except FileNotFoundError:
            return "El ejecutable configurado para Piper TTS no existe"


def play_wav(wav_path: Path) -> str | None:
    player = shutil.which("pw-play") or shutil.which("paplay") or shutil.which("aplay")
    if not player:
        return f"Audio generado en {wav_path}, pero no hay reproductor pw-play/paplay/aplay"
    proc = subprocess.Popen([player, str(wav_path)])
    threading.Thread(target=cleanup_after_playback, args=(proc, wav_path), daemon=True).start()
    return None


def cleanup_after_playback(proc: subprocess.Popen, wav_path: Path) -> None:
    try:
        proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
    time.sleep(1)
    wav_path.unlink(missing_ok=True)
