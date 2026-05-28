from __future__ import annotations

import atexit
import os
import threading

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

from . import paths
from .audit import AuditLog
from .codex_client import CodexClient
from .config import load_config
from .handy_bridge import ensure_handy_settings, latest_history_id, latest_transcription_after
from .ipc import IPCServer
from .stt import transcribe_recording
from .tts import Speaker


class VoiceCodexApp(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.juanma.VoiceCodex")
        self.config = load_config()
        self.audit = AuditLog(enabled=bool(self.config["audit"].get("enabled", True)))
        self.codex = CodexClient(self.config, self.audit)
        self.speaker = Speaker(self.config["tts"])
        self.ipc = IPCServer(self.on_ipc_action)
        self.window: Gtk.ApplicationWindow | None = None
        self.input_view: Gtk.TextView | None = None
        self.output_view: Gtk.TextView | None = None
        self.status_label: Gtk.Label | None = None
        self.pending_input = ""
        self.output_history: list[str] = []
        self.handy_start_history_id = 0
        self.handy_poll_attempts = 0

    def do_activate(self) -> None:
        self.hold()
        self.ipc.start()
        handy_msg = ensure_handy_settings(self.config["handy"])
        if handy_msg:
            self.audit.write("handy", handy_msg)
        if self.should_show_window_on_start():
            if not self.window:
                self.build_window()
            self.window.present()

    def build_window(self) -> None:
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title(self.config["ui"].get("window_title", paths.WINDOW_TITLE))
        self.window.set_default_size(780, 540)
        self.window.connect("close-request", self.on_close_request)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(12)
        root.set_margin_bottom(12)
        root.set_margin_start(12)
        root.set_margin_end(12)

        self.status_label = Gtk.Label(label="Idle")
        self.status_label.set_xalign(0)
        root.append(self.status_label)

        self.input_view = Gtk.TextView()
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_view.set_vexpand(False)
        input_scroll = Gtk.ScrolledWindow()
        input_scroll.set_min_content_height(120)
        input_scroll.set_child(self.input_view)
        root.append(input_scroll)

        self.output_view = Gtk.TextView()
        self.output_view.set_editable(False)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        output_scroll = Gtk.ScrolledWindow()
        output_scroll.set_vexpand(True)
        output_scroll.set_child(self.output_view)
        root.append(output_scroll)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        send_button = Gtk.Button(label="Enviar a Codex")
        send_button.connect("clicked", lambda _button: self.process_current_input())
        clear_button = Gtk.Button(label="Limpiar")
        clear_button.connect("clicked", lambda _button: self.clear_input())
        button_box.append(send_button)
        button_box.append(clear_button)
        root.append(button_box)

        self.window.set_child(root)
        self.set_status("Listo. Pulsa Alt+Z para hablar.")
        self.input_view.grab_focus()

    def on_close_request(self, _window: Gtk.ApplicationWindow) -> bool:
        if self.window:
            self.window.set_visible(False)
        return True

    def on_ipc_action(self, action: str) -> None:
        GLib.idle_add(self.handle_action, action)

    def handle_action(self, action: str) -> bool:
        if action == "ping":
            return False
        if action == "start":
            self.handy_start_history_id = latest_history_id()
            self.handy_poll_attempts = 0
            self.clear_input()
            self.set_status("Escuchando...")
            if self.config["ui"].get("auto_focus_on_record", False):
                self.present_and_focus()
            return False
        if action == "stop":
            self.set_status("Transcribiendo...")
            settle = int(self.config["handy"].get("transcription_settle_ms", 1800))
            GLib.timeout_add(settle, self.process_after_handy)
            return False
        return False

    def present_and_focus(self) -> None:
        if self.window:
            self.window.present()
        if self.input_view:
            self.input_view.grab_focus()

    def should_show_window_on_start(self) -> bool:
        if os.environ.get("VOICE_CODEX_START_HIDDEN") == "1":
            return False
        return bool(self.config["ui"].get("show_window_on_start", True))

    def clear_input(self) -> None:
        self.pending_input = ""
        if self.input_view:
            self.input_view.get_buffer().set_text("")

    def set_input_text(self, text: str) -> None:
        self.pending_input = text
        if self.input_view:
            self.input_view.get_buffer().set_text(text)

    def process_current_input(self) -> bool:
        text = self.get_input_text().strip()
        if not text:
            self.set_status("Sin texto transcrito.")
            return False
        self.append_output(f"\nUsuario: {text}\n")
        self.set_status("Codex pensando/actuando...")
        threading.Thread(target=self.ask_codex_worker, args=(text,), daemon=True).start()
        return False

    def process_after_handy(self) -> bool:
        text = self.get_input_text().strip()
        if text:
            return self.process_current_input()

        found = latest_transcription_after(self.handy_start_history_id)
        if found and found[1]:
            _history_id, transcript = found
            self.set_input_text(transcript)
            self.append_output(f"\nHandy: {transcript}\n")
            return self.process_current_input()

        if self.config.get("stt", {}).get("engine") == "whisper_cpp":
            transcript = transcribe_recording(self.config, paths.recording_file())
            if transcript:
                self.set_input_text(transcript)
                self.append_output(f"\nSTT: {transcript}\n")
                return self.process_current_input()
            self.set_status("No he detectado voz clara en la grabacion.")
            return False

        self.handy_poll_attempts += 1
        if self.handy_poll_attempts < 24:
            self.set_status("Esperando transcripcion de voz...")
            GLib.timeout_add(500, self.process_after_handy)
            return False

        self.set_status("Sin transcripcion. Revisa microfono o habla mas cerca.")
        return False

    def ask_codex_worker(self, text: str) -> None:
        answer = self.codex.ask(text)
        GLib.idle_add(self.finish_answer, answer)

    def finish_answer(self, answer: str) -> bool:
        self.append_output(f"\nCodex: {answer}\n")
        warning = self.speaker.speak(answer)
        if warning:
            self.append_output(f"\nTTS: {warning}\n")
        self.set_status("Listo.")
        return False

    def get_input_text(self) -> str:
        if not self.input_view:
            return self.pending_input
        buffer = self.input_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        return buffer.get_text(start, end, True)

    def append_output(self, text: str) -> None:
        self.output_history.append(text)
        self.output_history = self.output_history[-80:]
        if not self.output_view:
            return
        buffer = self.output_view.get_buffer()
        end = buffer.get_end_iter()
        buffer.insert(end, text)

    def set_status(self, text: str) -> None:
        if self.status_label:
            self.status_label.set_text(text)
        self.audit.write("status", text)


def main() -> int:
    paths.config_dir().mkdir(parents=True, exist_ok=True)
    paths.state_dir().mkdir(parents=True, exist_ok=True)
    atexit.register(lambda: paths.socket_file().unlink(missing_ok=True))
    app = VoiceCodexApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
