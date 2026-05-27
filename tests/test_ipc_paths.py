import unittest

from voice_codex import paths


class PathTests(unittest.TestCase):
    def test_socket_name(self):
        self.assertEqual(paths.socket_file().name, "voice-codex.sock")

    def test_window_title(self):
        self.assertEqual(paths.WINDOW_TITLE, "Voice Codex")


if __name__ == "__main__":
    unittest.main()
