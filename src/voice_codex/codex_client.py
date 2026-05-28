from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .memory import load_memory_context
from . import screen_context
from .skills import system_prompt


SCREENSHOT_MARKER = "[[VOICE_CODEX_REQUEST_SCREENSHOT:"


class CodexClient:
    def __init__(self, config: dict, audit) -> None:
        self.config = config
        self.audit = audit
        self.history: list[tuple[str, str]] = []

    def ask(self, user_text: str) -> str:
        images: list[Path] = []
        if self.config["screen"].get("mode") == "ai_decides" and screen_context.should_capture(user_text):
            image = screen_context.capture_fullscreen()
            if image:
                images.append(image)
                self.audit.write("captura", f"Captura automatica por contexto visual: {image}")

        answer = self._run_codex(user_text, images)
        if SCREENSHOT_MARKER in answer:
            mode = self._marker_mode(answer)
            image = screen_context.capture_region() if mode == "region" else screen_context.capture_fullscreen()
            if image:
                followup = (
                    "Adjunto la captura solicitada. Usa esta imagen para responder a la peticion original.\n\n"
                    f"Peticion original: {user_text}"
                )
                answer = self._run_codex(followup, [image])

        self.history.append((user_text, answer))
        self.history = self.history[-6:]
        return answer.strip()

    def _run_codex(self, user_text: str, images: list[Path]) -> str:
        codex = self.config["codex"]
        prompt = self._build_prompt(user_text, images)
        self.audit.write("prompt", prompt)

        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as output:
            output_path = Path(output.name)

        cmd = [
            "codex",
            "exec",
            "--json",
            "-m",
            str(codex.get("model", "gpt-5.4")),
            "-C",
            str(codex.get("workdir", str(Path.home()))),
            "-s",
            str(codex.get("sandbox", "danger-full-access")),
            "-o",
            str(output_path),
        ]
        if codex.get("model_reasoning_effort"):
            effort = str(codex["model_reasoning_effort"])
            cmd.extend(["-c", f'model_reasoning_effort="{effort}"'])
        if codex.get("bypass_approvals_and_sandbox", True):
            cmd.append("--dangerously-bypass-approvals-and-sandbox")
        for image in images:
            cmd.extend(["-i", str(image)])
        cmd.append("-")

        self.audit.write("codex-command", " ".join(cmd[:-1]) + " -")
        result = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
        final = output_path.read_text(encoding="utf-8").strip() if output_path.exists() else ""
        output_path.unlink(missing_ok=True)

        if result.returncode != 0:
            body = result.stderr.strip() or result.stdout.strip()
            self.audit.write("codex-error", body)
            return f"Codex fallo con codigo {result.returncode}.\n{body}"

        self.audit.write("codex-output", final or result.stdout)
        return final or result.stdout.strip()

    def _build_prompt(self, user_text: str, images: list[Path]) -> str:
        previous = "\n".join(
            f"Usuario: {user}\nVoice Codex: {assistant}" for user, assistant in self.history[-3:]
        )
        memory = load_memory_context(self.config.get("memory", {}))
        visual = ""
        if images:
            visual = "\nSe adjunta captura de pantalla. Usala si ayuda a resolver la tarea."
            if self.config["screen"].get("ocr_enabled", True):
                ocr_parts = [screen_context.ocr_image(image) for image in images]
                ocr = "\n".join(part for part in ocr_parts if part)
                if ocr:
                    visual += f"\nOCR detectado en pantalla:\n{ocr}"

        return f"""{system_prompt()}

Historial reciente:
{previous or "Sin historial previo."}

Memoria persistente:
{memory or "Sin memoria persistente guardada todavia."}

Peticion actual del usuario:
{user_text}
{visual}
"""

    def _marker_mode(self, answer: str) -> str:
        start = answer.find(SCREENSHOT_MARKER) + len(SCREENSHOT_MARKER)
        end = answer.find("]]", start)
        if end == -1:
            return "fullscreen"
        mode = answer[start:end].strip().lower()
        return "region" if mode == "region" else "fullscreen"
