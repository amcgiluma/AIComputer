from __future__ import annotations

import subprocess
import time
from pathlib import Path

from . import paths


VISUAL_HINTS = (
    "pantalla",
    "ves",
    "ver esto",
    "fondo",
    "wallpaper",
    "ventana",
    "aspecto",
    "queda",
    "se ve",
    "error abierto",
    "imagen",
    "captura",
    "visual",
)


def should_capture(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(hint in lowered for hint in VISUAL_HINTS)


def capture_fullscreen() -> Path | None:
    paths.screenshots_dir().mkdir(parents=True, exist_ok=True)
    target = paths.screenshots_dir() / f"screenshot-{int(time.time())}.png"
    result = subprocess.run(["grim", str(target)], text=True, capture_output=True)
    if result.returncode != 0:
        return None
    return target


def capture_region() -> Path | None:
    paths.screenshots_dir().mkdir(parents=True, exist_ok=True)
    target = paths.screenshots_dir() / f"screenshot-region-{int(time.time())}.png"
    geometry = subprocess.run(["slurp"], text=True, capture_output=True)
    if geometry.returncode != 0 or not geometry.stdout.strip():
        return None
    result = subprocess.run(["grim", "-g", geometry.stdout.strip(), str(target)], text=True, capture_output=True)
    if result.returncode != 0:
        return None
    return target


def ocr_image(image: Path) -> str:
    result = subprocess.run(["tesseract", str(image), "stdout"], text=True, capture_output=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
