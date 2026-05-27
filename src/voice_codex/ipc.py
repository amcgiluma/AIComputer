from __future__ import annotations

import json
import socket
import threading
from collections.abc import Callable

from . import paths


Handler = Callable[[str], None]


class IPCServer:
    def __init__(self, handler: Handler) -> None:
        self.handler = handler
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()

    def start(self) -> None:
        paths.runtime_dir().mkdir(parents=True, exist_ok=True)
        paths.socket_file().unlink(missing_ok=True)
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self) -> None:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(paths.socket_file()))
            server.listen(4)
            while not self.stop_event.is_set():
                try:
                    conn, _ = server.accept()
                except OSError:
                    continue
                with conn:
                    payload = conn.recv(4096).decode("utf-8").strip()
                    if not payload:
                        continue
                    try:
                        data = json.loads(payload)
                        action = data.get("action", "")
                    except json.JSONDecodeError:
                        action = payload
                    self.handler(action)


def send(action: str) -> bool:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(paths.socket_file()))
            client.sendall(json.dumps({"action": action}).encode("utf-8"))
        return True
    except OSError:
        return False
