from __future__ import annotations

from pathlib import Path


DEFAULT_FOLDERS = ("preferences", "projects", "system", "voice", "notes")
SUPPORTED_SUFFIXES = {".md", ".txt"}


def memory_dir(config: dict) -> Path:
    raw = config.get("dir") or Path.home() / ".codex" / "memories" / "voice-codex"
    return Path(str(raw)).expanduser()


def ensure_memory_dir(config: dict) -> Path:
    root = memory_dir(config)
    root.mkdir(parents=True, exist_ok=True)
    for folder in DEFAULT_FOLDERS:
        (root / folder).mkdir(exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Voice Codex memory\n\n"
            "Guarda aqui notas persistentes que quieres que Voice Codex tenga en cuenta.\n\n"
            "- `preferences/`: preferencias personales y estilo de trabajo.\n"
            "- `projects/`: contexto estable de proyectos.\n"
            "- `system/`: datos de tu maquina y entorno.\n"
            "- `voice/`: ajustes deseados de voz, transcripcion y TTS.\n"
            "- `notes/`: cualquier otra memoria util.\n\n"
            "Usa archivos `.md` o `.txt`. Voice Codex los lee antes de cada peticion.\n",
            encoding="utf-8",
        )
    return root


def load_memory_context(config: dict) -> str:
    if not config.get("enabled", True):
        return ""

    root = ensure_memory_dir(config)
    max_bytes = int(config.get("max_bytes", 20000) or 20000)
    remaining = max(max_bytes, 0)
    chunks: list[str] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.name.casefold() == "readme.md" or path.suffix.casefold() not in SUPPORTED_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            continue
        if not text:
            continue

        encoded = text.encode("utf-8")
        if remaining <= 0:
            break
        if len(encoded) > remaining:
            text = encoded[:remaining].decode("utf-8", errors="ignore").strip()
        remaining -= len(text.encode("utf-8"))
        chunks.append(f"Archivo: {path.relative_to(root)}\n{text}")

    return "\n\n---\n\n".join(chunks)
