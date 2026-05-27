from __future__ import annotations

import argparse
import sys

from .audit import AuditLog
from .codex_client import CodexClient
from .config import load_config
from .tts import Speaker


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask Voice Codex from the terminal")
    parser.add_argument("prompt", nargs="*", help="Prompt to send to Codex")
    parser.add_argument("--no-tts", action="store_true", help="Do not speak the answer")
    args = parser.parse_args()

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        prompt = sys.stdin.read().strip()
    if not prompt:
        print("No prompt provided", file=sys.stderr)
        return 2

    config = load_config()
    audit = AuditLog(enabled=bool(config["audit"].get("enabled", True)))
    answer = CodexClient(config, audit).ask(prompt)
    print(answer)
    if not args.no_tts:
        warning = Speaker(config["tts"]).speak(answer)
        if warning:
            print(f"TTS: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
